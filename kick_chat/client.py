import json
import os
import sys
from datetime import datetime
from typing import Any

import websocket
from curl_cffi import requests

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from kick_chat.constants import RESET, SOCKET_URL
from kick_chat.utils import hex_to_rgb


class Client:
    def __init__(self, *, username: str):
        self.chatroom_id = self.username_to_id(username)

    def username_to_id(self, username: str) -> int:
        res = requests.get(
            f"https://kick.com/api/v1/channels/{username}",
            impersonate="chrome110",
        )
        res.raise_for_status()
        data = res.json()
        return int(data["chatroom"]["id"])

    def subscribe(self, ws: websocket.WebSocketApp) -> None:
        ws.send(
            json.dumps(
                {
                    "event": "pusher:subscribe",
                    "data": {
                        "channel": f"chatrooms.{self.chatroom_id}.v2",
                        "auth": "",
                    },
                }
            )
        )

    def messageEvent(self, _ws: websocket.WebSocketApp, data: dict[str, Any]) -> None:
        time = datetime.fromisoformat(data["created_at"]).astimezone(tz=None).strftime("%H:%M:%S")
        message = data["content"]
        user = data["sender"]["username"]
        r, g, b = hex_to_rgb(data["sender"]["identity"]["color"])
        fgColorString = f"\033[38;2;{r};{g};{b}m"
        print(f"[{time}] {fgColorString}{user}{RESET}: {message}")

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        res = json.loads(message)
        match res["event"]:
            case "pusher:connection_established":
                self.subscribe(ws)
            case "pusher_internal:subscription_succeeded":
                print("Subscribed ...")
            case "App\\Events\\ChatMessageEvent":
                data = json.loads(res["data"])
                self.messageEvent(ws, data)

    def on_open(self, _ws: websocket.WebSocketApp) -> None:
        print("Connected ...")

    def listen(self) -> None:
        ws = websocket.WebSocketApp(
            SOCKET_URL,
            on_open=self.on_open,
            on_message=self.on_message,
        )
        ws.run_forever(reconnect=5)
