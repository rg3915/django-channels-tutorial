# channels

Sistema de chat feito com django-channels.

## Instalação

### Este projeto foi feito com:

* [Python 3.10.6](https://www.python.org/)
* [Django 4.2](https://www.djangoproject.com/)
* [Django channels](https://channels.readthedocs.io/en/stable/)

### Como rodar o projeto?

* Clone esse repositório.
* Crie um virtualenv com Python 3.
* Ative o virtualenv.
* Instale as dependências.
* Rode as migrações.

```
git clone https://github.com/rg3915/django-channels-tutorial.git
cd django-channels-tutorial

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python contrib/env_gen.py

python manage.py migrate
python manage.py createsuperuser --username="admin" --email=""
```

Rodando aplicação

```
uvicorn backend.asgi:application --reload
```

As salas são criadas dinamicamente na url.

Navegue em http://localhost:8000/chat/sala1


## Tutoriais

https://www.youtube.com/watch?v=cw8-KFVXpTE

https://www.youtube.com/watch?v=jsxFEONN_yo

https://www.youtube.com/watch?v=DqCqFRYO4W8

https://www.youtube.com/watch?v=SF1k_Twr9cg

https://stackoverflow.com/questions/73755881/djangorestframework-does-not-work-when-django-channel-is-applied


```python
# settings.py
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
```

Configurando [CHANNEL_LAYERS](https://channels.readthedocs.io/en/stable/topics/channel_layers.html)

```python
# asgi.py
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django

django.setup()
import chat.routing
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(chat.routing.websocket_urlpatterns))
        ),
    }
)
```

`chat/routing.py`

É o `url.py` do channels, vai dar match no endereço do websocket e fazer o dispatch para a classe.

```python
# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatRoomConsumer.as_asgi()),
]
```

`chat/consumers.py`

É o `views.py` do channels.

```python
# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        ...

    async def disconnect(self, close_code):
        ...

    async def receive(self, text_data):
        ...

    async def chat_message(self, event):
        ...
```

```html
<!-- templates/chatroom.html -->
<!-- Pega as mensagens do websocket -->
{{ request.user.username|json_script:"user_username" }} {{
room_name|json_script:"room-name" }}
<script>
  const user_username = JSON.parse(
    document.getElementById("user_username").textContent
  );
  document.querySelector("#submit").onclick = function (e) {
    const messageInputDom = document.querySelector("#input");
    const message = messageInputDom.value;
    chatSocket.send(
      JSON.stringify({
        message: message,
        username: user_username,
      })
    );
    messageInputDom.value = "";
  };

  const roomName = JSON.parse(document.getElementById("room-name").textContent);

  // Cria conexão com o websocket (gerando o link pela url)
  const chatSocket = new WebSocket(
    "ws://" + window.location.host + "/ws/chat/" + roomName + "/"
  );

  // Envia mensagem para o socket
  chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data);
    document.querySelector("#chat-text").value +=
      data.username + ": " + data.message + "\n";
  };
</script>
```
