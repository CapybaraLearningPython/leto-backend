from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

def convert_to_dict(message: Message):
    response = MessageToDict(message, preserving_proto_field_name=True)
    
    return response