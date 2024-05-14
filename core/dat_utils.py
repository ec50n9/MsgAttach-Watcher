import re
import os
from datetime import datetime
from typing import Dict, List

from core.batch_decode_dat import decode_image


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
