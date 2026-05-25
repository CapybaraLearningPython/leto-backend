from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    import traceback
    traceback.print_exc()
    print(f"DRF捕获到错误：{exc}")
    
    response = exception_handler(exc, context)
    return response