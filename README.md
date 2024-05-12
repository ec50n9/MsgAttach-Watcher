# MsgAttach Watcher

一个可以监听微信 MsgAttach 文件夹并自动解码保存图片的 Python 命令行工具。部分实现参考自: [PyWxDump](https://github.com/xaoyaoo/PyWxDump)

简单来说，它可以实时获取好友聊天记录中的图片单独保存到指定文件夹。


由于是临时起意帮朋友解决问题写的，为了图方便，就没有开发图形化界面和打包成 exe 文件，因此暂时仅支持安装好 Python3 环境的系统上使用命令行执行，后续有时间的话会尽量实现图形化配置界面和打包成 exe 文件（也有可能就不更新了，因为我懒hhh）。

如果有需求，可以提 issue 来告诉我，我会尽快添加。

（注：本项目仅用于学习交流，请勿用于商业用途。）

（注：本项目仅支持 Windows 系统，Mac 系统请自行修改代码。）

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

## Disclaimer (VERY VERY VERY IMPORTANT ! ! ! ! ! !)

### 1. Purpose of use

* This project is only for learning and communication purposes, **please do not use it for illegal purposes**, **please
  do not use it for illegal purposes**, **please do not use it for illegal purposes
  **, otherwise the consequences will be borne by yourself.
* Users understand and agree that any violation of laws and regulations, infringement of the legitimate rights and interests of others, is unrelated to this project and its developers, and the consequences are borne by the user themselves.

### 2. Usage Period

* You should delete the source code and (compiled) program of this project within 24 hours of downloading, saving, compiling, and using it; any use beyond this period is not related to this project or its developer.

### 3. Operation specifications

* This project only allows backup and viewing of the database under authorization. It is strictly prohibited for illegal purposes, otherwise all related responsibilities will be borne by the user. Any legal liability incurred by the user due to violation of this regulation will be borne by the user, and is unrelated to this project and its developer.
* It is strictly prohibited to use it to steal others' privacy. Otherwise, all relevant responsibilities shall be borne by yourself.
* It is strictly prohibited to conduct secondary development, otherwise all related responsibilities shall be borne by yourself.

### 4. Acceptance of Disclaimer

* Downloading, saving, further browsing the source code, or downloading, installing, compiling, and using this program indicates that you agree with this warning and promise to abide by it;

### 5. Forbidden for illegal testing or penetration

* It is prohibited to use the relevant technologies of this project to engage in illegal testing or penetration, and it is prohibited to use the relevant codes or related technologies of this project to engage in any illegal work. Any adverse consequences arising therefrom are not related to this project and its developers.
* Any resulting adverse consequences, including but not limited to data leakage, system failure, and privacy infringement, are not related to this project or its developers and are the responsibility of the user.

### 6. Modification of disclaimer

* This disclaimer may be modified and adjusted based on the project's operating conditions and changes in laws and regulations. Users should regularly check this page for the latest version of the disclaimer, and should comply with the latest version of the disclaimer when using this project.

### 7. Others

* In addition to the provisions of this disclaimer, users should comply with relevant laws, regulations, and ethical norms during the use of this project. The project and its developers will not be held responsible for any disputes or losses caused by users' violation of relevant regulations.

* Users are requested to carefully read and understand all contents of this disclaimer, and ensure that they strictly comply with relevant regulations when using this project.

## Ⅳ. 免责声明（非常重要！！！！！！！）

### 1. 使用目的

* 本项目仅供学习交流使用，**请勿用于非法用途**，**请勿用于非法用途**，**请勿用于非法用途**，否则后果自负。
* 用户理解并同意，任何违反法律法规、侵犯他人合法权益的行为，均与本项目及其开发者无关，后果由用户自行承担。

### 2. 使用期限

* 您应该在下载保存，编译使用本项目的24小时内，删除本项目的源代码和（编译出的）程序；超出此期限的任何使用行为，一概与本项目及其开发者无关。

### 3. 操作规范

* 本项目仅允许在授权情况下对数据库进行备份与查看，严禁用于非法目的，否则自行承担所有相关责任；用户如因违反此规定而引发的任何法律责任，将由用户自行承担，与本项目及其开发者无关。
* 严禁用于窃取他人隐私，严禁用于窃取他人隐私，严禁用于窃取他人隐私，否则自行承担所有相关责任。
* 严禁进行二次开发，严禁进行二次开发，严禁进行二次开发，否则自行承担所有相关责任。

### 4. 免责声明接受

* 下载、保存、进一步浏览源代码或者下载安装、编译使用本程序，表示你同意本警告，并承诺遵守它;

### 5. 禁止用于非法测试或渗透

* 禁止利用本项目的相关技术从事非法测试或渗透，禁止利用本项目的相关代码或相关技术从事任何非法工作，如因此产生的一切不良后果与本项目及其开发者无关。
* 任何因此产生的不良后果，包括但不限于数据泄露、系统瘫痪、侵犯隐私等，均与本项目及其开发者无关，责任由用户自行承担。

### 6. 免责声明修改

* 本免责声明可能根据项目运行情况和法律法规的变化进行修改和调整。用户应定期查阅本页面以获取最新版本的免责声明，使用本项目时应遵守最新版本的免责声明。

### 7. 其他

* 除本免责声明规定外，用户在使用本项目过程中应遵守相关的法律法规和道德规范。对于因用户违反相关规定而引发的任何纠纷或损失，本项目及其开发者不承担任何责任。

* 请用户慎重阅读并理解本免责声明的所有内容，确保在使用本项目时严格遵守相关规定。