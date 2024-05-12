import hashlib
import json
import os
import re
import shutil
import sqlite3
from datetime import datetime
import time
from typing import Dict, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from batch_decode_dat import decode_image
from decode_db import decrypt_sqlite_file
from get_wx_info import read_info


def parse_path(path: str) -> Dict[str, str]:
    """
    解析文件路径，提取用户ID、日期和文件名
    """
    path = os.path.normpath(path).replace("\\", "/")
    match = re.match(
        r".*?MsgAttach/([a-fA-F0-9]{32})/Image/(\d{4}-\d{2})/(.+?\.dat)", path
    )
    if match:
        md5_id, date, file_name = match.groups()
        last_edit_time = datetime.fromtimestamp(os.path.getmtime(path))
        return {
            "path": path,
            "md5_id": md5_id,
            "date": date,
            "file_name": file_name,
            "last_edit_time": last_edit_time,
        }
    else:
        return {}



def read_dat_files(
    root_dir: str, whitelisted_md5_ids: List[str] = []
) -> List[Dict[str, str]]:
    """
    读取指定目录下的所有 .dat 文件，并将文件信息存储在字典数组中
    """
    result = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".dat"):
                file_path = os.path.join(dirpath, filename)
                file_info = parse_path(file_path)
                if file_info and (
                    not whitelisted_md5_ids
                    or file_info.get("md5_id") in whitelisted_md5_ids
                ):
                    result.append(file_info)
    return result


def handle_dat_file(file_info: Dict[str, str]):
    """
    处理 .dat 文件
    """
    file_path = file_info.get("path")
    md5_id = file_info.get("md5_id")
    date = file_info.get("date")
    file_name = file_info.get("file_name")
    last_edit_time = file_info.get("last_edit_time")

    base_name, ext = os.path.splitext(file_name)
    edit_date = last_edit_time.strftime("%Y-%m-%d")

    wx_info = md5_user_dict.get(md5_id)
    if not wx_info:
        print(f"未找到 md5_id 为 {md5_id} 的用户信息")
        return
    user_name = (
        wx_info.get("remark") or wx_info.get("nick_name") or wx_info.get("alias")
    )

    output_path = f"./output/{wx_name}/{edit_date}/{user_name}/{base_name}.jpg"
    print(f"正在解码 {file_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    decode_image(file_path, output_path)


class MyHandler(FileSystemEventHandler):
    def __init__(self, whitelisted_users: List[str]):
        self.whitelisted_users = whitelisted_users

    def on_any_event(self, event):
        if event.is_directory or not event.src_path.endswith(".dat"):
            return

        file_info = parse_path(event.src_path)
        if file_info:
            if (
                not self.whitelisted_users
                or file_info.get("md5_id") in self.whitelisted_users
            ):
                handle_dat_file(file_info)

    def on_created(self, event):
        self.on_any_event(event)

    def on_modified(self, event):
        self.on_any_event(event)


def watch_dat_files(root_dir: str, whitelisted_users: List[str] = []):
    """
    监视指定目录下的 .dat 文件，并将文件信息存储在字典数组中
    """
    observer = Observer()
    observer.schedule(MyHandler(whitelisted_users), root_dir, recursive=True)
    observer.start()
    print(f"开始监视 {root_dir} 下的文件变化...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    # 从 ./version_list.json 读取版本信息

    with open("./version_list.json", "r") as f:
        version_list = json.load(f)

    # 读取微信信息
    result = read_info(version_list=version_list, is_logging=True)
    if not result:
        print("微信信息获取失败")
        exit(1)
    wx_name = result[0].get("name")
    wx_file_path = result[0].get("filePath")
    wx_key = result[0].get("key")
    if not wx_key:
        print(f"获取 {wx_name} 的key失败")
        exit(1)

    # 破解MicroMsg.db数据库
    micro_db_path = os.path.join(wx_file_path, "Msg", "MicroMsg.db")
    micro_decrypted_db_path = os.path.join(
        os.path.abspath("."), "dbs", "decrypted_micro_msg.db"
    )
    os.makedirs(os.path.dirname(micro_decrypted_db_path), exist_ok=True)
    shutil.copyfile(micro_db_path, micro_decrypted_db_path)
    decrypt_sqlite_file(wx_key, micro_decrypted_db_path)

    # 读取MicroMsg数据库
    micro_db_conn = sqlite3.connect(micro_decrypted_db_path)
    micro_db_conn.row_factory = sqlite3.Row
    micro_cursor = micro_db_conn.cursor()
    micro_cursor.execute("SELECT * FROM Contact")
    contact_list = micro_cursor.fetchall()
    micro_db_conn.close()

    # 生成 md5_user_dict 映射表
    md5_user_dict = {
        hashlib.md5(contact["UserName"].encode()).hexdigest(): {
            "user_name": contact["UserName"],
            "alias": contact["Alias"],
            "nick_name": contact["NickName"],
            "remark": contact["Remark"],
        }
        for contact in contact_list
    }

    msg_attach_path = os.path.join(wx_file_path, "FileStorage", "MsgAttach")

    # 获取 msg_attach_path 下的所有文件夹
    # dat_files_info = read_dat_files(msg_attach_path)
    # print(f"共找到 {len(dat_files_info)} 个 .dat 文件")

    # for file_info in dat_files_info:
    #     handle_dat_file(file_info)

    # 监视 msg_attach_path 下的文件变化
    watch_dat_files(
        msg_attach_path, whitelisted_users=["4e57d4ac0a4bd64c6f052e7e755bc2e9"]
    )
