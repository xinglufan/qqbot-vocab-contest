from QQBot import QQBot
from config import host
from VocabGroup import VocabGroup

Groups = [
    VocabGroup(),
]


async def qq_msg_received(bot, data):
    print(data)
    for group in Groups:
        ret = await group(bot, data)
        if ret:
            break


if __name__ == '__main__':
    QQBot(host, qq_msg_received)
