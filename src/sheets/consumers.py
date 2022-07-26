from channels.generic.websocket import WebsocketConsumer


class OrderConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
