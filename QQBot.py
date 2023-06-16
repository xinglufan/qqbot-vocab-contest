import asyncio
import json
import traceback

import websockets


class QQBot:
    def __init__(self, addr, callback):
        self.websocket = None
        self.callback = callback
        self.echoIndex = 0
        asyncio.get_event_loop().run_until_complete(self.response(addr))

    async def sendGroupMsg(self, group_id, message):
        data = {
            "action": "send_group_msg",
            "params": {
                "group_id": group_id,
                "message": message,
                "auto_escape": False,
            },
            "echo": str(self.echoIndex)
        }
        print("sendGroupMsg: " + message)
        await self.websocket.send(json.dumps(data))
        self.echoIndex += 1

    async def sendPrivateMsg(self, user_id, message):
        data = {
            "action": "send_private_msg",
            "params": {
                "user_id": user_id,
                "message": message,
                "auto_escape": False,
            },
            "echo": str(self.echoIndex)
        }
        print("sendPrivateMsg: " + message)
        await self.websocket.send(json.dumps(data))
        self.echoIndex += 1

    async def onReceive(self, msg):
        try:
            data = json.loads(msg)
            if "message_type" in data:
                if data["message_type"] == "group":
                    group_id = data["group_id"]
                    sender = data["sender"]
                    nickname = sender["nickname"]
                    user_id = sender["user_id"]
                    message = data["message"]
                    message_id = data["message_id"]
                    await self.callback(self, {
                        "group_id": group_id,
                        "user_id": user_id,
                        "nickname": nickname,
                        "message": message,
                        "message_id": message_id,
                    })
                elif data["message_type"] == 'private':
                    sender = data["sender"]
                    nickname = sender["nickname"]
                    user_id = sender["user_id"]
                    message = data["message"]
                    message_id = data["message_id"]
                    await self.callback(self, {
                        "group_id": -1,
                        "user_id": user_id,
                        "nickname": nickname,
                        "message": message,
                        "message_id": message_id,
                    })
        except Exception as e:
            print(e, "\n", traceback.format_exc())

    async def response(self, addr):
        print("open " + addr)
        while True:
            try:
                async with websockets.connect(addr) as websocket:
                    self.websocket = websocket
                    while True:
                        recv_msg = await websocket.recv()
                        await self.onReceive(recv_msg)
            except Exception as e:
                print(e)
                await asyncio.sleep(5)  # 等待 5 秒后再次尝试连接
                print("尝试重连")
