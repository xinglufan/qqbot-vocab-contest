# qqbot-vocab-contest

抢答背单词qq机器人，基于go-cqhttp

# 部署方法

### 1. 部署QQ机器人

按照go-cqhttp官方文档部署好qq机器人 

github地址 https://github.com/Mrs4s/go-cqhttp

部署文档 https://docs.go-cqhttp.org/guide/quick_start.html#%E5%9F%BA%E7%A1%80%E6%95%99%E7%A8%8B

注意需配置好**正向Websocket**服务

### 2. 部署背单词BOT

克隆该项目到本地

`git clone https://github.com/xinglufan/qqbot-vocab-contest`

配置好python环境 （建议使用python3.7以上）

安装依赖

`pip install -r requirements.txt`

修改项目中的config.py脚本，怎么修改注释应该写得很清楚了

```python
# go-cqhttp 服务的正向WS服务器地址
host = "ws://127.0.0.1:8080"

# 该项目的绝对路径
ROOT = "./"

# 白名单QQ群，只有添加群号，机器人才会响应
GROUPS_ID = [
    1234567890,
]
```



运行main.py脚本

`python main.py`

# 3.使用方法

在加了白名单的群里输入下面的关键字：

`菜单`

`随机/连续高考/四级/六级/托福单词 `

例如输入：`连续六级单词 `

连续的意思是群员答完一题自动生成下一题

# 4.联系方式

欢迎直接加群体验255954365，有问题也可以加群主

另外推荐一下我的APP 《**单词播放器**》

看美剧时可以点词翻译，词汇标注等功能！

详情点击 http://aipie.cool



