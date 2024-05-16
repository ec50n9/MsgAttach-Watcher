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

from config import User


class AddWhitelistDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGeometry(300, 300, 700, 500)
        self.setWindowTitle("添加白名单")

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 搜索栏
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索用户名")
        self.search_box.textChanged.connect(self.filter_user)
        self.layout.addWidget(self.search_box)

        list_actions_layout = QHBoxLayout()
        select_all_button = QPushButton("全选")
        select_all_button.clicked.connect(self.select_all)
        select_none_button = QPushButton("全不选")
        select_none_button.clicked.connect(self.select_none)
        reverse_select_button = QPushButton("反选")
        reverse_select_button.clicked.connect(self.reverse_select)
        list_actions_layout.addWidget(select_all_button)
        list_actions_layout.addWidget(select_none_button)
        list_actions_layout.addWidget(reverse_select_button)
        self.layout.addLayout(list_actions_layout)

        # 列表
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(
            ["原始id", "备注", "微信名称", "微信号"]
        )
        self.table_widget.setColumnWidth(0, 180)
        self.table_widget.setColumnWidth(1, 100)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 150)
        self.layout.addWidget(self.table_widget)

        # 确认按钮
        self.buttons_layout = QHBoxLayout()
        self.confirm_button = QPushButton("保存")
        self.confirm_button.clicked.connect(self.add_selected_users)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.close)
        self.buttons_layout.addWidget(self.confirm_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.buttons_layout)

        self.populate_user_list()

    def select_all(self):
        """全选"""
        for row in range(self.table_widget.rowCount()):
            if not self.table_widget.isRowHidden(row):
                checkbox_item = self.table_widget.item(row, 0)
                checkbox_item.setCheckState(Qt.CheckState.Checked)

    def select_none(self):
        """全不选"""
        for row in range(self.table_widget.rowCount()):
            if not self.table_widget.isRowHidden(row):
                checkbox_item = self.table_widget.item(row, 0)
                checkbox_item.setCheckState(Qt.CheckState.Unchecked)

    def reverse_select(self):
        """反选"""
        for row in range(self.table_widget.rowCount()):
            if not self.table_widget.isRowHidden(row):
                checkbox_item = self.table_widget.item(row, 0)
                if checkbox_item.checkState() == Qt.CheckState.Checked:
                    checkbox_item.setCheckState(Qt.CheckState.Unchecked)
                else:
                    checkbox_item.setCheckState(Qt.CheckState.Checked)

    def populate_user_list(self):
        users = self.parent().user_list
        self.table_widget.setRowCount(len(users))

        user_name_in_whitelist = [
            user.user_name for user in self.parent().config.whitelist
        ]

        for row, user in enumerate(users):
            is_checked = user["user_name"] in user_name_in_whitelist

            # ID
            user_name_item = QTableWidgetItem(user["user_name"])
            user_name_item.setCheckState(
                Qt.CheckState.Unchecked if not is_checked else Qt.CheckState.Checked
            )
            alias_item = QTableWidgetItem(user["alias"])
            nick_name_item = QTableWidgetItem(user["nick_name"])
            remark_item = QTableWidgetItem(user["remark"])

            self.table_widget.setItem(row, 0, user_name_item)
            self.table_widget.setItem(row, 1, remark_item)
            self.table_widget.setItem(row, 2, nick_name_item)
            self.table_widget.setItem(row, 3, alias_item)

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
        user_list = []
        for row in range(self.table_widget.rowCount()):
            checkbox_item = self.table_widget.item(row, 0)
            if checkbox_item.checkState() == Qt.CheckState.Checked:
                user = User(
                    user_name=self.table_widget.item(row, 0).text(),
                    remark=self.table_widget.item(row, 1).text(),
                    nick_name=self.table_widget.item(row, 2).text(),
                    alias=self.table_widget.item(row, 3).text(),
                )
                user_list.append(user)
        self.parent().update_whitelist(user_list)
        self.close()
