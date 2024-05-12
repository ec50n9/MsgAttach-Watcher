import time
from typing import List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from dat_utils import parse_path


class MyHandler(FileSystemEventHandler):
    def __init__(self, whitelisted_users: List[str], handle_dat_file: callable):
        self.whitelisted_users = whitelisted_users
        self.handle_dat_file = handle_dat_file

    def on_any_event(self, event):
        if event.is_directory or not event.src_path.endswith(".dat"):
            return

        file_info = parse_path(event.src_path)
        if file_info:
            if (
                not self.whitelisted_users
                or file_info.get("md5_id") in self.whitelisted_users
            ):
                self.handle_dat_file(file_info)

    def on_created(self, event):
        self.on_any_event(event)

    def on_modified(self, event):
        self.on_any_event(event)


def watch_dat_files(root_dir: str, handle_dat_file: callable, whitelisted_users: List[str] = []):
    """
    监视指定目录下的 .dat 文件，并将文件信息存储在字典数组中
    """
    observer = Observer()
    observer.schedule(MyHandler(whitelisted_users, handle_dat_file), root_dir, recursive=True)
    observer.start()
    print(f"开始监视 {root_dir} 下的文件变化...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
