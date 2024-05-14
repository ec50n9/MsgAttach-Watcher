import hashlib
import json
import os
import shutil
import sqlite3
import time
import pystache
from typing import Dict

from core.batch_decode_dat import decode_image
from core.dat_utils import read_dat_files
from core.dat_watcher import watch_dat_files
from core.decode_db import decrypt_sqlite_file
from core.get_wx_info import read_info


# 模板变量中使用的 file_edit_time 的时间格式
EDIT_TIME_FORMAT = "%Y-%m-%d"
# 转换好的图片的输出路径，可使用模板变量，具体格式见 README.md
OUTPUT_PATH_TEMPLATE = "./output/{{self_wx_name}}/{{file_edit_time}}/{{contact_user_name}}/{{file_base_name}}.jpg"


def handle_dat_file(
    file_info: Dict[str, str],
    md5_user_dict: Dict[str, Dict],
    wx_name: str,
    output_path_template: str,
    edit_time_format: str = "%Y-%m-%d",
):
    """
    处理 .dat 文件
    """
    file_path = file_info.get("path")
    md5_id = file_info.get("md5_id")
    wx_date = file_info.get("date")
    file_name = file_info.get("file_name")
    last_edit_time = file_info.get("last_edit_time")

    base_name, ext = os.path.splitext(file_name)

    contact_user_info = md5_user_dict.get(md5_id)
    if not contact_user_info:
        print(f"未找到 md5_id 为 {md5_id} 的用户信息")
        return
    contact_user_name = (
        contact_user_info.get("remark")
        or contact_user_info.get("nick_name")
        or contact_user_info.get("alias")
    )
    contact_alias = contact_user_info.get("alias")

    output_path = pystache.render(
        output_path_template,
        {
            "self_wx_name": wx_name,
            "contact_md5_id": md5_id,
            "contact_user_name": contact_user_name,
            "contact_alias": contact_alias,
            "file_origin_name": file_name,
            "file_base_name": base_name,
            "file_wx_time": wx_date,
            "file_edit_time": last_edit_time.strftime(edit_time_format),
        },
    )

    print(f"正在解码 {file_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    decode_image(file_path, output_path)


def init_wx_info():
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

    return wx_name, msg_attach_path, md5_user_dict


if __name__ == "__main__":
    wx_name, msg_attach_path, md5_user_dict = init_wx_info()

    def start_handle_all_dat_files():
        """
        获取 msg_attach_path 下的所有文件夹
        """
        dat_files_info = read_dat_files(msg_attach_path, [])
        print(f"共找到 {len(dat_files_info)} 个 .dat 文件")
        for file_info in dat_files_info:
            handle_dat_file(
                file_info=file_info,
                md5_user_dict=md5_user_dict,
                wx_name=wx_name,
                output_path_template=OUTPUT_PATH_TEMPLATE,
                edit_time_format=EDIT_TIME_FORMAT,
            )

    running, start_watching, stop_watching = watch_dat_files(
        root_dir=msg_attach_path,
        whitelisted_users=[],
        handle_dat_file=lambda file_info: handle_dat_file(
            file_info=file_info,
            md5_user_dict=md5_user_dict,
            wx_name=wx_name,
            output_path_template=OUTPUT_PATH_TEMPLATE,
            edit_time_format=EDIT_TIME_FORMAT,
        ),
    )

    if not running:
        start_watching()
        time.sleep(5)
        stop_watching()
