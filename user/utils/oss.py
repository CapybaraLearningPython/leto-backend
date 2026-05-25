import alibabacloud_oss_v2 as oss
import alibabacloud_oss_v2.aio as oss_aio
from utils.single import SingletonMeta
from grpc import StatusCode
from grpc_interceptor.exceptions import GrpcException
import os.path
import uuid
from datetime import timedelta


class OSS(metaclass=SingletonMeta):
    def __init__(self):
        credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()

        cfg = oss.config.load_default()
        cfg.credentials_provider = credentials_provider

        cfg.region = "cn-hangzhou"

        self.client = oss_aio.AsyncClient(cfg)
        self.sync_client = oss.Client(cfg)
        self.bucket = "tll0211"
        self.region = cfg.region

    async def _delete_file(self, key: str):
        try:
            result = await self.client.delete_object(
                oss.DeleteObjectRequest(
                    bucket=self.bucket,
                    key=key,
                )
            )

            print(
                f"status code: {result.status_code}\n"
                f"request id: {result.request_id}\n"
                f"etag: {result.etag}"
            )

        except Exception as e:
            raise GrpcException(
                status_code=StatusCode.INTERNAL, details=f"OSS删除失败：{e}"
            )

    async def generate_presigned_url(
        self, file_name: str, content_type: str, exp: int = 3600
    ):
        extension = os.path.splitext(file_name)[1].lower()
        if extension not in [".jpg", ".jpeg", ".png"]:
            raise GrpcException(
                status_code=StatusCode.INVALID_ARGUMENT,
                details="仅支持 .jpg .jpeg .png 三种格式！",
            )
        key = f"leto_avatar/{uuid.uuid4().hex}{extension}"
        pre_result = self.sync_client.presign(
            oss.PutObjectRequest(
                bucket=self.bucket,
                key=key,
                content_type=content_type
            ),
            expires=timedelta(seconds=exp),
        )
        file_url = f"https://{self.bucket}.oss-{self.region}.aliyuncs.com/{key}"

        print(
            f"method: {pre_result.method},"
            f'expiration: {pre_result.expiration.strftime("%Y-%m-%dT%H:%M:%S.000Z")},'
            f"url: {pre_result.url}"
        )

        for header_key, value in pre_result.signed_headers.items():
            print(f"signed headers key: {header_key}, signed headers value: {value}")

        return pre_result.url, pre_result.signed_headers ,file_url

    async def delete_image(self, key):
        await self._delete_file(key)
        return key

    async def close(self):
        await self.client.close()

oss_client = OSS()