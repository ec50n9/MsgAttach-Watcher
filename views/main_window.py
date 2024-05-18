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
    QSystemTrayIcon,
    QMenu,
    QCheckBox,
    QTabWidget,
)
from PyQt6.QtGui import QIcon

from config import Config
from utils.auto_run import AutoRun, AutoRun_Is_Open
from utils.excel import save_dict_to_excel
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
        self.setWindowTitle("MsgAttach Aides")
        self.initTary()
        self.setup_ui()

        # 启动监听
        if self.config.start_watching:
            self.start_watching()

    def initTary(self):
        self.tary_icon = QSystemTrayIcon(self)
        self.tary_icon.setToolTip("MsgAttach Watcher")
        self.tary_icon.setIcon(QIcon("assets/icon.png"))
        self.tary_icon.show()

        menu = QMenu()
        self.tary_icon.setContextMenu(menu)

        show_action = menu.addAction("显示主界面")
        show_action.triggered.connect(self.show)
        start_action = menu.addAction("开始监控")
        start_action.triggered.connect(self.start_watching)
        stop_action = menu.addAction("停止监控")
        stop_action.triggered.connect(self.stop_watching)
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(self.close)

        self.tary_icon.activated.connect(self.icon_activated)

    def icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.setup_home_tab()
        self.setup_tools_tab()
        self.tabs.setCurrentIndex(0)

        self.layout.addWidget(self.tabs)

    def setup_home_tab(self):
        # 表单
        self.home_form_layout = QFormLayout()
        self.home_form_layout.setHorizontalSpacing(10)

        # 保存的根路径
        self.base_path_label = QLabel("基础保存路径:")

        self.base_path_layout = QHBoxLayout()

        self.base_path_input = QLineEdit()
        self.base_path_input.setText(self.config.base_path)
        self.base_path_input.textChanged.connect(self.set_base_path)

        self.base_path_button = QPushButton("选择路径")
        self.base_path_button.setToolTip("选择要转换的图片文件夹")
        self.base_path_button.clicked.connect(self.choose_folder)

        self.base_path_layout.addWidget(self.base_path_input)
        self.base_path_layout.addWidget(self.base_path_button)
        self.home_form_layout.addRow(self.base_path_label, self.base_path_layout)

        # 保存路径模板
        self.path_template_label = QLabel("具体文件路径:")
        self.path_template_input = QLineEdit()
        self.path_template_input.setText(self.config.path_template)
        self.path_template_input.textChanged.connect(self.set_path_template)
        self.home_form_layout.addRow(self.path_template_label, self.path_template_input)

        # 日期格式
        self.date_format_label = QLabel("分类日期格式:")
        self.date_format_input = QLineEdit()
        self.date_format_input.setText(self.config.date_format)
        self.date_format_input.textChanged.connect(self.set_date_format)
        self.home_form_layout.addRow(self.date_format_label, self.date_format_input)

        # 白名单
        self.whitelist_label = QLabel("监听白名单:")

        self.whitelist_layout = QVBoxLayout()
        self.whitelist = QListWidget()
        self.whitelist.addItems([str(user) for user in self.config.whitelist])
        self.whitelist.itemDoubleClicked.connect(self.remove_whitelist_item)

        self.add_whitelist_button = QPushButton("添加好友到白名单")
        self.add_whitelist_button.clicked.connect(self.show_add_whitelist_dialog)

        self.whitelist_layout.addWidget(self.whitelist)
        self.whitelist_layout.addWidget(self.add_whitelist_button)
        self.home_form_layout.addRow(self.whitelist_label, self.whitelist_layout)

        # 保存按钮
        self.save_button = QPushButton("保存全部设置")
        self.save_button.clicked.connect(self.save_config)
        self.home_form_layout.addWidget(self.save_button)

        # 实时生效的设置
        self.real_time_layout = QHBoxLayout()
        # 开机自启动
        self.autostart_checkbox = QCheckBox("开机自启动")
        self.autostart_checkbox.setChecked(AutoRun_Is_Open(key_name="MsgAttachWatcher"))
        self.autostart_checkbox.stateChanged.connect(
            lambda: (
                self.enable_autostart()
                if self.autostart_checkbox.isChecked()
                else self.disable_autostart()
            )
        )
        # 默认开始监控
        self.start_watching_checkbox = QCheckBox("默认开始监控")
        self.start_watching_checkbox.setChecked(self.config.start_watching)
        self.start_watching_checkbox.stateChanged.connect(
            lambda: setattr(
                self.config, "start_watching", self.start_watching_checkbox.isChecked()
            )
        )
        # 保存缩略图
        self.save_thumb_checkbox = QCheckBox("保存缩略图")
        self.save_thumb_checkbox.setChecked(self.config.save_thumb)
        self.save_thumb_checkbox.stateChanged.connect(
            lambda: setattr(
                self.config, "save_thumb", self.save_thumb_checkbox.isChecked()
            )
        )

        self.real_time_layout.addWidget(self.autostart_checkbox)
        self.real_time_layout.addWidget(self.start_watching_checkbox)
        self.real_time_layout.addWidget(self.save_thumb_checkbox)
        self.home_form_layout.addRow(self.real_time_layout)

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
        self.home_form_layout.addRow(self.actions_layout)

        # 设置标签最小宽度
        self.base_path_label.setMinimumWidth(50)
        self.path_template_label.setMinimumWidth(50)
        self.date_format_label.setMinimumWidth(50)
        self.whitelist_label.setMinimumWidth(50)

        self.tab_home = QWidget()
        self.tab_home.setLayout(self.home_form_layout)
        self.tabs.addTab(self.tab_home, "设置")

    def setup_tools_tab(self):
        self.tools_layout = QVBoxLayout()

        # 批量导出好友
        self.export_friends_button = QPushButton("导出好友列表")
        self.export_friends_button.clicked.connect(self.export_friends)
        self.tools_layout.addWidget(self.export_friends_button)

        self.tab_tools = QWidget()
        self.tab_tools.setLayout(self.tools_layout)
        self.tabs.addTab(self.tab_tools, "工具")

    def export_friends(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存好友列表", "friends.xlsx", "Excel 文件 (*.xlsx)"
        )
        if not file_path:
            return
        try:
            save_dict_to_excel(self.user_list, file_path)
            # 导出成功提示
            QMessageBox.information(self, "提示", "导出成功！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败：{e}")

    def enable_autostart(self):
        AutoRun(switch="open", key_name="MsgAttachWatcher")
        self.autostart_checkbox.setChecked(AutoRun_Is_Open(key_name="MsgAttachWatcher"))

    def disable_autostart(self):
        AutoRun(switch="close", key_name="MsgAttachWatcher")
        self.autostart_checkbox.setChecked(AutoRun_Is_Open(key_name="MsgAttachWatcher"))

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
        reply = reply = QMessageBox(self)
        reply.setWindowTitle(self.tr("提示"))
        reply.setText(self.tr("选择你的操作："))

        close_btn = reply.addButton(self.tr("退出程序"), QMessageBox.ButtonRole.YesRole)
        minimize_btn = reply.addButton(
            self.tr("最小化界面"), QMessageBox.ButtonRole.NoRole
        )
        reply.setDefaultButton(minimize_btn)

        reply.setIcon(QMessageBox.Icon.Question)
        reply.exec()

        if reply.clickedButton() == close_btn:
            self.stop_watching()
            event.accept()
        elif reply.clickedButton() == minimize_btn:
            event.ignore()
            self.hide()  # 窗口最小化
        else:
            event.ignore()
