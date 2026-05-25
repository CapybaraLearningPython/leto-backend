from locust import HttpUser, task, between

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyMDU2MzA0NDMyNzk0MDQyMzY4LCJleHAiOjE3Nzk3NzY5NzUsInRva2VuX3R5cGUiOiJhY2Nlc3MifQ.eYI8crUv8Hq3p5mc1EpwRMb5PViizle53SBu2hUJXHI"


class SeckillUser(HttpUser):
    wait_time = between(0, 0)

    host = "http://127.0.0.1:8004"

    @task
    def seckill(self):

        headers = {"Authorization": f"Bearer {TOKEN}"}

        response = self.client.post(
            "/seckill/create_order",
            json={
                "quantity": 1,
                "seckill_id": 2056621208224399360,
                "address": "成都市锦江区",
            },
            headers=headers,
            name="seckill",
        )

        if response.status_code != 200:
            print(response.status_code, response.text)


# 秒杀系统并发正确性测试总结

# =========================
# 测试目标
# =========================
# 验证秒杀系统在高并发场景下是否存在：
# 1. 超卖问题
# 2. 重复下单问题
# 3. Redis 与数据库不一致导致的数据错误
# 4. 并发竞争导致的库存异常

# =========================
# 测试环境
# =========================
# 后端框架：FastAPI
# 鉴权方式：JWT
# 缓存组件：Redis
# 压测工具：Locust
# 测试接口：/seckill/create_order

# =========================
# 测试配置
# =========================
# Locust配置：
# - Users: 100
# - Spawn Rate: 100
# - 测试时长: 2~5秒瞬时并发

# 秒杀商品：
# - 初始库存: 1

# 测试方式：
# - 单用户高并发
# - 同一JWT Token模拟重复请求

# =========================
# 测试场景一：Redis命中（正常情况）
# =========================
# 测试逻辑：
# Redis已记录用户秒杀状态，后续请求被拦截

# 测试结果：
# - 首次请求：成功创建订单
# - 后续请求：全部被Redis拦截（重复下单）
# - 数据库订单数：1
# - 库存最终状态：0
# - 未出现负库存

# 结论：
# - Redis防重逻辑生效
# - 一人一单约束成立
# - 并发请求被有效削峰

# =========================
# 测试场景二：Redis未命中（异常/不一致情况）
# =========================
# 测试逻辑：
# Redis未拦截请求，进入数据库校验

# 测试结果：
# - 数据库成功拦截重复订单
# - 库存不足时请求被拒绝
# - 未出现重复订单
# - 未出现负库存
# - 库存最终为0

# 结论：
# - 数据库层具备兜底能力
# - 系统不依赖单一Redis校验
# - 数据一致性仍可保证

# =========================
# 最终验证结果
# =========================
# 订单维度：
# - 同一用户仅成功一单

# 库存维度：
# - 库存未出现负数
# - 扣减结果正确

# 并发维度：
# - 瞬时高并发下未出现明显竞态问题
# - Redis + DB双层校验有效

# =========================
# 总结
# =========================
# 当前系统已验证：
# - 一人一单机制有效
# - 未发生超卖
# - 并发情况下数据一致性基本正确
# - Redis作为前置拦截 + DB兜底结构成立
