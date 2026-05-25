from django.apps import AppConfig
from .utils.consul_client import consul_client
import atexit
import os


class SeckillConfig(AppConfig):
    name = 'management'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return
        consul_client.deregister_all()
        consul_client.register_service()
        atexit.register(consul_client.deregister)