import os
import sys
import json
from .single import SingletonMeta

from typing import List

from alibabacloud_dypnsapi20170525.client import Client as Dypnsapi20170525Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dypnsapi20170525 import models as dypnsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class SendCode(metaclass=SingletonMeta):
    def __init__(self):
        pass

    @staticmethod
    def _create_client() -> Dypnsapi20170525Client:
        config = open_api_models.Config(
            # access_key_id="",
            # access_key_secret="",
            endpoint="",
        )
        return Dypnsapi20170525Client(config)

    @staticmethod
    async def send_code(tel: str) -> None:
        client = SendCode._create_client()
        send_sms_verify_code_request = (
            dypnsapi_20170525_models.SendSmsVerifyCodeRequest(
                scheme_name="测试方案",
                country_code="86",
                phone_number=tel,
                sign_name="速通互联验证码",
                template_code="100001",
                template_param='{"code":"##code##","min":"5"}',
            )
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = await client.send_sms_verify_code_with_options_async(
                send_sms_verify_code_request, runtime
            )
            print(json.dumps(resp, default=str, indent=2))
        except Exception as error:
            print(error.message)


class VerifyCode(metaclass=SingletonMeta):
    def __init__(self):
        pass

    @staticmethod
    def _create_client() -> Dypnsapi20170525Client:
        config = open_api_models.Config(
            # access_key_id=" ",
            # access_key_secret="",
            endpoint="",
        )
        return Dypnsapi20170525Client(config)

    @staticmethod
    async def verify_code(tel, code) -> None:
        client = VerifyCode._create_client()
        check_sms_verify_code_request = (
            dypnsapi_20170525_models.CheckSmsVerifyCodeRequest(
                scheme_name="测试方案", phone_number=tel, verify_code=code
            )
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = await client.check_sms_verify_code_with_options_async(
                check_sms_verify_code_request, runtime
            )
            print(json.dumps(resp, default=str, indent=2))
            return resp
        except Exception as error:
            raise

sending_client = SendCode()
verification_client = VerifyCode()
