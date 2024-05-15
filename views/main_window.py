import sys
from typing import Dict, List
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QFileDialog,
    QLabel,
    QFormLayout,
)

from config import Config
from views.add_whitelist_dialog import AddWhitelistDialog


class MainWindow(QWidget):
    def __init__(
        self,
        config: Config,
        user_list: List[Dict[str, str]],
        on_save_config: callable,
        on_start_watching: callable,
        on_stop_watching: callable,
    ):
        super().__init__()

        self.config = config
        self.on_save_config = on_save_config
        self.user_list = user_list

        self.is_watching = False
        self.on_start_watching = on_start_watching
        self.on_stop_watching = on_stop_watching

        self.setGeometry(300, 300, 600, 300)
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
        self.base_path_input.setText(self.config.base_path)
        self.base_path_input.textChanged.connect(self.set_base_path)

        self.base_path_button = QPushButton("选择路径")
        self.base_path_button.setToolTip("选择要转换的图片文件夹")
        self.base_path_button.clicked.connect(self.choose_folder)

        self.base_path_layout.addWidget(self.base_path_input)
        self.base_path_layout.addWidget(self.base_path_button)
        self.form_layout.addRow(self.base_path_label, self.base_path_layout)

        # 保存路径模板
        self.path_template_label = QLabel("模板:")
        self.path_template_input = QLineEdit()
        self.path_template_input.setText(self.config.path_template)
        self.path_template_input.textChanged.connect(self.set_path_template)
        self.form_layout.addRow(self.path_template_label, self.path_template_input)

        # 日期格式
        self.date_format_label = QLabel("日期格式:")
        self.date_format_input = QLineEdit()
        self.date_format_input.setText(self.config.date_format)
        self.date_format_input.textChanged.connect(self.set_date_format)
        self.form_layout.addRow(self.date_format_label, self.date_format_input)

        # 白名单
        self.whitelist_label = QLabel("白名单:")

        self.whitelist_layout = QVBoxLayout()
        self.whitelist = QListWidget()
        self.whitelist.addItems([str(user) for user in self.config.whitelist])
        self.whitelist.itemDoubleClicked.connect(self.remove_whitelist_item)

        self.add_whitelist_button = QPushButton("添加白名单")
        self.add_whitelist_button.clicked.connect(self.show_add_whitelist_dialog)

        self.whitelist_layout.addWidget(self.whitelist)
        self.whitelist_layout.addWidget(self.add_whitelist_button)
        self.form_layout.addRow(self.whitelist_label, self.whitelist_layout)

        # 保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_config)
        self.form_layout.addWidget(self.save_button)

        # 动作按钮
        self.actions_layout = QHBoxLayout()
        self.status_label = QLabel("状态: 未开始")
        self.start_button = QPushButton("开始监控")
        self.stop_button = QPushButton("停止监控")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_watching)
        self.stop_button.clicked.connect(self.stop_watching)
        self.actions_layout.addWidget(self.status_label)
        self.actions_layout.addWidget(self.start_button)
        self.actions_layout.addWidget(self.stop_button)
        self.form_layout.addRow(self.actions_layout)

        # 设置标签最小宽度
        self.base_path_label.setMinimumWidth(50)
        self.path_template_label.setMinimumWidth(50)
        self.date_format_label.setMinimumWidth(50)
        self.whitelist_label.setMinimumWidth(50)

        self.layout.addLayout(self.form_layout)

    def set_base_path(self, text):
        self.config.base_path = text

    def choose_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "选择文件夹", self.base_path_input.text()
        )
        if folder_path:
            self.set_base_path(folder_path)
            self.base_path_input.setText(folder_path)

    def set_path_template(self, text):
        self.config.path_template = text

    def set_date_format(self, text):
        self.config.date_format = text

    def remove_whitelist_item(self, item):
        self.config.whitelist.remove(self.config.whitelist[self.whitelist.row(item)])
        self.whitelist.takeItem(self.whitelist.row(item))

    def show_add_whitelist_dialog(self):
        dialog = AddWhitelistDialog(self)
        dialog.show()

    def update_whitelist(self, user_list):
        self.config.whitelist = user_list
        self.whitelist.clear()
        self.whitelist.addItems([str(user) for user in user_list])

    def save_config(self):
        self.on_save_config()
        if self.is_watching:
            reply = QMessageBox.question(
                self,
                "提示",
                "监控已启动，是否重启监控？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.restart_watching()
        else:
            QMessageBox.information(self, "提示", "保存成功！")

    def start_watching(self):
        self.on_start_watching()
        self.is_watching = True
        self.status_label.setText("状态: 监控中")
        self.status_label.setStyleSheet("color: green")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_watching(self):
        self.on_stop_watching()
        self.is_watching = False
        self.status_label.setText("状态: 停止监控")
        self.status_label.setStyleSheet("color: red")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def restart_watching(self):
        self.stop_watching()
        self.start_watching()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "提示",
            "确认退出吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.stop_watching()
            event.accept()
        else:
            event.ignore()
