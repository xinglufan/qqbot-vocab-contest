import asyncio
import pickle
import random
import threading
from asyncio import sleep
from pathlib import Path

from Regexp import Regexp
from config import ROOT, GROUPS_ID


def is_file_exists(filePath):
    return Path(filePath).exists()


def write_pickle(file, data):
    data = pickle.dumps(data)
    with open(file, "wb") as f:
        f.write(data)


def load_pickle(file):
    if is_file_exists(file):
        with open(file, "rb") as f:
            return pickle.loads(f.read())
    return None


contest_map = load_pickle(ROOT + "/assets/contest_map.pickle")

addition_map = {'cet4': 8,
                'cet6': 10,
                'gk': 6,
                'ky': 10,
                'toefl': 15,
                }

tags_chs = {'cet4': '四级',
            'cet6': '六级',
            'gk': '高考',
            'ky': '考研',
            'toefl': '托福',
            }


def get_group_id(data):
    group_id = data["group_id"]
    if data["group_id"] == -1:
        group_id = data["user_id"]
    return group_id


def gen_one_test(tag):
    if tag in contest_map:
        contest_list = contest_map[tag]
        i = random.randint(0, len(contest_list) - 1)
        return contest_list[i]


class VocabGroup:
    def __init__(self):
        self.img2 = "[CQ:face,id=320][CQ:face,id=320][CQ:face,id=320]"
        self.random_vocab_reg = Regexp("^随机(?P<value>.+)单词$")
        self.seq_vocab_reg = Regexp("^连续(?P<value>.+)单词$")
        self.ans_map = {}
        self.seq_open = []
        self.group_ids = GROUPS_ID
        self.user_scores = load_pickle(ROOT + "/user_scores.pickle")
        self.user_nickname = load_pickle(ROOT + "/user_nickname.pickle")
        if self.user_scores is None:
            self.user_scores = {}
        if self.user_nickname is None:
            self.user_nickname = {}

        self.send_contest_queue = []
        threading.Thread(target=self.send_contest_thread).start()

    def send_contest_thread(self):
        asyncio.run(self.async_send_contest_thread())

    async def async_send_contest_thread(self):
        while True:
            if len(self.send_contest_queue) > 0:
                contest_data = self.send_contest_queue.pop(0)
                await self.gen_one_test(*contest_data)
            else:
                await sleep(1)

    async def send_response(self, bot, data, reply, at=False):
        if at:
            if data["group_id"] == -1:
                await bot.sendPrivateMsg(data["user_id"], reply)
            else:
                await bot.sendGroupMsg(data["group_id"],
                                       "[CQ:reply,id={}][CQ:at,qq={}]{}".format(data["message_id"], data["user_id"],
                                                                                reply))
        else:
            if data["group_id"] == -1:
                await bot.sendPrivateMsg(data["user_id"], reply)
            else:
                await bot.sendGroupMsg(data["group_id"], reply)

    async def __call__(self, bot, data):
        flag = False
        for gid in self.group_ids:
            if data["group_id"] == gid:
                flag = True
                break
        if data["group_id"] == -1 or flag:
            if await self.process_ask_one_test(bot, data):
                return True
            if await self.process_ask_seq_test(bot, data):
                return True
            if await self.process_response(bot, data):
                return True
            if await self.process_rank(bot, data):
                return True
            if await self.process_menu(bot, data):
                return True
        return False

    async def process_menu(self, bot, data):
        content = data["message"].strip()
        if content == "菜单":
            reply = "\n".join([
                "[随机/连续][高考/四级/六级/托福]单词",
                "例：连续高考单词",
                "排行榜",
            ])
            await self.send_response(bot, data, reply)
            return True
        return False

    async def process_rank(self, bot, data):
        content = data["message"].strip()
        if content == "排行榜":
            group_id = get_group_id(data)
            if group_id not in self.user_scores:
                self.user_scores[group_id] = {}
            user_scores_group = self.user_scores[group_id]
            rank_list = []
            for user_id in user_scores_group:
                rank_list.append((self.user_nickname[user_id], user_scores_group[user_id]))
            sorted_lst = sorted(rank_list, key=lambda x: x[1], reverse=True)
            output = []
            for i, l in enumerate(sorted_lst):
                if i + 1 >= 10:
                    break
                output.append("{}. {} {}分".format(i + 1, l[0], l[1]))
            reply = "\n".join(output)
            await self.send_response(bot, data, reply)
            return True
        return False

    async def process_ask_one_test(self, bot, data):
        content = data["message"].strip()
        ret = self.random_vocab_reg.findMap(content)
        if ret is not None:
            value = ret['value'].toStr()
            await self.gen_one_test(bot, data, value)

            # 关闭连续作答
            group_id = get_group_id(data)
            if group_id in self.seq_open:
                self.seq_open.remove(group_id)

            return True
        return False

    async def process_ask_seq_test(self, bot, data):
        content = data["message"].strip()
        ret = self.seq_vocab_reg.findMap(content)
        if ret is not None:
            value = ret['value'].toStr()
            group_id = get_group_id(data)
            self.seq_open.append(group_id)
            await self.gen_one_test(bot, data, value)
            return True
        return False

    async def gen_one_test(self, bot, data, value):
        ansp = None
        if value == "四级":
            ansp = gen_one_test("cet4")
        elif value == "六级":
            ansp = gen_one_test("cet6")
        elif value == "考研":
            ansp = gen_one_test("ky")
        elif value == "高考":
            ansp = gen_one_test("gk")
        elif value == "托福":
            ansp = gen_one_test("toefl")
        if ansp is not None:
            self.save_ansp(ansp, data)
            await self.send_response(bot, data, ansp['question'])

    async def process_response(self, bot, data):
        content = str(data["message"]).strip()
        ansp = self.load_ansp(data)
        if ansp is not None:
            content = content.replace("[CQ:at,qq=3185678695]", "").strip().upper()
            if content == ansp['ans1']:
                addition = addition_map[ansp['tag']]
                score = self.add_score(data, addition)
                reply = "回答正确！{} 加{}分 \n当前得分：{}\n{}\n{}".format(
                    data['nickname'],
                    addition,
                    score,
                    self.img2,
                    ansp['ans2'])
                self.remove_ansp(data)
                await self.send_response(bot, data, reply, at=True)
                # 连续作答
                await sleep(5)
                group_id = get_group_id(data)
                if group_id in self.seq_open:
                    # await self.gen_one_test(bot, data, tags_chs[ansp['tag']])
                    self.send_contest_queue.append([bot, data, tags_chs[ansp['tag']]])
                return True
            elif content == 'A' \
                    or content == 'B' \
                    or content == 'C' \
                    or content == 'D':
                addition = -10
                score = self.add_score(data, addition)
                reply = "答错了，扣{}分\n当前得分：{}".format(-addition, score)
                await self.send_response(bot, data, reply, at=True)
                return True
        return False

    def save_ansp(self, ansp, data):
        group_id = get_group_id(data)
        self.ans_map[group_id] = ansp

    def load_ansp(self, data):
        group_id = get_group_id(data)
        if group_id in self.ans_map:
            return self.ans_map[group_id]
        return None

    def remove_ansp(self, data):
        group_id = get_group_id(data)
        if group_id in self.ans_map:
            self.ans_map.pop(group_id)

    def add_score(self, data, ds):
        user_id = data['user_id']
        nickname = data['nickname']
        self.user_nickname[user_id] = nickname
        group_id = get_group_id(data)
        if group_id not in self.user_scores:
            self.user_scores[group_id] = {}
        user_scores_group = self.user_scores[group_id]
        if user_id not in user_scores_group:
            user_scores_group[user_id] = 0
        user_scores_group[user_id] += ds
        write_pickle(ROOT + f"/user_scores.pickle", self.user_scores)
        write_pickle(ROOT + f"/user_nickname.pickle", self.user_nickname)
        return user_scores_group[user_id]

    def read_score(self, data):
        user_id = data['user_id']
        nickname = data['nickname']
        self.user_nickname[user_id] = nickname
        group_id = get_group_id(data)
        if group_id not in self.user_scores:
            self.user_scores[group_id] = {}
        user_scores_group = self.user_scores[group_id]
        if user_id not in user_scores_group:
            user_scores_group[user_id] = 0
        return user_scores_group[user_id]
