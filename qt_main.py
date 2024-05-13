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
    QFileDialog,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QFormLayout,
)
from PyQt6.QtCore import Qt


class AddWhitelistDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(300, 300, 500, 300)
        self.setWindowTitle("添加白名单")

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 搜索栏
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索用户名")
        self.layout.addWidget(self.search_box)

        # 列表
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["ID", "昵称", "签名"])
        self.layout.addWidget(self.table_widget)

        # 确认按钮
        self.buttons_layout = QHBoxLayout()
        self.confirm_button = QPushButton("添加")
        self.cancel_button = QPushButton("取消")
        self.buttons_layout.addWidget(self.confirm_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.buttons_layout)

        # 绑定事件
        self.confirm_button.clicked.connect(self.add_selected_users)
        self.cancel_button.clicked.connect(self.close)
        self.search_box.textChanged.connect(self.filter_user)

        self.populate_user_list()

    def populate_user_list(self):
        users = [
            {"nickname": "Alice", "id": "001", "signature": "AI enthusiast"},
            {"nickname": "Bob", "id": "002", "signature": "Python developer"},
        ]
        self.table_widget.setRowCount(len(users))

        for row, user in enumerate(users):
            # ID
            id_item = QTableWidgetItem(user["id"])
            id_item.setCheckState(Qt.CheckState.Unchecked)
            # 昵称
            nickname_item = QTableWidgetItem(user["nickname"])
            # 签名
            signature_item = QTableWidgetItem(user["signature"])

            self.table_widget.setItem(row, 0, id_item)
            self.table_widget.setItem(row, 1, nickname_item)
            self.table_widget.setItem(row, 2, signature_item)

    def filter_user(self, text):
        # 先隐藏所有项
        for row in range(self.table_widget.rowCount()):
            match = False
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if text.lower() in item.text().lower():
                    match = True
                    break
            self.table_widget.setRowHidden(row, not match)

    def add_selected_users(self):
        for row in range(self.table_widget.rowCount()):
            checkbox_item = self.table_widget.item(row, 0)
            if checkbox_item.checkState() == Qt.CheckState.Checked:
                user = {
                    "id": self.table_widget.item(row, 0).text(),
                    "nickname": self.table_widget.item(row, 1).text(),
                    "signature": self.table_widget.item(row, 2).text(),
                }
                self.parent().add_whitelist_item(user)
        self.close()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle("MsgAttach Watcher")

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 表单
        self.form_layout = QFormLayout()
        self.form_layout.setHorizontalSpacing(10)

        # 保存的根路径
        self.base_path_label = QLabel("路径:")
        self.base_path_layout = QHBoxLayout()
        self.base_path_input = QLineEdit()
        self.base_path_button = QPushButton("选择路径")
        self.base_path_button.setToolTip("选择要转换的图片文件夹")
        self.base_path_layout.addWidget(self.base_path_input)
        self.base_path_layout.addWidget(self.base_path_button)
        self.form_layout.addRow(self.base_path_label, self.base_path_layout)

        # 保存路径模板
        self.path_template_label = QLabel("模板:")
        self.path_template_input = QLineEdit()
        self.form_layout.addRow(self.path_template_label, self.path_template_input)

        # 日期格式
        self.date_format_label = QLabel("日期格式:")
        self.date_format_input = QLineEdit()
        self.form_layout.addRow(self.date_format_label, self.date_format_input)

        # 白名单
        self.whitelist_label = QLabel("白名单:")
        self.whitelist_layout = QVBoxLayout()
        self.whitelist = QListWidget()
        self.add_whitelist_button = QPushButton("添加白名单")
        self.whitelist_layout.addWidget(self.whitelist)
        self.whitelist_layout.addWidget(self.add_whitelist_button)
        self.form_layout.addRow(self.whitelist_label, self.whitelist_layout)

        # 设置标签最小宽度
        self.base_path_label.setMinimumWidth(50)
        self.path_template_label.setMinimumWidth(50)
        self.date_format_label.setMinimumWidth(50)
        self.whitelist_label.setMinimumWidth(50)

        self.layout.addLayout(self.form_layout)

        # 绑定事件
        self.base_path_button.clicked.connect(self.choose_folder)
        self.add_whitelist_button.clicked.connect(self.show_add_whitelist_dialog)
        self.whitelist.itemDoubleClicked.connect(self.remove_whitelist_item)

    def choose_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "选择文件夹", self.base_path_input.text()
        )
        if folder_path:
            self.base_path_input.setText(folder_path)

    def remove_whitelist_item(self, item):
        self.whitelist.takeItem(self.whitelist.row(item))

    def show_add_whitelist_dialog(self):
        dialog = AddWhitelistDialog(self)
        dialog.show()

    def add_whitelist_item(self, user):
        self.whitelist.addItem(user.get("nickname", "未知用户"))

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
