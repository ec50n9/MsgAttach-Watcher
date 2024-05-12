import re
import os
from datetime import datetime
from typing import Dict

from batch_decode_dat import decode_image


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


def handle_dat_file(file_info: Dict[str, str], md5_user_dict: Dict[str, Dict], wx_name: str):
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
