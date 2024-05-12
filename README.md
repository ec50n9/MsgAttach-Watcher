# MsgAttach Watcher

一个可以监听微信 MsgAttach 文件夹并自动解码保存图片的 Python 命令行工具。

人话：一个可以实时获取好友聊天记录中的图片单独保存到指定文件夹。

## 如何使用

1. 下载并安装 Python 3.x
2. 下载本项目代码并解压
3. 打开命令提示符，进入项目目录
4. 运行 `pip install -r requirements.txt` 安装依赖
5. 修改 `main.py` 中的 `OUTPUT_PATH_TEMPLATE` 变量，指定图片保存路径
6. 运行 `main.py` 启动程序

```bash
python main.py
```

## OUTPUT_PATH_TEMPLATE 模板变量说明

| 变量 | 说明 |
| --- | --- |
| `self_wx_name` | 当前登录的微信名称 |
| `contact_md5_id` | 图片保存的联系人 md5 加密后的 id |
| `contact_user_name` | 图片保存的联系人名称 |
| `contact_alias` | 图片保存的联系人微信号 |
| `file_origin_name` | 图片保存的原始文件名 |
| `file_base_name` | 图片保存的基础文件名 |
| `file_wx_time` | 图片保存的微信消息时间(仅年和月, 且不可格式化) |
| `file_edit_time` | 图片保存的编辑时间(精确到秒, 可通过 EDIT_TIME_FORMAT 变量格式化) |

默认模板为：

```
EDIT_TIME_FORMAT = "%Y-%m-%d"

OUTPUT_PATH_TEMPLATE = "./output/{{self_wx_name}}/{{file_edit_time}}/{{contact_user_name}}/{{file_base_name}}.jpg"
```

保存路径示例：

```
./output/你的微信名/2024-01-01/好友微信名/xxx.jpg
```

## 说明

1. 程序会监听 MsgAttach 文件夹，当有新的文件到达时，会读取dat文件内容并解密为图片，然后保存到指定路径。
2. 图片保存路径由 `OUTPUT_PATH_TEMPLATE` 变量指定，其中 `%Y%m%d` 表示年月日，`%H%M%S` 表示时分秒。

## 一些乱七八糟的笔记

Msg/Multi/MSG0.db 解密出来后，其中的 Name2ID 表和 MsgAttach 文件夹下的文件夹名称基本是一一对应的，只要把数据库中的 wxid 转换成 md5 即为对应的文件夹名称。
Msg/MicroMsg.db 解密出来后，其中的 Contact 表即为联系人列表，可以先在这个表中选择需要的联系人，然后在 MsgAttach 文件夹下找到对应的文件夹。

流程：
1. 打开并登录微信
2. 运行 get_wx_info.py 获取微信目录和数据库 key
3. 解密并读取 Msg/MicroMsg.db 中的 Contact 表，选择需要监听的联系人，并获取其 wxid
4. 转换 wxid 为 md5 得到文件夹名称
5. 监听文件夹变化，当有新的文件到达时，读取dat文件内容并解密保存为图片。
