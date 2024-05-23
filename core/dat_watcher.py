import os
import shutil
import time
from typing import List
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler

from config import Config
from core.dat_utils import parse_dat_path


class DatFileHandler(FileSystemEventHandler):
    def __init__(
        self, config: Config, whitelisted_users: List[str], handle_dat_file: callable
    ):
        self.config = config
        self.whitelisted_users = whitelisted_users
        self.handle_dat_file = handle_dat_file

    def on_any_event(self, event):
        if event.is_directory or not event.src_path.endswith(".dat"):
            return

        file_info = parse_dat_path(event.src_path)
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


class RedictHandler(FileSystemEventHandler):
    def __init__(
        self,
        config: Config,
        redict_dir: str,
    ):
        self.config = config
        self.redict_dir = redict_dir
        pass

    def on_any_event(self, event):
        src_path = event.src_path

        if os.path.isdir(src_path):
            return

        filename = os.path.basename(src_path)
        dirname = os.path.dirname(src_path).split(os.sep)[-1]

        target_dir = os.path.join(self.redict_dir, dirname)
        target_path = os.path.join(target_dir, filename)

        os.makedirs(target_dir, exist_ok=True)

        try:
            shutil.copyfile(src_path, target_path)
            print(f"文件 {filename} 已重定向到 {target_path}")
        except Exception as e:
            print(f"文件 {filename} 重定向失败: {e}")

    def on_created(self, event: FileSystemEvent) -> None:
        self.on_any_event(event)

    def on_modified(self, event: FileSystemEvent) -> None:
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

            # 监视 MsgAttach 目录下的 .dat 文件
            msg_attach_dir = os.path.join(root_dir, "FileStorage", "MsgAttach")
            observer.schedule(
                DatFileHandler(
                    config=config,
                    whitelisted_users=whitelisted_users,
                    handle_dat_file=handle_dat_file,
                ),
                msg_attach_dir,
                recursive=True,
            )

            # 监视 File 目录下的文件进行重定向
            if config.is_file_redict:
                file_dir = os.path.join(root_dir, "FileStorage", "File")
                observer.schedule(
                    RedictHandler(config=config, redict_dir=config.file_redict_path),
                    file_dir,
                    recursive=True,
                )

            # 监视 Video 目录下的文件进行重定向
            if config.is_video_redict:
                video_dir = os.path.join(root_dir, "FileStorage", "Video")
                observer.schedule(
                    RedictHandler(config=config, redict_dir=config.video_redict_path),
                    video_dir,
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
