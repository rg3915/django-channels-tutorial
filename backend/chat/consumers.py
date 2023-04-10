import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Pega o nome da sala (pode ser um slug também)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Entra no channel com o nome/slug
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Aceita a connection
        await self.accept()

    async def disconnect(self, close_code):
        # Sai do group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Envia mensagem para o grupo
        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'chat_message', 'message': message}
        )

    # Recebe mensagens do channel
    async def chat_message(self, event):
        message = event['message']

        # Envia mensagem para o websocket
        await self.send(text_data=json.dumps({'message': message}))
