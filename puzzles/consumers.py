import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.puzzle_id = self.scope["url_route"]["kwargs"]["puzzle_id"]
        self.room_group_name = f"chat_puzz_{self.puzzle_id}"

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive a message from the socket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to everyone in room group
        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'chat.message', 'message': message}
        )

    # Receive a chat.message message from room group
    async def chat_message(self, event):
        message = event['message']
        # Send to socket
        await self.send(text_data=json.dumps({'message': message}))
