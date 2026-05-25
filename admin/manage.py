#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(...) from exc
    
    args = sys.argv
    if len(args) > 1 and args[1] == 'runserver' and len(args) == 2:
        from management.utils.consul_client import consul_client
        args = ['manage.py', 'runserver', f'0.0.0.0:{consul_client.port}']
    
    execute_from_command_line(args)


if __name__ == '__main__':
    main()
