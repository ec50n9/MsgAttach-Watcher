#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QInputDialog,
    QFileDialog,
    QLabel,
)
from PyQt6.QtGui import QFont


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle("MsgAttach Watcher")

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 保存的根路径
        self.base_path_layout = QHBoxLayout()
        self.base_path_label = QLabel("路径:")
        self.base_path_input = QLineEdit()
        self.base_path_button = QPushButton("选择路径")
        self.base_path_button.setToolTip("选择要转换的图片文件夹")
        self.base_path_layout.addWidget(self.base_path_label)
        self.base_path_layout.addWidget(self.base_path_input)
        self.base_path_layout.addWidget(self.base_path_button)

        # 保存路径模板
        self.path_template_layout = QHBoxLayout()
        self.path_template_label = QLabel("模板:")
        self.path_template_input = QLineEdit()
        self.path_template_layout.addWidget(self.path_template_label)
        self.path_template_layout.addWidget(self.path_template_input)

        # 日期格式
        self.date_format_layout = QHBoxLayout()
        self.date_format_label = QLabel("日期格式:")
        self.date_format_input = QLineEdit()
        self.date_format_layout.addWidget(self.date_format_label)
        self.date_format_layout.addWidget(self.date_format_input)

        # 白名单
        self.whitelist_layout = QHBoxLayout()
        self.whitelist_label = QLabel("白名单:")
        self.whitelist = QListWidget()
        self.whitelist_layout.addWidget(self.whitelist_label)
        self.whitelist_layout.addWidget(self.whitelist)

        # 添加白名单按钮
        self.add_whitelist_button = QPushButton("添加白名单")

        self.base_path_label.setMinimumWidth(50)
        self.path_template_label.setMinimumWidth(50)
        self.date_format_label.setMinimumWidth(50)
        self.whitelist_label.setMinimumWidth(50)

        self.layout.addLayout(self.base_path_layout)
        self.layout.addLayout(self.path_template_layout)
        self.layout.addLayout(self.date_format_layout)
        self.layout.addLayout(self.whitelist_layout)
        self.layout.addWidget(self.add_whitelist_button)

        self.base_path_button.clicked.connect(self.choose_folder)
        self.add_whitelist_button.clicked.connect(self.show_add_whitelist_dialog)
        self.whitelist.itemDoubleClicked.connect(self.remove_whitelist_item)

    def choose_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder_path:
            self.base_path_input.setText(folder_path)

    def remove_whitelist_item(self, item):
        self.whitelist.takeItem(self.whitelist.row(item))

    def add_whitelist_item(self):
        username, ok = QInputDialog.getText(self, "添加白名单", "输入用户名:")
        if ok and username:
            self.whitelist.addItem(username)

    def show_add_whitelist_dialog(self):
        self.add_whitelist_item()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "提示",
            "确认退出吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
