#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import time
import hashlib
import json
import os
import shutil
import sqlite3
import sys
from typing import Dict
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
import psutil
import pystache

from config import ConfigManager
from core.batch_decode_dat import decode_image
from core.dat_watcher import watch_dat_files
from core.decode_db import decrypt_sqlite_file
from core.get_wx_info import read_info
from views.main_window import MainWindow


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
    jpg_type = file_info.get("jpg_type")
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
            "file_type": jpg_type,
            "file_origin_name": file_name,
            "file_base_name": base_name,
            "file_wx_time": wx_date,
            "file_edit_time": (last_edit_time or datetime.now()).strftime(
                edit_time_format
            ),
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
        return None, None, None
    wx_name = result[0].get("name")
    wx_file_path = result[0].get("filePath")
    wx_key = result[0].get("key")
    if not wx_key:
        print(f"获取 {wx_name} 的key失败")
        return None, None, None

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


def main(wx_name, msg_attach_path, md5_user_dict):
    # 加载配置
    config_manager = ConfigManager("./config.json")

    is_watching = False
    stop_watching = None

    def start_watching_wrapper():
        nonlocal is_watching, stop_watching, wx_name, msg_attach_path, md5_user_dict, config_manager
        base_path = os.path.normpath(config_manager.config.base_path)
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        path_template = os.path.normpath(config_manager.config.path_template)
        user_name_in_whitelist = [
            hashlib.md5(user.user_name.encode()).hexdigest()
            for user in config_manager.config.whitelist
        ]
        output_path_template = os.path.join(base_path, path_template)
        edit_time_format = config_manager.config.date_format

        # 监听文件变化
        is_watching = True
        stop_watching = watch_dat_files(
            config=config_manager.config,
            root_dir=msg_attach_path,
            whitelisted_users=user_name_in_whitelist,
            handle_dat_file=lambda file_info: handle_dat_file(
                file_info=file_info,
                md5_user_dict=md5_user_dict,
                wx_name=wx_name,
                output_path_template=output_path_template,
                edit_time_format=edit_time_format,
            ),
        )

    def stop_watching_wrapper():
        nonlocal is_watching, stop_watching
        if stop_watching is None:
            print("未开始监听文件变化")
            return
        is_watching = False
        stop_watching()

    window = MainWindow(
        config=config_manager.config,
        user_list=[v for _, v in md5_user_dict.items()],
        on_save_config=config_manager.save_config,
        on_start_watching=start_watching_wrapper,
        on_stop_watching=stop_watching_wrapper,
    )
    window.show()


class WaitForWechatStartWorker(QThread):

    finished = pyqtSignal(str, str, dict)

    def run(self):
        while True:
            for process in psutil.process_iter(["name", "exe", "pid", "cmdline"]):
                if process.name() == "WeChat.exe":
                    # 初始化微信信息
                    wx_name, msg_attach_path, md5_user_dict = init_wx_info()
                    if wx_name is not None:
                        self.finished.emit(wx_name, msg_attach_path, md5_user_dict)
                        return
                    else:
                        print("微信信息获取失败")

            time.sleep(3)


def app():
    app = QApplication(sys.argv)

    # 显示等待窗口
    waiting_window = QMessageBox()
    waiting_window.setWindowTitle("等待启动中")
    waiting_window.setText("请在微信客户端中登录并保持登录状态")
    waiting_window.addButton("取消", QMessageBox.ButtonRole.YesRole)
    waiting_window.show()

    # 等待微信启动
    worker = WaitForWechatStartWorker()

    def callback(wx_name, msg_attach_path, md5_user_dict):
        waiting_window.close()
        main(
            wx_name=wx_name,
            msg_attach_path=msg_attach_path,
            md5_user_dict=md5_user_dict,
        )

    worker.finished.connect(callback)
    worker.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    app()
