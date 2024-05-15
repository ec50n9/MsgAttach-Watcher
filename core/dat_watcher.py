import time
from typing import List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config import Config
from core.dat_utils import parse_path


class MyHandler(FileSystemEventHandler):
    def __init__(
        self, config: Config, whitelisted_users: List[str], handle_dat_file: callable
    ):
        self.config = config
        self.whitelisted_users = whitelisted_users
        self.handle_dat_file = handle_dat_file

    def on_any_event(self, event):
        if event.is_directory or not event.src_path.endswith(".dat"):
            return

        file_info = parse_path(event.src_path)
        if file_info:
            if (not self.config.save_thumb) and file_info.get("jpg_type") == "Thumb":
                return

            if (
                self.whitelisted_users
                and file_info.get("md5_id") not in self.whitelisted_users
            ):
                return

            self.handle_dat_file(file_info)

    def on_created(self, event):
        self.on_any_event(event)

    def on_modified(self, event):
        self.on_any_event(event)


def watch_dat_files(
    config: Config,
    root_dir: str,
    handle_dat_file: callable,
    whitelisted_users: List[str] = [],
):
    """
    监视指定目录下的 .dat 文件，并将文件信息存储在字典数组中
    """
    observer = None
    running = False

    def start_watching():
        nonlocal observer, running
        if not running:
            observer = Observer()
            observer.schedule(
                MyHandler(
                    config=config,
                    whitelisted_users=whitelisted_users,
                    handle_dat_file=handle_dat_file,
                ),
                root_dir,
                recursive=True,
            )
            observer.start()
            print(f"开始监视 {root_dir} 下的文件变化...")
            running = True

    def stop_watching():
        nonlocal observer, running
        if running:
            observer.stop()
            observer.join()
            print(f"停止监视 {root_dir} 下的文件变化...")
            running = False

    start_watching()
    return stop_watching
