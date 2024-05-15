from dataclasses import asdict, dataclass, field, is_dataclass
import json
import os
from typing import Any, List


@dataclass
class User:
    user_name: str
    alias: str = ""
    nick_name: str = ""
    remark: str = ""

    def __str__(self) -> str:
        return f"{self.remark or self.nick_name or self.alias} ({self.user_name})"


@dataclass
class Config:
    base_path: str = "./output"
    path_template: str = (
        "{{self_wx_name}}/{{file_edit_time}}/{{contact_user_name}}/{{file_base_name}}.jpg"
    )
    date_format: str = "%Y-%m-%d"
    whitelist: List[User] = field(default_factory=list)

    @classmethod
    def from_dict(cls, config_dict: dict):
        whitelist = [
            User(**user_dict) for user_dict in config_dict.pop("whitelist", [])
        ]
        return cls(**config_dict, whitelist=whitelist)


class DataclassEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


class ConfigManager:
    config_file_path: str
    config: Config

    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.load_config()

    def load_config(self):
        # 如果文件不存在，在自动创建并写入 {}
        if not os.path.exists(self.config_file_path):
            with open(self.config_file_path, "w") as f:
                f.write("{}")

        with open(self.config_file_path, "r") as f:
            config_dict = json.load(f)
            self.config = Config.from_dict(config_dict)

    def save_config(self):
        with open(self.config_file_path, "w") as f:
            config_dict = self.config.__dict__
            json.dump(config_dict, f, cls=DataclassEncoder, indent=4)
