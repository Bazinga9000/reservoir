import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import F
from django.core.serializers.json import DjangoJSONEncoder

from .models import Puzzle, ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.puzzle_id = int(self.scope["url_route"]["kwargs"]["puzzle_id"])
        self.puzzle = await Puzzle.objects.filter(id=self.puzzle_id).afirst()

        # reject connection if not authenticated or puzzle is invalid
        if not self.user.is_authenticated or self.puzzle is None:
            self.close()
            return
        
        self.username = await self._get_username()
        self.room_group_name = f"chat_puzz_{self.puzzle_id}"

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # if we are rejecting the connection, room_group_name was not set,
        # so return early
        if not hasattr(self, 'room_group_name'):
            return
        
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
    
    @database_sync_to_async
    def _get_username(self):
        return self.user.discorduser.cached_username

    # Receive a message from the socket
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            assert isinstance(data, dict)
        except json.JSONDecodeError | UnicodeDecodeError | AssertionError:
            # ignore invalid message
            # TODO: check if this is an acceptable handling strategy
            return
        
        msg_type = data.get('type')

        print(data)

        if msg_type == 'get_history':
            after_id = data.get('after', 0)
            if isinstance(after_id, int):
                qset = ChatMessage.objects.filter(
                    puzzle__id=self.puzzle_id,id__gt=after_id
                ).values(
                    'id',
                    'sent_date',
                    'content',
                    username=F('user__discorduser__cached_username')
                )
                messages = [msg async for msg in qset]
                print(messages)
                await self.send(text_data=json.dumps(
                    {'type': 'history', 'messages': messages},
                    cls=DjangoJSONEncoder
                ))


        elif msg_type == 'message':
            chat_msg_content = data.get('content')

            # ignore blank chat messages, if they somehow get sent
            if not chat_msg_content:
                return
            
            msg_obj = await ChatMessage.objects.acreate(
                puzzle=self.puzzle,
                user=self.user,
                content=chat_msg_content
            )

            message = {
                'id': msg_obj.id,
                'username': self.username,
                'sent_date': msg_obj.sent_date,
                'content': chat_msg_content
            }
            message_json = json.dumps(
                {'type': 'message', 'message': message},
                cls=DjangoJSONEncoder
            )

            # Send message to everyone in room group
            await self.channel_layer.group_send(
                self.room_group_name, {'type': 'chat.message', 'json': message_json}
            )

    # Receive a chat.message message from room group
    async def chat_message(self, event):
        message_json = event['json']
        # Send to socket
        await self.send(text_data=message_json)
