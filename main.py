import hashlib
import json
import os
import shutil
import sqlite3
from typing import Dict, List

from dat_utils import handle_dat_file, parse_path, read_dat_files
from dat_watcher import watch_dat_files
from decode_db import decrypt_sqlite_file
from get_wx_info import read_info


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
    # dat_files_info = read_dat_files(
    #     msg_attach_path, ["4e57d4ac0a4bd64c6f052e7e755bc2e9"]
    # )
    # print(f"共找到 {len(dat_files_info)} 个 .dat 文件")

    # for file_info in dat_files_info:
    #     handle_dat_file(file_info, md5_user_dict, wx_name)

    # 监视 msg_attach_path 下的文件变化
    watch_dat_files(
        root_dir=msg_attach_path,
        whitelisted_users=["4e57d4ac0a4bd64c6f052e7e755bc2e9"],
        handle_dat_file=lambda file_info: handle_dat_file(
            file_info, md5_user_dict, wx_name
        ),
    )
