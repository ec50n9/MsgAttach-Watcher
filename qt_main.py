#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PyQt6.QtWidgets import QApplication

from config import ConfigManager
from views.main_window import MainWindow


def main():
    # 加载配置
    config_manager = ConfigManager(os.path.join(os.path.dirname(__file__), 'config.json'))

    app = QApplication(sys.argv)
    window = MainWindow(config=config_manager.config, save_config=config_manager.save_config)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
