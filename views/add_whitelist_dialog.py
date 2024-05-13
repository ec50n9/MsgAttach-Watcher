import sys
from PyQt6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
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
