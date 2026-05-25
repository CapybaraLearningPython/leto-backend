def delivery_report(err, msg):
    if err is not None:
        print("Broker消息发送失败：", err)
