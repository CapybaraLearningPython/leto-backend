# 乐淘商城 LetoMall

一个基于微服务架构的秒杀电商系统，核心解决高并发场景下的超卖、缓存击穿等问题，并实现了服务发现与负载均衡以及秒杀链路的削峰填谷。
**Locust压测报告请见文档末尾**

## 技术栈

| 类别 | 技术选型 |
|---|---|
| 前端 | Vue3 (JS) |
| 统一网关 | FastAPI |
| 微服务 | gRPC (Python) 授权服务 / 用户服务 / 秒杀服务 |
| 服务发现 | Consul + 自定义轮询负载均衡 |
| 管理后台 | Django + DRF (和微服务共用网关) |
| 数据库 | MySQL 8.0（库存带乐观锁 version_id）|
| 缓存 | Redis 7（Lua脚本防超卖，互斥锁防护缓存击穿） |
| 消息队列 | Kafka（KRaft模式） |
| 对象存储 | 阿里云OSS（预签名直传） |
| 支付 | 支付宝网页支付 |
| 容器化 | Docker |

## 架构总览

系统由网关统一收口所有请求，网关通过Consul做服务发现，拿到健康实例列表后自己做轮询转发。JWT校验放在网关层做，通过之后请求才会被转发到具体的微服务，微服务以及管理后台本身不用重复做鉴权，只有网关可被外部访问。

```
客户端 → 网关（JWT校验 + Consul服务发现 + 负载均衡）→ 具体微服务/管理后台 → Redis / Kafka / MySQL
```

## 授权模块

验证码请求的链路是请求由网关转发到授权中心，授权中心调用阿里云短信服务，发送验证码和校验验证码均由阿里云短信服务完成，本地不参与校验。

登录/注册合并成一个入口处理，逻辑是先验证码校验，再查手机号。如果手机号已经存在就走登录逻辑，不存在就顺手完成注册，两条路径最后都会在Redis里写入Refresh Token，然后把授权信息返回给客户端。

采用双Token设计。Access Token刷新走单独接口，即Redis里比对Refresh Token是否有效，有效就签发新的Access Token返回，不涉及数据库查询，保证刷新接口速度。

管理后台的强制登出功能，本质就是直接从Redis里删掉对应用户的Refresh Token，下次这个用户拿旧Token刷新的时候会直接失败，不需要额外维护一张黑名单表。

## 用户模块

地址管理是普通的CRUD，走JWT鉴权之后直接操作数据库，没有太多特殊设计。

头像上传用的是OSS预签名的方式，避免让文件流经过自己的服务器。网关校验完JWT之后，头像服务向OSS申请一个带签名的上传地址和对应请求头，把这个地址返回给客户端，客户端拿着这个地址直接把文件传到OSS，不经过后端中转。上传完成之后再把最终的头像地址写回数据库。这样设计的好处是服务器不用处理文件的上传流量，也不用自己维护存储。

## 秒杀模块

秒杀列表和详情页数据在创建商品时存入Redis，降低数据库压力。

为了防止超卖并减少数据库压力，本项目采用了三层防护：

**第一层，Redis + Lua脚本 + 缓存击穿防护**：购买请求先到这一层做限购校验和库存校验。考虑到生产环境中可能会因为各种原因导致缓存缺失而无法读取秒杀商品的信息进行后续订单操作，Redis层在查询不到相关信息时会触发互斥锁相关逻辑，此时只会有一个请求能够成功拿到锁并读取数据库重建缓存，从而避免因为缓存失效而导致的无法下单，也避免了大量请求直接打到数据库。

库存扣减在Lua脚本里完成，以保证查库存和扣库存这两个动作是原子的。如果分成两条Redis命令，中间可能被别的并发请求insert进来，导致库存被超卖。Lua脚本在Redis里是单线程执行的，天然规避了这个竞态条件。

**第二层，Kafka异步削峰**：Redis这一层校验通过之后，请求不会直接打到数据库，而是先扔进Kafka的消息队列，由消费者异步处理后续的数据库操作。这样即便秒杀瞬间涌进来几千个请求，得益于消息队列极高的吞吐量，消费者只需按照自己的节奏处理消息即可，不会被瞬时并发直接打满连接池。

**第三层，数据库乐观锁兜底**：消费者从Kafka里取到请求之后，数据库层面会再做一次限购和库存校验，然后带着`version_id`字段去更新库存，如果更新时发现版本号已经被别的事务改过，说明发生了并发冲突，这次扣减失败，不会出现两个请求同时读到"库存还有1件"然后都扣减成功的情况。

在这样的秒杀链路中，Redis层挡住绝大部分无效请求（限购超限、库存已空的直接在这一层被拒绝），Kafka层把真正有效的请求削峰打散，数据库层用乐观锁做最后一道保险。压测阶段用Locust模拟了100件库存、1000并发用户抢购，验证下来库存扣减没有出现负数或者超发的情况。在同样的测试条件下模拟缓存失效的场景（删除Redis对应商品的Key），结果表明最终只有一个请求拿到互斥锁并成功重建缓存，证明缓存击穿防护有效。

订单生成之后，消费者会把订单号写回Redis，方便前端轮询查询支付状态。

支付这一步接的是支付宝的网页支付接口，客户端定时轮询Redis里的订单状态，用户在支付宝完成支付之后，支付宝会回调后端接口，后端收到回调再去修改数据库里的订单状态。

## 管理后台

用Django + DRF单独搭了一套后台管理系统，商品管理和秒杀活动管理都是走管理后台直接操作数据库，跟C端用户请求是两套服务，互不干扰。

## 部署

项目部署在阿里云ECS（4核8G，Ubuntu 22.04），基础设施（MySQL、Redis、Kafka、Consul）用Docker Compose统一起，Python服务本身用nohup常驻后台运行，前端打包之后由Nginx负责托管静态资源并反向代理API请求到网关。由于条件限制，本次仅使用单机进行了部署，性能受限较大，因此本分布式项目测试多集中于正确性测试。

## 目录结构

```
leto-backend/
├── admin/          # Django管理后台
├── gateway/        # FastAPI网关，服务发现+负载均衡+JWT校验
├── auth/           # 授权中心（gRPC）
├── user/           # 用户服务（gRPC）
├── seckill/        # 秒杀服务（gRPC）+ Kafka消费者
├── venv/
└── docker-compose.yml
```

## 快速开始

```bash
git clone git@github.com:CapybaraLearningPython/leto-backend.git
cd leto-backend

# 启动基础设施
docker compose up -d

# 激活虚拟环境
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 分别启动各个服务
cd auth && python main.py &
cd ../user && python main.py &
cd ../seckill && python main.py &
cd ../seckill && python -m services.consumer &
cd ../admin && python manage.py runserver &
cd ../gateway && python main.py &
```
## 附录：Locust压测报告
**测试日期**：2026-07-17<br>
**测试目标**：验证秒杀下单链路在高并发场景下的库存一致性（是否超卖）与限购逻辑正确性

### 一、测试背景

LetoMall 秒杀模块采用「Redis Lua 原子扣减 → Kafka 异步下单 → 数据库乐观锁（`version_id`）」三层机制防止超卖。在部署上线前，需要通过并发压测验证该机制在真实高并发场景下是否可靠。

#### 系统架构（压测涉及部分）

- 网关层：FastAPI，路由 `POST /seckill/create_order`，JWT 鉴权（`auth_dependency`）解析出 `user_id` 后通过 gRPC metadata（key: `user-id`）透传给下游
- 服务层：gRPC Seckill 服务，`SeckillInterceptor` 拦截器从 metadata 解析 `user_id`（不查库，纯透传）
- 数据层：库存预扣在 Redis（Lua 原子操作），订单创建经 Kafka 异步消费写入 MySQL，乐观锁字段为 `version_id`

### 二、测试环境

| 项目 | 配置 |
|---|---|
| 服务端 | 阿里云 ECS 4核8GB，Ubuntu 22.04，成都地域，公网 IP `47.109.186.250` |
| 压测客户端 | 本地 Mac，Locust |
| 目标秒杀活动 | `seckill_id = 2077648144430006272` |
| 初始库存 | 100 |
| 限购数量 | 每用户 1 件（`max_per_buyer = 1`） |
| 并发用户数 | 1000（对应 1000 个不同 `user_id`，取值区间 90000–90999） |
| Spawn rate | 100 用户/秒 |

### 三、鉴权方案

由于秒杀下单接口需要合法 JWT 才能通过网关鉴权，且拦截器和业务逻辑均不校验用户在数据库中是否真实存在（`order` 与 `user` 表无外键约束），因此采用**离线批量生成合法 JWT** 的方式模拟 1000 个不同用户，无需真实注册用户或走短信登录流程。

#### Token 生成脚本

```python
import jwt
from datetime import datetime, timedelta
import json

SECRET_KEY = "<与服务端 self.secret_key 保持一致>"
ACCESS_TOKEN_EXPIRES = timedelta(hours=6)

def generate_access_token(user_id: int) -> str:
    payload = dict(user_id=user_id)
    payload["exp"] = int((datetime.now() + ACCESS_TOKEN_EXPIRES).timestamp())
    payload["token_type"] = "access"
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# 生成 1000 个 token，user_id 取值 90000~90999，避免与真实用户冲突
tokens = {uid: generate_access_token(uid) for uid in range(90000, 91000)}

with open("test_tokens.json", "w") as f:
    json.dump(tokens, f)

print(f"生成了 {len(tokens)} 个token")
```

#### 链路验证（压测前手动 curl）

```bash
curl -X POST http://47.109.186.250/seckill/create_order \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"seckill_id": 2077648144430006272, "quantity": 1, "address": "四川省成都市测试地址123号"}'

# 返回：{"status":"订单请求已提交！"}
```

确认鉴权、gRPC metadata 透传、拦截器解析、业务逻辑全链路打通后正式压测。

### 四、压测脚本（Locust）

```python
from locust import HttpUser, task, between, events
import json
import itertools
from collections import Counter

with open("test_tokens.json") as f:
    tokens = json.load(f)

token_cycle = itertools.cycle(tokens.values())
result_counter = Counter()

class SeckillUser(HttpUser):
    host = "http://47.109.186.250"
    wait_time = between(0, 0.1)

    def on_start(self):
        self.token = next(token_cycle)

    @task
    def seckill_order(self):
        with self.client.post(
            "/seckill/create_order",
            json={
                "seckill_id": 2077648144430006272,
                "quantity": 1,
                "address": "四川省成都市测试地址123号"
            },
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result_counter["success"] += 1
                response.success()
            else:
                try:
                    detail = response.json().get("detail") or response.text
                except Exception:
                    detail = response.text
                result_counter[f"failed: {detail}"] += 1
                response.success()  # 业务拒绝不计入 Locust 系统失败率

@events.quitting.add_listener
def on_quit(environment, **kwargs):
    print("\n===== 请求结果分布 =====")
    for reason, count in result_counter.most_common():
        print(f"{reason}: {count}")
    print(f"总计: {sum(result_counter.values())}")
    print("========================\n")
```

#### 启动命令 / 参数

- Number of users: `1000`
- Spawn rate: `100`
- Host: `http://47.109.186.250`

### 五、测试前置：数据重置

```sql
-- 清空上一轮测试数据
DELETE FROM `order` WHERE seckill_id = '2077648144430006272';

-- 重置库存
UPDATE seckill表 SET stock = 100 WHERE id = '2077648144430006272';
```

```bash
# 清理 Redis 中该秒杀活动相关的库存/幂等锁 key
redis-cli --scan --pattern "*2077648144430006272*" | xargs redis-cli DEL
```

### 六、压测结果

#### 6.1 请求结果分布（Locust 终端输出）

| 结果 | 次数 |
|---|---|
| success（下单成功） | 100 |
| failed: 预扣库存失败：购买数量超过库存 | 28803 |
| failed: 预扣库存失败：重复下单 | 4387 |
| failed: （超时/连接异常等） | 2385 |
| failed: 500 Internal Server Error（nginx） | 2 |
| **总计** | **35677** |

> 偶发 500 错误（2 次）占比极低，暂不阻塞上线，但建议后续通过日志定位具体触发条件

#### 6.2 性能数据（Locust 汇总）

| 指标 | 数值 |
|---|---|
| 总请求数 | 35677 |
| 系统级失败率（HTTP 层） | 0.00% |
| 峰值 QPS | 约 594 req/s |
| 响应时间中位数（Med） | 1300 ms |
| 响应时间 P95 | 3600 ms |
| 响应时间 P99 | 5600 ms |
| 最大响应时间（100%） | 39594 ms |

> 说明：存在长尾响应（P99.9 达 24s~39s），推测与瞬时高并发下 Redis/gRPC 连接排队有关，建议作为后续性能优化项跟进，但不影响本次库存一致性结论。
> 
> 考虑到是单机部署模拟分布式，Kafka、Consul等基础设施反而会明显拖累性能，所以性能表现不如预期

#### 6.3 数据库验证

**库存扣减验证**

```sql
SELECT stock FROM seckill表 WHERE id = '2077648144430006272';
-- 结果：0（100 → 0，精确扣减，无负库存）
```

**订单总数验证**

```sql
SELECT COUNT(*) FROM `order` WHERE seckill_id = '2077648144430006272';
-- 结果：101
```

初步核查发现 101 条中包含 1 条压测前遗留的历史订单（非本轮压测产生），排查如下：

```sql
SELECT id, user_id, created_at, status
FROM `order`
WHERE seckill_id = '2077648144430006272'
ORDER BY created_at ASC
LIMIT 3;
```

| id | user_id | created_at | status |
|---|---|---|---|
| 2077693093628346368 | 2077628510771347456 | 2026-07-16 17:53:30 | 2 |
| 2077951799460888576 | 90001 | 2026-07-17 11:01:30 | 1 |
| 2077951799532191744 | 90000 | 2026-07-17 11:01:30 | 1 |

第一条订单 `user_id`（2077628510771347456）不在本轮压测使用的测试 `user_id` 区间（90000–90999）内，且 `created_at` 早于本轮压测启动时间约 18 小时，`status` 也与压测产生的订单（`status=1`）不同，确认为压测前遗留的历史数据，与本轮压测无关。

**排除历史订单后，本轮压测实际产生订单数 = 101 - 1 = 100，与库存扣减数量精确一致。**

**限购逻辑验证（是否存在同一用户重复购买成功）**

```sql
SELECT user_id, COUNT(*) AS cnt
FROM `order`
WHERE seckill_id = '2077648144430006272'
GROUP BY user_id
HAVING cnt > 1;
-- 结果：Empty set（无重复购买记录）
```

### 七、结论

| 验证项 | 结果 |
|---|---|
| 库存是否精确扣减为 0（无负库存） | 通过 |
| 实际成交订单数是否等于初始库存（100） | 通过（排除历史脏数据后精确为 100） |
| 是否存在同一用户重复购买成功（限购失效） | 通过（无重复） |
| HTTP 层系统性错误率 | 0.00%（500 错误仅 2 次，占比 0.006%，可能为瞬时资源竞争） |

**在 100 库存 / 1000 并发用户 / 每用户限购 1 件的场景下，LetoMall 秒杀系统的 Redis Lua 原子扣减 + 数据库乐观锁（`version_id`）+ 限购校验三层防超卖机制均验证通过，未出现超卖、库存穿透或重复购买问题。**


## LetoMall 缓存击穿防护 — 设计与测试报告

**测试日期**：2026-07-18<br>
**测试目标**：为秒杀详情缓存、库存缓存加上缓存击穿防护，验证 Redis key 因误删/宕机重启/新数据写入时机不巧等原因意外丢失时，高并发请求下是否只触发一次真正的数据库查询和缓存重建，而不是所有并发请求同时打穿数据库

### 一、背景

LetoMall 秒杀下单接口 `CreateOrder`，在 Redis 中依赖两类缓存：

- **秒杀详情缓存**（`seckill_{id}`）：活动的价格、时间、库存等信息
- **库存缓存**（`seckill_stock_{id}`）：用于 Lua 原子扣减的实时库存数值

这两类缓存正常由 admin 服务在创建/上架活动时写入，但没有对"Redis 中途丢失这个 key"的场景做兜底。若某个热点活动的缓存意外失效（误删、Redis 重启后未恢复、新建活动时机恰好撞上故障等），所有并发请求会同时发现缓存缺失、同时打向数据库，造成缓存击穿，拖垮数据库。

采用的方案是经典的 **Cache-Aside + 互斥锁重建**：读取时发现缓存缺失，尝试抢一把 Redis 分布式锁；抢到锁的请求负责查库、重建缓存；未抢到锁的请求短暂等待后重试读取缓存。

### 二、方案设计

#### 2.1 为什么不用逻辑过期方案

逻辑过期（缓存永不真过期，允许短暂返回旧数据）适合能接受"稍微过时"的场景（如商品详情页）。但库存/限购数据要求强一致——旧数据可能导致超卖或绕过限购，因此选择互斥锁方案：宁可让请求短暂等待，也不允许返回过期的库存/限购状态。

#### 2.2 锁 vs Lua：两种机制的分工

项目中已有的库存扣减用 **Lua 脚本**做原子操作（检查限购+检查库存+扣减+防重复下单，一次性提交给 Redis 单线程执行，无需锁协调，性能更优）。

这次新增的缓存重建用**分布式锁**（`SET NX EX`），因为重建缓存是低频操作，锁带来的"抢锁-等待-释放"网络开销可以接受，而且重建逻辑本身（先查库、再多次写 Redis）无法整体塞进一条 Lua 脚本原子执行。

#### 2.3 与 Redis 整体宕机场景的边界

本次防护针对的场景是"某个 key 意外丢失，但 Redis 服务本身仍可用"。若 Redis 整体宕机，锁本身也无处存放，需要应用层熔断限流兜底——这部分评估后不在本次任务范围内，记录为后续可选项，不阻塞当前验收。

### 三、核心代码

#### 3.1 秒杀详情缓存重建（`get_seckill_detail`）

```python
async def get_seckill_detail(self, seckill_id: str):
    seckill_key = self.SECKILL_KEY.format(seckill_id)
    detail = await self.get_dict(seckill_key)
    if detail:
        return detail

    rebuild_key = self.DETAIL_REBUILD_KEY.format(seckill_id)
    max_retry = 30
    for _ in range(max_retry):
        # 每轮重试前先查一次缓存，命中就直接返回，避免不必要的抢锁
        detail = await self.get_dict(seckill_key)
        if detail:
            return detail

        got_lock = await self.client.set(rebuild_key, 1, nx=True, ex=5)
        if got_lock:
            try:
                # 双重检查：抢到锁后可能已被别的请求重建完毕
                detail = await self.get_dict(seckill_key)
                if detail:
                    return detail

                # 查库时使用独立的 session，不复用外部传入的长生命周期 session
                async with AsyncSessionFactory() as session:
                    async with session.begin():
                        seckill = await session.scalar(
                            select(Seckill).where(Seckill.id == seckill_id)
                        )
                        if not seckill:
                            return None

                        ex = int((seckill.ends_at - datetime.now()).total_seconds())
                        detail = {
                            "id": seckill.id,
                            "seckill_price": str(seckill.seckill_price),
                            "starts_at": seckill.starts_at.isoformat(),
                            "ends_at": seckill.ends_at.isoformat(),
                            "created_at": seckill.created_at.isoformat(),
                            "stock": seckill.stock,
                            "max_per_buyer": seckill.max_per_buyer,
                        }
                        if ex > 0:
                            await self.client.set(seckill_key, json.dumps(detail), ex=ex)

                return detail
            finally:
                await self.client.delete(rebuild_key)
        else:
            await asyncio.sleep(0.05)

    return None
```

#### 3.2 库存缓存重建（`_ensure_stock_key`）

```python
async def _ensure_stock_key(self, seckill: dict):
    ends_at = datetime.fromisoformat(seckill["ends_at"])
    now = datetime.now()
    if ends_at <= now:
        return  # 活动已结束，不重建

    stock_key = self.SECKILL_STOCK_KEY.format(seckill["id"])
    exists = await self.get_stock(seckill["id"])
    if exists:
        return

    rebuild_key = self.STOCK_REBUILD_KEY.format(seckill["id"])
    got_lock = await self.client.set(rebuild_key, 1, nx=True, ex=5)

    if got_lock:
        try:
            exists = await self.get_stock(seckill["id"])
            if exists:
                return
            ex = int((ends_at - now).total_seconds())
            await self.client.set(stock_key, seckill["stock"], ex=ex)
        finally:
            await self.client.delete(rebuild_key)
    else:
        await asyncio.sleep(0.05)
        await self._ensure_stock_key(seckill)
```

`_ensure_stock_key` 挂载在 `decrease_stock`（库存扣减入口）内部调用，`get_seckill_detail` 在 `CreateOrder` 接口最前面调用，两者共同保护下单链路。

### 四、测试方法

#### 4.1 测试工具

Locust，1000个并发虚拟用户（每用户对应一个独立的合法 JWT token），spawn rate 100（尽量让请求同时到达，制造真实的并发竞争窗口）。

#### 4.2 测试步骤

```bash
# 1. 制造缓存击穿场景：手动删除某活动的详情缓存与库存缓存
redis-cli DEL seckill_2077648889497780224
redis-cli DEL seckill_stock_2077648889497780224

# 2. 清空日志，保证统计的是本次测试的独立结果
> ~/logs/seckill.log

# 3. Locust 发起 1000 个并发下单请求
locust -f locustfile_cache_test.py
# Number of users: 1000, Spawn rate: 100

# 4. 统计各关键节点的触发次数
grep -a -c "detail缓存：抢锁成功" ~/logs/seckill.log
grep -a -c "detail缓存：重建成功" ~/logs/seckill.log
grep -a -c "stock缓存：抢锁成功" ~/logs/seckill.log
grep -a -c "stock缓存：重建成功" ~/logs/seckill.log
```

#### 4.3 判断标准

「抢锁成功」与「重建成功」次数应均为 **1**：说明无论多少并发请求同时发现缓存缺失，只有一个请求真正查库、写入缓存，其余请求通过等待/复用结果的方式正确处理，未发生重复查库或数据不一致。

### 五、测试结果

| 指标 | DETAIL 缓存 | STOCK 缓存 |
|---|---|---|
| 缓存未命中/尝试重建 | 13 | 22 |
| 抢锁成功 | **1** | **1** |
| 未抢到锁/等待重试 | 9 | 21 |
| 第二次检查缓存命中 | 0 | 0 |
| 重建成功 | **1** | **1** |
| DB 查无此活动 | 0 | — |
| 活动已结束不写入缓存 | 0 | — |
| 重试次数用完仍未成功 | 0 | — |

**结论：1000 个用户并发请求下，详情缓存与库存缓存均只触发一次真正的数据库查询和 Redis 重建，缓存击穿防护验证通过。**

> - **detail缓存尝试次数不等于未抢到锁的次数加上抢锁成功的次数的原因：** detail优化过逻辑，每次循环开头都会检查是否已经有缓存，如果有就会直接返回不会输出到日志；stock是通过递归进行循环，每次递归会完整走完流程，因此只要尝试重建则必会输出这次尝试的结果。
> - **stock的尝试次数更大的原因：** detail的重建逻辑是每个请求第一次缓存未命中才输出日志，后续重试不会反复输出；stock的逻辑是递归循环，每次递归都会输出尝试重建的日志，所以次数更多。

### 六、踩坑记录

排查过程中发现并修复了以下问题，均已在最终版本中解决：

| 问题 | 现象 | 原因 | 处理方式 |
|---|---|---|---|
| 新代码未接入业务流程 | 反复测试 print 从不触发 | `CreateOrder` 中仍调用旧的 `get_dict`，未切换到新写的 `get_seckill_detail` | 修改调用点，接入新方法 |
| Key 格式化参数不匹配 | `KeyError: 'seckill_id'` | 常量模板用命名占位符 `{seckill_id}`，调用时用位置参数 `.format(seckill_id)` | 统一为位置参数风格 |
| 漏 import | `NameError: name 'select' is not defined` | 复制代码时遗漏 `from sqlalchemy import select` | 补全 import |
| 缩进丢失 | 方法调用报错但报错信息具有误导性 | 复制粘贴时方法体缩进丢失，脱离了类定义，变成模块级游离函数 | 用 `python3 -m py_compile` 校验语法后再部署 |
| 漏写 return | 高并发下部分请求 log 全部为 0 | `if/else` 分支处理完写缓存逻辑后未 `return`，函数未正常退出，在循环中反复打转 | 补上统一的 `return detail` |
| session 并发复用 | `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called` | 复用了从 gRPC 拦截器传入的长生命周期 `session`，跨越多次 `await asyncio.sleep` 后再执行数据库操作，触发异步上下文错误 | 改为在需要查库时用 `AsyncSessionFactory()` 现开独立 session，用完自动关闭 |
| Protobuf 默认值省略 | 库存为 0 的活动在列表接口报 `Field required [type=missing]` | proto3 对数值类型字段，值等于默认值(0)时序列化时会被省略，Gateway 侧 Pydantic 模型严格校验该字段导致报错 | 涉及数值字段加 `optional` 关键字，重新生成 pb2 文件（seckill 与 gateway 两处均需生成，此前是两份独立的 pb2 副本导致遗漏同步） |
| Git 历史泄露密钥 | GitHub push protection 拦截 push | 阿里云 AccessKey 曾以明文提交进 git 历史 | 先在阿里云控制台作废旧 key，再用 `git filter-repo --replace-text` 清理全部历史 commit，强推覆盖远程 |

### 七、遗留事项

1. **Redis 整体宕机场景**：本次防护仅覆盖"单个 key 意外丢失、Redis 服务本身可用"的场景。若 Redis 整体不可用，锁机制本身失效，需要应用层限流/熔断兜底，评估后暂不在本次范围内实现
2. **DETAIL 缓存"抢锁成功"仍存在一定的空抢锁开销**：本次测试中每轮重试前已加入"先查缓存再抢锁"的优化，实际验证抢锁成功次数已精确收敛为 1，未观察到明显的重复抢锁问题
3. **proto 文件存在于两个服务目录下、各自维护一份编译产物**：属于历史遗留的项目结构问题，建议后续将 proto 定义统一到共享目录，避免再次出现"改一处忘了改另一处"导致的编译产物不同步
