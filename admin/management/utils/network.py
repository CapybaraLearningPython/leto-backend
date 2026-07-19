import socket

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]
    
def get_local_address():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        return "127.0.0.1"

def get_free_address():
    return get_local_address(), get_free_port()
