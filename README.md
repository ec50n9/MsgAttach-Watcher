Msg/Multi/MSG0.db 解密出来后，其中的 Name2ID 表和 MsgAttach 文件夹下的文件夹名称基本是一一对应的，只要把数据库中的 wxid 转换成 md5 即为对应的文件夹名称。
Msg/MicroMsg.db 解密出来后，其中的 Contact 表即为联系人列表，可以先在这个表中选择需要的联系人，然后在 MsgAttach 文件夹下找到对应的文件夹。

流程：
1. 打开并登录微信
2. 运行 get_wx_info.py 获取微信目录和数据库 key
3. 解密并读取 Msg/MicroMsg.db 中的 Contact 表，选择需要监听的联系人，并获取其 wxid
4. 转换 wxid 为 md5 得到文件夹名称
5. 监听文件夹变化，当有新的文件到达时，读取dat文件内容并解密保存为图片。
