# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import psutil
import ctypes
from PyQt5.QtGui import QPainter, QLinearGradient, QColor
import ctypes.wintypes
import win32process
from datetime import datetime, timezone
import pytz
from collections import Counter
import traceback
from cryptography.fernet import Fernet
import json
from PyQt5.QtWidgets import QMessageBox
import socket
import hashlib
from PyQt5 import QtWidgets, QtCore, QtGui
import threading
import time
from PyQt5.QtCore import pyqtSignal, QObject
import copy
import win32con
import win32api
from PyQt5.QtCore import QTimer, QPoint
import multiprocessing

SERVER_HOST = '192.168.2.4'
# SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9001
CHUNK_SIZE = 4096
KEY = b'_9ggcT08_jZZuyxqpQwQY1hoy-tpEHW_m7NMTgjKRl4='
RUN_TYPE = False
data = []  # 全局共享数据列表
data_lock = threading.Lock()  # 全局锁
MAX_LENGTH = 100  # 队列最大长度（防止内存过大）
make_asle_position = {'采购': [], '销售': [], '价格': [], '数量': [], '立即挂单': []}
close_position = {'批量转采': [], '批量转销': [], '单笔转货': []}
batch_position = {'批量价格': [], '确定': [],'取消':[]}
sell_position = {'出仓价格': [], '确认': []}

button_UI = {'采购销售位置': make_asle_position, '批量转位置': close_position, '批量出仓位置': batch_position,
             '出仓位置': sell_position}
older_list = []
# 格式--> 时间 方向 进单价 第几仓
def_run_num = 0


UIA_PATHS = {
    "销售": [
        # {"Name": "OkFarm-only", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"AutomationId": "app", "LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"Name": "销售", "LocalizedControlType": "按钮"},
    ],
    "采购": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"AutomationId": "app", "LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"Name": "采购", "LocalizedControlType": "按钮"},
    ],
    "价格": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"AutomationId": "app", "LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "编辑"},
    ],
    "数量": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"AutomationId": "app", "LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "调节按钮"},
    ],
    "立即挂单": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"AutomationId": "app", "LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"Name": "立即挂单", "LocalizedControlType": "按钮"},
    ],
    "批量转采": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"AutomationId": "app", "LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"Name": "批量转采", "LocalizedControlType": "按钮"},
    ],
    "批量转销": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"AutomationId": "app", "LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"Name": "批量转销", "LocalizedControlType": "按钮"},

    ],
    "单笔转货": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"AutomationId": "app", "LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "表格"},
        {},
        {"Name": "单笔转货", "LocalizedControlType": "项"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"Name": "单笔转货", "LocalizedControlType": "按钮"},
    ],
    "卖出价格": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"LocalizedControlType": "组"},
        {"Name": "dialog", "LocalizedControlType": "对话框"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "调节按钮"},
    ],
    "确认": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"LocalizedControlType": "组"},
        {"Name": "dialog", "LocalizedControlType": "对话框"},
        {"Name": "确认", "LocalizedControlType": "按钮"},
    ],
    "批量卖出价格": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"LocalizedControlType": "组"},
        {"Name": "dialog", "LocalizedControlType": "对话框"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "组"},
        {"LocalizedControlType": "调节按钮"},
    ],
    "确定": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"LocalizedControlType": "组"},
        {"Name": "dialog", "LocalizedControlType": "对话框"},
        {"Name": "确定", "LocalizedControlType": "按钮"},
    ],
    "取消": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "文档"},
        {"LocalizedControlType": "组"},
        {"Name": "dialog", "LocalizedControlType": "对话框"},
        {"LocalizedControlType": "组"},
        {"Name": "取消", "LocalizedControlType": "按钮"},
    ],

}
UIA_PATHS___ = {
    "销售": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "DocumentControl"},
        {"AutomationId": "app", "LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"Name": "销售", "LocalizedControlType": "ButtonControl"},
    ],
    "采购": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "DocumentControl"},
        {"AutomationId": "app", "LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"Name": "采购", "LocalizedControlType": "ButtonControl"},
    ],
    "价格": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "DocumentControl"},
        {"AutomationId": "app", "LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "EditControl"},
    ],
    "数量": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "DocumentControl"},
        {"AutomationId": "app", "LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "EditControl"},
    ],
    "立即挂单": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "DocumentControl"},
        {"AutomationId": "app", "LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"Name": "立即挂单", "LocalizedControlType": "ButtonControl"},
    ],
    "批量转采": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "DocumentControl"},
        {"AutomationId": "app", "LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"Name": "批量转采", "LocalizedControlType": "ButtonControl"},
    ],
    "批量转销": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "DocumentControl"},
        {"AutomationId": "app", "LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"Name": "批量转销", "LocalizedControlType": "ButtonControl"},

    ],
    "单笔转货": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "DocumentControl"},
        {"AutomationId": "app", "LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": ""},
        {},
        {"Name": "单笔转货", "LocalizedControlType": ""},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"Name": "单笔转货", "LocalizedControlType": "ButtonControl"},
    ],
    "卖出价格": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "DocumentControl"},
        {"LocalizedControlType": "GroupControl"},
        {"Name": "dialog", "LocalizedControlType": "CustomControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "SpinnerControl"},
    ],
    "确认": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "DocumentControl"},
        {"LocalizedControlType": "GroupControl"},
        {"Name": "dialog", "LocalizedControlType": "CustomControl"},
        {"Name": "确认", "LocalizedControlType": "ButtonControl"},
    ],
    "批量卖出价格": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "DocumentControl"},
        {"LocalizedControlType": "GroupControl"},
        {"Name": "dialog", "LocalizedControlType": "CustomControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "GroupControl"},
        {"LocalizedControlType": "SpinnerControl"},
    ],
    "确定": [
        # {"Name": "UniAgri", "LocalizedControlType": "窗格"},
        {"Name": "OkFarm-only", "LocalizedControlType": "DocumentControl"},
        {"LocalizedControlType": "GroupControl"},
        {"Name": "dialog", "LocalizedControlType": "CustomControl"},
        {"Name": "确定", "LocalizedControlType": "ButtonControl"},
    ],

}



# 窗口逻辑
class MainFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.setMinimumSize(250, 200)
        self.resize(450, 320)
        # 边框判定宽度
        self._border_size = 10
        self._is_resizing = False
        self._resize_direction = None
        self._press_pos = None
        self._window_rect = None
        self.setMouseTracking(True)  # 全窗口都可以跟踪鼠标
        self.installEventFilter(self)

        # 强制定时刷新鼠标样式
        self._cursor_timer = QTimer(self)
        self._cursor_timer.timeout.connect(self.update_cursor)
        self._cursor_timer.start(20)  # 20ms检查一次

        # UI示例内容
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui.titlebar)
        layout.addWidget(self.ui.centralwidget)
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def get_resize_region(self, pos):
        rect = self.rect()
        x, y, w, h = pos.x(), pos.y(), rect.width(), rect.height()
        edge = self._border_size
        title_bar_height = 38  # 如果你的TitleBar高度是38像素
        # 仅右、底和右下角可以缩放
        if y <= title_bar_height:
            return None
        if x > w - edge and y > h - edge:
            return "bottom_right"
        elif x > w - edge:
            return "right"
        elif y > h - edge:
            return "bottom"
        return None

    # 用于事件过滤器调用
    def custom_mouse_event(self, event):

        pos = event.pos()

        title_bar_height = getattr(self.ui, "titlebar", None)
        if title_bar_height:
            title_bar_height = self.ui.titlebar.height()
        else:
            title_bar_height = 38

        region = self.get_resize_region(pos)
        # print(f"pos: {pos}, region: {region}")
        if region == "right":
            self.setCursor(QtCore.Qt.SizeHorCursor)
        elif region == "bottom":
            self.setCursor(QtCore.Qt.SizeVerCursor)
        elif region == "bottom_right":
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)

        # 按下逻辑
        if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.LeftButton:
            if region:
                self._is_resizing = True
                self._resize_direction = region
                self._press_pos = event.globalPos()
                self._window_rect = self.geometry()
        # 拖动逻辑
        elif event.type() == QtCore.QEvent.MouseMove and self._is_resizing and self._resize_direction:
            delta = event.globalPos() - self._press_pos
            rect = self._window_rect
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            # 对各方向进行拉伸
            if self._resize_direction == "right":
                self.setGeometry(x, y, max(w + delta.x(), self.minimumWidth()), h)
            elif self._resize_direction == "bottom":
                self.setGeometry(x, y, w, max(h + delta.y(), self.minimumHeight()))
            elif self._resize_direction == "left":
                new_x = x + delta.x()
                new_w = w - delta.x()
                if new_w >= self.minimumWidth():
                    self.setGeometry(new_x, y, new_w, h)
            elif self._resize_direction == "top":
                new_y = y + delta.y()
                new_h = h - delta.y()
                if new_h >= self.minimumHeight():
                    self.setGeometry(x, new_y, w, new_h)
            elif self._resize_direction == "top_left":
                new_x = x + delta.x()
                new_w = w - delta.x()
                new_y = y + delta.y()
                new_h = h - delta.y()
                if new_w >= self.minimumWidth() and new_h >= self.minimumHeight():
                    self.setGeometry(new_x, new_y, new_w, new_h)
            elif self._resize_direction == "top_right":
                new_y = y + delta.y()
                new_h = h - delta.y()
                if new_h >= self.minimumHeight():
                    self.setGeometry(x, new_y, max(w + delta.x(), self.minimumWidth()), new_h)
            elif self._resize_direction == "bottom_left":
                new_x = x + delta.x()
                new_w = w - delta.x()
                if new_w >= self.minimumWidth():
                    self.setGeometry(new_x, y, new_w, max(h + delta.y(), self.minimumHeight()))
            elif self._resize_direction == "bottom_right":
                self.setGeometry(x, y, max(w + delta.x(), self.minimumWidth()),
                                 max(h + delta.y(), self.minimumHeight()))

        # 松开逻辑
        elif event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
            self._is_resizing = False
            self._resize_direction = None

    # 事件过滤器，所有控件（包括子控件）上的鼠标事件都能处理
    def eventFilter(self, obj, event):
        if event.type() in (
                QtCore.QEvent.MouseMove,
                QtCore.QEvent.MouseButtonPress,
                QtCore.QEvent.MouseButtonRelease,
        ):
            self.custom_mouse_event(event)
            # 返回False让事件继续分发到控件，其实无所谓了
        return super().eventFilter(obj, event)

    def update_cursor(self):
        # 这块代码在任意鼠标静止时也会执行，能彻底抹掉操作系统自动设置的边框resize样式
        global_pos = QtGui.QCursor.pos()
        local_pos = self.mapFromGlobal(global_pos)
        region = self.get_resize_region(local_pos)
        title_bar_height = getattr(self.ui, "titlebar", None)
        if title_bar_height:
            t_height = self.ui.titlebar.height()
        else:
            t_height = 38
        if local_pos.y() <= t_height:
            self.setCursor(QtCore.Qt.ArrowCursor)
        elif region == "right":
            self.setCursor(QtCore.Qt.SizeHorCursor)
        elif region == "bottom":
            self.setCursor(QtCore.Qt.SizeVerCursor)
        elif region == "bottom_right":
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)


# c窗口通讯？
class SignalBus(QObject):
    update_browser_signal = pyqtSignal(str)


# c窗口渲染？
class TitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._press_pos = None
        self.setFixedHeight(38)
        # self.installEventFilter(self)
        # self.setMouseTracking(True)
        # self._resizing = False
        # self._start_pos = None
        # background: qlineargradient(x1:0, y1: 0, x2: 1, y2: 1, stop: 0  # 6a95cc, stop:1 #6a95cc);
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)  # 可选，确保自绘背景
        self.setStyleSheet("""

            QLabel#titleLabel {
                background: transparent;
                color: #FFFFFF;
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 3px;
            }
            QPushButton {
                border: none;
                color: white;
                font-size: 18px;
                width: 32px;
                height: 32px;
                border-radius: 6px;
                padding: 0;
                background: transparent;
            }
            QPushButton#minBtn:hover {
                background: #6A95CC;
                color: #132666;
            }
            QPushButton#closeBtn {
                background: #3A4D8F;
                color: #fff;
            }
            QPushButton#closeBtn:hover {
                background: #6A95CC;
                color: #132666;
            }
        """)
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.setContentsMargins(12, 0, 8, 0)
        hbox.setSpacing(0)

        # 没有icon、直接标题
        self.title = QtWidgets.QLabel("量化交易-鹰嘴豆")
        self.title.setObjectName("titleLabel")
        self.title.setStyleSheet("background: transparent;")
        hbox.addWidget(self.title)
        hbox.addStretch()

        # 最小化按钮
        self.btn_min = QtWidgets.QPushButton("—")
        self.btn_min.setObjectName("minBtn")
        self.btn_min.setFixedSize(32, 32)
        hbox.addWidget(self.btn_min)
        # 关闭按钮
        self.btn_close = QtWidgets.QPushButton("×")
        self.btn_close.setObjectName("closeBtn")
        self.btn_close.setFixedSize(32, 32)
        hbox.addWidget(self.btn_close)

        self.btn_close.clicked.connect(self._on_close)
        self.btn_min.clicked.connect(self._on_min)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._press_pos = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._press_pos and event.buttons() == QtCore.Qt.LeftButton:
            self.window().move(event.globalPos() - self._press_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._press_pos = None

    def _on_close(self):
        self.window().close()

    def _on_min(self):
        self.window().showMinimized()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 渐变背景
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0, QColor("#1E3A8A"))
        grad.setColorAt(1.0, QColor("#6A95CC"))
        painter.fillRect(self.rect(), grad)
    #
    # def mousePressEvent(self, event):
    #     if self.isNearEdge(event.pos()):
    #         self._resizing = True
    #         self._start_pos = event.pos()
    #
    # def mouseMoveEvent(self, event):
    #     if self._resizing:
    #         dx = event.x() - self._start_pos.x()
    #         dy = event.y() - self._start_pos.y()
    #         self.resize(self.width() + dx, self.height() + dy)
    #         self._start_pos = event.pos()
    #
    # def mouseReleaseEvent(self, event):
    #     self._resizing = False
    #
    # def isNearEdge(self, pos, edge=10):
    #     return (abs(pos.x() - self.width()) < edge and abs(pos.y() - self.height()) < edge)
    #


# 窗口UI
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        MainWindow.resize(350, 280)
        # self.installEventFilter(self)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout.addWidget(self.pushButton_3)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.verticalLayout.addWidget(self.comboBox)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_2.addWidget(self.label_5)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_2.addWidget(self.textBrowser)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        # spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # self.horizontalLayout.addItem(spacerItem)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout.addWidget(self.lineEdit_2)
        # spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # self.horizontalLayout.addItem(spacerItem1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout.addWidget(self.lineEdit_3)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        # MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        signal_bus.update_browser_signal.connect(self.handle_update_browser)

        # QSS全局科技风美化（色卡取色）
        MainWindow.setStyleSheet("""


            QWidget {
                font-size: 13px;
                background: #d8e5ff;
                color: #132666;
                border-radius: 0;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #4d68c7, stop:1 #3A4D8F);
                border: none;
                color: #fff;
                padding: 6px 14px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 15px;
                margin: 2px 0;
                transition: background 0.3s;
            }
            QPushButton:hover {
                background: #132666;
                color: #6A95CC;
            }
            QComboBox {
                border: 1.5px solid #3A4D8F;
                background: #e6efff;
                color: #132666;
                border-radius: 6px;
                padding: 3px 8px;
                font-size: 14px;
            }
            QComboBox QAbstractItemView {
                background: #e6efff;
                color: #132666;
                selection-background-color: #6A95CC;
                selection-color: #132666;
            }
            QLineEdit {
                border: 1.2px solid #3A4D8F;
                border-radius: 6px;
                background-color: #d5e7ff;
                color: #132666;
                padding: 2px 7px;
                font-size: 14px;
            }
            QTextBrowser {
                border: 1.2px solid #3A4D8F;
                border-radius: 7px;
                background: #d5e7ff;
                color: #132666;
                font-size: 15px;
            }
            QLabel {
                color: #3A4D8F;
                font-weight: 500;
            }
            #label_4 {
                color: #132666;
                font-weight: 700;
                font-size: 14px;
                margin-top: 4px;
            }

        """)

        self.titlebar = TitleBar(MainWindow)
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.titlebar)
        layout.addWidget(self.centralwidget)
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        MainWindow.setCentralWidget(container)

        self.load_and_set_settings()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.pushButton.setText(_translate("MainWindow", "初始化"))
        self.pushButton_2.setText(_translate("MainWindow", "开启/停止"))
        self.pushButton_3.setText(_translate("MainWindow", "保存设置"))
        self.comboBox.setItemText(0, _translate("MainWindow", "策略1"))
        self.comboBox.setItemText(1, _translate("MainWindow", "策略2"))
        self.label_5.setText(_translate("MainWindow", "运行输出"))
        self.label.setText(_translate("MainWindow", "一仓"))
        self.label_2.setText(_translate("MainWindow", "二仓"))
        self.label_3.setText(_translate("MainWindow", "三仓"))
        self.label_4.setText(_translate("MainWindow", "市场有风险，投资需谨慎"))
        self.label_4.setStyleSheet("color: #ed4245; font-weight:700; font-size:14px;")
        # 绑定信号和你自己的函数
        self.pushButton.clicked.connect(self.on_init_clicked)
        self.pushButton_2.clicked.connect(self.on_start_clicked)
        self.pushButton_3.clicked.connect(self.on_save_clicked)

    def load_and_set_settings(self):
        vals = load_settings()
        if vals:
            self.lineEdit.setText(vals.get("一仓", ""))
            self.lineEdit_2.setText(vals.get("二仓", ""))
            self.lineEdit_3.setText(vals.get("三仓", ""))
            index = self.comboBox.findText(vals.get("策略", ""), QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.comboBox.setCurrentIndex(index)
            self.textBrowser.clear()
            self.textBrowser.append("已读取设置: " + str(vals))
        else:
            self.textBrowser.clear()
            self.textBrowser.append("读取设置失败或无设置。")

    def on_init_clicked(self):
        print("初始化被点了")
        self.textBrowser.clear()
        self.textBrowser.append("正在初始化...")
        if RUN_TYPE:
            QMessageBox.information(self.pushButton, "提示", "程序已经在运行了，请不用重复启动")
            return
        # 获取行情端
        print('获取行情端')
        target_pid, tamp = find_main()
        print(target_pid, tamp)
        if target_pid == 1:
            QMessageBox.information(self.pushButton, "提示", "未找到行情端进程")
            return
        if target_pid == 2:
            QMessageBox.information(self.pushButton, "提示", "未找到目标窗口标题")
            return
        print('寻找交易端')
        win, tit, hwnd = find_busing()
        if win == 1:
            QMessageBox.information(self.pushButton, "提示", "未找到交易端标题")
            return
        global data
        # 获取服务器数据
        try:
            data_str = request_and_recv()
            data_list = eval(data_str)
            with data_lock:
                for i in data_list:
                    data.append(eval(i))
                data = inin_data(data)
        except:
            traceback.print_exc()
            QMessageBox.information(self.pushButton, "提示", "服务器没有响应")

        print('收到消息验证通过,启动线程')
        thread1 = threading.Thread(
            target=entry_program,
            args=(win, tit),
            daemon=True  # 主线程退出时自动终止
        )
        thread1.start()
        print('入口线程启动')
        thread2 = threading.Thread(
            target=read_program,
            args=(target_pid,),
            daemon=True  # 主线程退出时自动终止
        )
        thread2.start()
        print('抓取线程启动')
        thread3 = threading.Thread(
            target=producer_thread,
            args=(win, hwnd,),
            daemon=True  # 主线程退出时自动终止
        )
        hwnd = get_window_handle('OkFarm-only')
        # thread3 = threading.Thread(
        #     target=aa,
        #     args=(hwnd, UIA_PATHS,),
        #     daemon=True  # 主线程退出时自动终止
        # )
        thread3.start()

        # thread3.start()
        print('扫描线程启动')
        self.textBrowser.clear()
        self.textBrowser.append("初始化完成，请启动开仓")

    def on_start_clicked(self):
        print("启动开仓被点了")
        global RUN_TYPE
        RUN_TYPE = not RUN_TYPE
        # 设置开仓条件

    def on_save_clicked(self):
        # 获取输入框和下拉框的值
        val1 = self.lineEdit.text()
        val2 = self.lineEdit_2.text()
        val3 = self.lineEdit_3.text()
        combo_val = self.comboBox.currentText()
        val_dict = {
            "一仓": val1,
            "二仓": val2,
            "三仓": val3,
            "策略": combo_val
        }
        print('保存')
        save_settings(val_dict)
        self.textBrowser.clear()
        self.textBrowser.append("已保存设置: " + str(val_dict))

    def show_info(self, text, title="提示"):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def handle_update_browser(self, msg):
        self.textBrowser.clear()
        self.textBrowser.append(msg)


# 子进程：一次性扫描并返回结果（UIA 只在子进程里用）
def uia_worker_main(conn, hwnd, paths_dict):
    import uiautomation as auto  # 子进程内导入，避免父子进程状态干扰
    from comtypes import CoInitialize, CoUninitialize
    import win32gui

    # 初始化 COM + UIAutomation
    CoInitialize()
    try:
        with auto.UIAutomationInitializerInThread():
            window = auto.ControlFromHandle(hwnd)
            if not window.Exists(0, 0):
                conn.send(None)
                conn.close()
                return
            left, top, _, _ = win32gui.GetWindowRect(hwnd)
            print()
            # 这里复用你已实现的 DFS 链式查找
            def center_relative(rect):
                return [(rect.left + rect.right) // 2 - left, (rect.top + rect.bottom) // 2 - top]

            result = {}
            for key, path in paths_dict.items():
                ctl = find_by_path_dfs(window, path)
                if ctl:
                    rect = ctl.BoundingRectangle
                    result[key] = center_relative(rect)
                else:
                    result[key] = None

            conn.send(result)
            conn.close()
    except Exception as e:
        try:
            conn.send(None)
            conn.close()
        except:
            pass
    finally:
        CoUninitialize()


# 父进程封装：启动子进程扫描一次，拿到结果后立即退出子进程
def scan_once_in_process(hwnd, paths_dict, timeout=10.0):
    parent_conn, child_conn = multiprocessing.Pipe(duplex=False)
    p = multiprocessing.Process(target=uia_worker_main, args=(child_conn, hwnd, paths_dict), daemon=True)
    p.start()
    positions = None
    try:
        if parent_conn.poll(timeout):
            positions = parent_conn.recv()
    except EOFError:
        positions = None
    finally:
        # 优雅结束子进程
        p.join(timeout=1.0)
        if p.is_alive():
            p.terminate()
            p.join()
    return positions


def update_dict(old, new):
    for key, new_val in new.items():
        # 检查键是否存在旧字典中
        if key not in old:
            continue
        old_val = old[key]
        # 处理嵌套字典的情况
        if isinstance(new_val, dict) and isinstance(old_val, dict):
            update_dict(old_val, new_val)
        # 处理非空列表/元组/数字等有效值
        elif new_val and (isinstance(new_val, list) or isinstance(new_val, tuple)):
            old[key] = new_val
        # 处理非None的有效值（数字、字符串等）
        elif new_val is not None and not (isinstance(new_val, list) and not new_val):
            old[key] = new_val
    return old


# 入口程序
def entry_program(win, tit):
    global data, RUN_TYPE, older_list, button_UI
    # 格式化数据
    N = 1  # 价格通道周期5
    Q = 0  # 震荡验证周期3
    Q1 = 0  # 阈值参数2
    N1 = 1  # 延迟周期3
    # 读取json
    UI_dict = {}
    with open('UI_data.json', 'r', encoding='utf-8') as file:
        UI_dict = json.load(file)
    while True:
        time.sleep(1)
        with data_lock:
            deep_copied = copy.deepcopy(data)
        old = copy.deepcopy(UI_dict)
        new = update_dict(UI_dict, button_UI)
        # print('读取到的UI_dict', old)
        # print('识别到的button_UI', button_UI)
        # print('融合过后new', new)
        # print(new != old)
        # new = copy.deepcopy(UI_dict)
        # update_dict(new, button_UI)
        if new != old:
            print('UI_dict', old)
            print('button_UI', button_UI)
            print('new', new)
            print('数据发生改变')
            with open('UI_data.json', 'w', encoding='utf-8') as file:
                json.dump(new, file, ensure_ascii=False, indent=2)
                file.close()
            print('数据已经跟新')
            signal_bus.update_browser_signal.emit('按钮数据已经更新')
            # input()
            time.sleep(1)
        with open('UI_data.json', 'r', encoding='utf-8') as file:
            UI_dict = json.load(file)
            file.close()
            print('读取到的UI_dict',UI_dict)
        # print('重新读取数据',UI_dict)
        # print(deep_copied[-1])
        # print(deep_copied)
        deep_copied, signals = detect_signals(deep_copied, N, Q, Q1, N1)  # 计算------------
        print('计算完成', signals)
        # print(deep_copied[-1])
        with data_lock:
            data = copy.deepcopy(deep_copied)
        # # print(data)

        msg = '当前K:'
        if deep_copied[-1][1]['o'] == deep_copied[-1][1]['c']:
            msg += '平点'
            # continue
        if deep_copied[-1][1]['o'] > deep_copied[-1][1]['c'] and deep_copied[-1][1]['h'] - deep_copied[-1][1]['l'] == 3:
            msg += '阴K'
            # continue
        elif deep_copied[-1][1]['o'] > deep_copied[-1][1]['c']:
            msg += '阴K平头'
            # continue
        if deep_copied[-1][1]['o'] < deep_copied[-1][1]['c'] and deep_copied[-1][1]['h'] - deep_copied[-1][1]['l'] == 3:
            msg += '阳K'
            # continue
        elif deep_copied[-1][1]['o'] < deep_copied[-1][1]['c']:
            msg += '阳K平头'
        # global
        if RUN_TYPE:
            RUN = "开启中"
        else:
            RUN = "已关闭"

        msg += '\n当前趋势:' + deep_copied[-1][1]['sig']
        msg += '\nCAB:' + str(int(deep_copied[-1][1]['cab'])) + ' BAB:' + str(int(deep_copied[-1][1]['bab']))
        msg += '\n当前价格:' + str(deep_copied[-1][1]['c'])
        msg += '\n开单状态:' + RUN
        with data_lock:
            for i in older_list:
                msg += "\n" + str(i[0]) + " " + str(i[1]) + " " + str(i[2]) + " " + str(i[3])
        # print(msg)
        print(deep_copied[-1])
        signal_bus.update_browser_signal.emit(msg)
        # 开仓部分

        # older_list = []
        # 格式--> 时间 方向 进单价 第几仓

        if RUN_TYPE:
            # 进单部分----

            if deep_copied[-1][1]['sig'] == deep_copied[-2][1]['sig'] == '做多':
                if deep_copied[-1][1]['o'] > deep_copied[-1][1]['c'] > deep_copied[-1][1]['l']:
                    ords = int(deep_copied[-1][1]['c'])
                    vals = load_settings()
                    if not older_list:
                        num = vals['一仓']
                        add_purchase(UI_dict, tit, ords, num)
                        with data_lock:
                            older_list.append([deep_copied[-1][0], '做多', ords, '一仓'])
                        print('已添加列表------', older_list)

                    if ords not in [ordss[2] for ordss in older_list]:
                        if len(older_list) == 1:
                            num = vals['二仓']
                            add_purchase(UI_dict, tit, ords, num)
                            print('已添加列表', older_list)
                            with data_lock:
                                older_list.append([deep_copied[-1][0], '做多', ords, '二仓'])

                    if ords not in [ordss[2] for ordss in older_list]:
                        if len(older_list) == 2:
                            num = vals['三仓']
                            print('已添加列表', older_list)
                            add_purchase(UI_dict, tit, ords, num)
                            with data_lock:
                                older_list.append([deep_copied[-1][0], '做多', ords, '三仓'])

            if deep_copied[-1][1]['sig'] == deep_copied[-2][1]['sig'] == '做空':
                if deep_copied[-1][1]['h'] > deep_copied[-1][1]['c'] > deep_copied[-1][1]['o']:
                    ords = int(deep_copied[-1][1]['c'])
                    vals = load_settings()
                    if not older_list:
                        num = vals['一仓']
                        print('已添加列表', older_list)
                        add_sale(UI_dict, tit, ords, num)
                        with data_lock:
                            older_list.append([deep_copied[-1][0], '做空', ords, '一仓'])

                    if ords not in [ordss[2] for ordss in older_list]:
                        if len(older_list) == 1:
                            num = vals['二仓']
                            print('已添加列表', older_list)
                            add_sale(UI_dict, tit, ords, num)
                            with data_lock:
                                older_list.append([deep_copied[-1][0], '做空', ords, '二仓'])

                    if ords not in [ordss[2] for ordss in older_list]:
                        if len(older_list) == 2:
                            num = vals['三仓']
                            print('已添加列表', older_list)
                            add_sale(UI_dict, tit, ords, num)
                            with data_lock:
                                older_list.append([deep_copied[-1][0], '做空', ords, '三仓'])

            # 出单部分--------
            # 止损出单
            if deep_copied[-3][1]['sig'] == '做多' and deep_copied[-2][1]['sig'] == '做空':
                # 批量转采
                # 获取当前成立价格 因为是新的一根K无论如何，都成立
                # 判断是否还有多单持仓
                with data_lock:
                    has_long = any(i[1] == '做多' for i in older_list)
                if has_long:
                    # if older_list:
                    ords = deep_copied[-1][1]['o']
                    add_batch_purchase(UI_dict, tit, ords)
                    with data_lock:
                        older_list = []
            if deep_copied[-3][1]['sig'] == '做空' and deep_copied[-2][1]['sig'] == '做多':
                # 批量转销
                # 获取当前成立价格 因为是新的一根K无论如何，都成立
                with data_lock:
                    has_long = any(i[1] == '做空' for i in older_list)
                if has_long:
                    # if older_list:
                    ords = deep_copied[-1][1]['o']  #
                    add_batch_sale(UI_dict, tit, ords)
                    with data_lock:
                        older_list = []
            # 止盈出单
            for i in older_list:
                if i[1] == '做多':
                    # 条件 开单价格+2 等于当前k最高价 且 必须是阳k
                    if i[2] + 2 == deep_copied[-1][1]['h'] and deep_copied[-1][1]['o'] < deep_copied[-1][1]['c']:
                        # 价格成立 出单
                        ords = deep_copied[-1][1]['h'] - 1
                        add_sell(UI_dict, tit, ords)
                        with data_lock:
                            older_list.remove(i)
                if i[1] == '做空':
                    # 条件 开单价格-2 等于当前k最低价 且 必须是阴k
                    if i[2] - 2 == deep_copied[-1][1]['l'] and deep_copied[-1][1]['o'] > deep_copied[-1][1]['c']:
                        # 价格成立 出单
                        ords = deep_copied[-1][1]['l'] + 1
                        add_sell(UI_dict, tit, ords)
                        with data_lock:
                            older_list.remove(i)


# 清空输入框
def send_delete_and_backspace(hwnd, count=5):
    VK_DELETE = 0x2E
    VK_BACK = 0x08

    for _ in range(count):
        # 发送 Delete (down + up)
        win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, VK_DELETE, 0)
        win32gui.SendMessage(hwnd, win32con.WM_KEYUP, VK_DELETE, 0)
        time.sleep(0.1)
        # 发送 Backspace (down + up)
        win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, VK_BACK, 0)
        win32gui.SendMessage(hwnd, win32con.WM_KEYUP, VK_BACK, 0)
        time.sleep(0.1)


# 字符转码
def string_to_wmchar(text):
    if not text.isdigit():
        raise ValueError("只允许输入0~9数字字符串")
    return [ord(ch) for ch in text]


# 采购
def add_purchase(UI_dict, tit, ords, num):
    print('采购')
    print('验证')
    print('验证')
    run = False
    with data_lock:
        for i in older_list:
            if ords == i[2]:
                run = True
                print(older_list, ords)
                print('验证失败')
                return
    if run:
        print('验证成功')
    make_asle_position = UI_dict["采购销售位置"]
    hwnd = win32gui.FindWindow(None, tit)
    # print('rect寻找完成', time.time() - t)

    # 获取采购点位

    print(make_asle_position)
    # print('寻找完成',time.time()-t)

    x = int(make_asle_position['采购'][0])
    y = int(make_asle_position['采购'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))

    time.sleep(0.1)
    x = int(make_asle_position['价格'][0])
    y = int(make_asle_position['价格'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))

    send_delete_and_backspace(hwnd)

    for i in string_to_wmchar(str(ords)):
        win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, i, 0)
        win32gui.SendMessage(hwnd, win32con.WM_CHAR, i, 0)
        win32gui.SendMessage(hwnd, win32con.WM_KEYUP, i, 0)

    x = int(make_asle_position['数量'][0])
    y = int(make_asle_position['数量'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))

    send_delete_and_backspace(hwnd)

    for i in string_to_wmchar(str(num)):
        win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, i, 0)
        win32gui.SendMessage(hwnd, win32con.WM_CHAR, i, 0)
        win32gui.SendMessage(hwnd, win32con.WM_KEYUP, i, 0)

    x = int(make_asle_position['立即挂单'][0])
    y = int(make_asle_position['立即挂单'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))


# 销售
def add_sale(UI_dict, tit, ords, num):
    global older_list
    print('销售')
    print('验证')
    run = False
    with data_lock:
        for i in older_list:
            if ords == i[2]:
                run = True
                print(older_list, ords)
                print('验证失败')
                return
    if run:
        print('验证成功')

    make_asle_position = UI_dict["采购销售位置"]
    # with data_lock:
    #     make_asle_position = button_UI['销售销售位置']
    # t = time.time()
    hwnd = win32gui.FindWindow(None, tit)
    # 获取销售点位

    print(make_asle_position)
    # print('寻找完成', time.time() - t)
    x = int(make_asle_position['销售'][0])
    y = int(make_asle_position['销售'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))

    time.sleep(0.1)
    x = int(make_asle_position['价格'][0])
    y = int(make_asle_position['价格'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))

    send_delete_and_backspace(hwnd)

    for i in string_to_wmchar(str(ords)):
        win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, i, 0)
        win32gui.SendMessage(hwnd, win32con.WM_CHAR, i, 0)
        win32gui.SendMessage(hwnd, win32con.WM_KEYUP, i, 0)

    x = int(make_asle_position['数量'][0])
    y = int(make_asle_position['数量'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))

    send_delete_and_backspace(hwnd)

    for i in string_to_wmchar(str(num)):
        win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, i, 0)
        win32gui.SendMessage(hwnd, win32con.WM_CHAR, i, 0)
        win32gui.SendMessage(hwnd, win32con.WM_KEYUP, i, 0)

    x = int(make_asle_position['立即挂单'][0])
    y = int(make_asle_position['立即挂单'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))


# 批量转采
def add_batch_purchase(UI_dict, tit, ords):
    print('批量转采')
    close_position = UI_dict["批量转位置"]
    batch_position = UI_dict["批量出仓位置"]
    # with data_lock:
    #     close_position = button_UI['批量转位置']
    #     batch_position = button_UI['批量出仓位置']
    hwnd = win32gui.FindWindow(None, tit)
    # 获取窗口矩形
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    # 计算尺寸
    width = int((right - left)/2)
    height = int((bottom - top)/2*0.9)
    # 获取平仓 批量转采 批量转销
    # close_position = add_close_position(win, close_position)
    print(close_position)

    x = int(close_position['批量转采'][0])
    y = int(close_position['批量转采'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))
    time.sleep(0.3)

    # 获取批量平仓
    # batch_position = {'价格': [], '确定': []}
    # batch_position = add_batch_position(window, batch_position)
    print(batch_position)

    x = int(batch_position['批量价格'][0])
    y = int(batch_position['批量价格'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))
    send_delete_and_backspace(hwnd)

    for i in string_to_wmchar(str(ords)):
        win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, i, 0)
        win32gui.SendMessage(hwnd, win32con.WM_CHAR, i, 0)
        win32gui.SendMessage(hwnd, win32con.WM_KEYUP, i, 0)

    time.sleep(0.2)

    x = int(batch_position['确定'][0])
    y = int(batch_position['确定'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))

    time.sleep(0.2)
    x = int(batch_position['取消'][0])
    y = int(batch_position['取消'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))


# 批量转销
def add_batch_sale(UI_dict, tit, ords):
    print('批量转销')
    close_position = UI_dict["批量转位置"]
    batch_position = UI_dict["批量出仓位置"]
    # with data_lock:
    #     close_position = button_UI['批量转位置']
    #     batch_position = button_UI['批量出仓位置']
    hwnd = win32gui.FindWindow(None, tit)

    # 获取平仓 批量转采 批量转销
    # close_position = add_close_position(win, close_position)
    print(close_position)
    x = int(close_position['批量转销'][0])
    y = int(close_position['批量转销'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))
    time.sleep(0.3)

    # 获取批量平仓
    # batch_position = {'价格': [], '确定': []}
    # batch_position = add_batch_position(window, batch_position)
    print(batch_position)

    x = int(batch_position['批量价格'][0])
    y = int(batch_position['批量价格'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))
    send_delete_and_backspace(hwnd)

    for i in string_to_wmchar(str(ords)):
        win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, i, 0)
        win32gui.SendMessage(hwnd, win32con.WM_CHAR, i, 0)
        win32gui.SendMessage(hwnd, win32con.WM_KEYUP, i, 0)

    time.sleep(0.2)

    x = int(batch_position['确定'][0])
    y = int(batch_position['确定'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))


    time.sleep(0.2)

    x = int(batch_position['取消'][0])
    y = int(batch_position['取消'][1])
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))



# 出单
def add_sell(UI_dict, tit, ords):
    print('出单')
    close_position = UI_dict["批量转位置"]
    sell_position = UI_dict['出仓位置']
    # with data_lock:
    #     close_position = button_UI['批量转位置']
    #     sell_position = button_UI['出仓位置']
    hwnd = win32gui.FindWindow(None, tit)
    rect = win32gui.GetWindowRect(hwnd)
    left, top, _, _ = rect
    # 获取平仓 批量转采 批量转销
    # sell_position = add_sell_position(win, sell_position)
    print(close_position)
    if '单笔转货' in close_position:

        x = int(close_position['单笔转货'][0])
        y = int(close_position['单笔转货'][1])
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))
        time.sleep(0.3)
        # 获取转让
        # sell_position = {'价格': [], '数量': [], '确认': []}
        # sell_position = add_batch_position(win, sell_position)
        print(sell_position)

        x = int(sell_position['出仓价格'][0])
        y = int(sell_position['出仓价格'][1])
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))
        send_delete_and_backspace(hwnd)

        for i in string_to_wmchar(str(ords)):
            win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, i, 0)
            win32gui.SendMessage(hwnd, win32con.WM_CHAR, i, 0)
            win32gui.SendMessage(hwnd, win32con.WM_KEYUP, i, 0)
        time.sleep(0.2)
        x = int(sell_position['确认'][0])
        y = int(sell_position['确认'][1])
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, None, win32api.MAKELONG(x, y))
        win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(x, y))


# 读取程序
def read_program(target_pid):
    address = 0x0019F3AC
    PROCESS_ALL_ACCESS = 0x1F0FFF
    handle = win32api.OpenProcess(PROCESS_ALL_ACCESS, False, target_pid)
    ord_val = 0
    val = 0
    data_s = ['0', []]
    while True:
        utc_now = datetime.now(timezone.utc)
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_time = utc_now.astimezone(beijing_tz)

        # 格式化为标准字符串
        key = beijing_time.strftime('%H:%M')
        key_s = beijing_time.strftime('%S')
        buffer = ctypes.create_string_buffer(8)
        bytesRead = ctypes.c_size_t(0)
        result = ctypes.windll.kernel32.ReadProcessMemory(
            int(handle),
            ctypes.c_void_p(address),
            buffer,
            8,
            ctypes.byref(bytesRead)
        )
        if result == 0:
            print("读取内存失败，检查权限、位宽、地址是否有效")
        else:
            dbl_val = ctypes.c_double.from_buffer(buffer).value
            try:

                if 100 < dbl_val < 10000:
                    val = int(dbl_val)
                    if val != ord_val:
                        ord_val = val

                        if data_s[0] == key_s:
                            data_s[1].append(ord_val)
                            # print('ord_val??',ord_val)
                            # return data_s, data
                        else:
                            # print('data_s',data_s)
                            count = Counter(data_s[1])
                            sorted_items = sorted(count.items(), key=lambda x: (-x[1], x[0]))
                            list_r = [item for item, freq in sorted_items]
                            result = ord_val
                            result2 = 0
                            result3 = 0
                            result4 = 0
                            if list_r:
                                result = list_r[0]
                            if len(list_r) > 1:
                                result2 = list_r[1]
                            if len(list_r) > 2:
                                result3 = list_r[1]
                            if len(list_r) > 3:
                                result4 = list_r[1]
                            # print(data_s)
                            # print('添加数据', result, result2, result3, result4,list_r,data_s)
                            if val == 0:
                                pass
                            else:
                                # data = add_json(key, val, val2, val3, val4, data)  # 添加
                                # print(result)
                                if result == 0:
                                    print('result为0', data_s)
                                    # with data_lock:
                                    #     result = data[-1][1]['c']
                                    # input('result为0')
                                    # continue
                                if result2 == 0:
                                    result2 = result
                                if result3 == 0:
                                    result3 = result
                                if result4 == 0:
                                    result4 = result
                                with data_lock:
                                    if data[-1][0] == key:
                                        data[-1][1]['c'] = result  # 收盘价
                                        if data[-1][1]['h'] < result:
                                            data[-1][1]['h'] = result
                                        if data[-1][1]['l'] > result:
                                            data[-1][1]['l'] = result

                                        if data[-1][1]['h'] < result2:
                                            data[-1][1]['h'] = result2
                                        if data[-1][1]['l'] > result2:
                                            data[-1][1]['l'] = result2

                                        if data[-1][1]['h'] < result3:
                                            data[-1][1]['h'] = result3
                                        if data[-1][1]['l'] > result3:
                                            data[-1][1]['l'] = result3

                                        if data[-1][1]['h'] < result4:
                                            data[-1][1]['h'] = result4
                                        if data[-1][1]['l'] > result4:
                                            data[-1][1]['l'] = result4
                                    else:
                                        # 添加数据
                                        del data[0]
                                        data.append([key, {'c': result, 'o': result, 'l': result, 'h': result, 'HH': 0,
                                                           'LH': 0, 'H1': 0, 'L1': 0, 'baa': 0, 'bab': 0, 'caa': 0,
                                                           'cab': 0, 'K1': 0, 'K2': 0, 'TMP': 0, 'sig': ''}])
                                        # data, signals = detect_signals(data, N, Q, Q1, N1)  # 计算------------
                            data_s = [key_s, []]
                            # print('数据计算完成',data)
                            # return data_s, data
                        # data_s,data = add_list_S(key,key_s, val, data_s,data)
                        # print('数据变化，当前值是', val, dbl_val, data)

            except:
                traceback.print_exc()
                pass
                print(val)
                print('数据错误')


# 初始化程序
def inin_data(data):
    new_data = []
    print(data)
    for i in data:
        print('i?', i)
        if i[1]['c'] == i[1]['o'] == i[1]['l'] == i[1]['h']:
            continue
        else:
            i[1]['c'] = int(i[1]['c'])
            i[1]['o'] = int(i[1]['o'])
            i[1]['l'] = int(i[1]['l'])
            i[1]['h'] = int(i[1]['h'])
            i[1]['HH'] = 0
            i[1]['LH'] = 0
            i[1]['H1'] = 0
            i[1]['L1'] = 0
            i[1]['baa'] = 0
            i[1]['bab'] = 0
            i[1]['caa'] = 0
            i[1]['cab'] = 0
            i[1]['K1'] = 0
            i[1]['K2'] = 0
            i[1]['TMP'] = 0
            i[1]['sig'] = ''
            new_data.append(i)
    print('数据长度', len(new_data))
    return new_data


# 加密
def encrypt_data(data):
    return Fernet(KEY).encrypt(data.encode())


# 解密
def decrypt_data(token):
    return Fernet(KEY).decrypt(token).decode()


# 保存配置文件
def save_settings(values_dict):
    # 组合为字符串保存
    print('保存1')
    data_str = json.dumps(values_dict)
    print('保存2')
    encrypted = encrypt_data(data_str)
    print('保存3')
    with open("user_settings.bin", "wb") as f:
        print('保存4')
        f.write(encrypted)


# 加载配置文件
def load_settings():
    try:
        with open("user_settings.bin", "rb") as f:
            encrypted = f.read()
        data_str = decrypt_data(encrypted)
        return json.loads(data_str)
    except Exception:
        return None


def get_pid_by_name(process_name):
    for p in psutil.process_iter(['pid', 'name']):
        if p.info['name'] and p.info['name'].lower() == process_name.lower():
            return p.info['pid']
    return None


def get_windows_by_pid(pid):
    titles = []

    def callback(hwnd, extra):
        try:
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                title = win32gui.GetWindowText(hwnd)
                if title:
                    titles.append(title)
        except Exception:
            pass

    win32gui.EnumWindows(callback, None)
    return titles


def find_control_by_automationid_and_name(root_control, automation_id, name=""):
    for child in root_control.GetChildren():
        if child.AutomationId == automation_id and child.Name == name:
            return child
        result = find_control_by_automationid_and_name(child, automation_id, name)
        if result:
            return result
    return None


def find_main():  # 1. 获取 isky.exe 进程PID
    target_pid = get_pid_by_name('isky.exe')
    if not target_pid:
        print("未找到 isky.exe 进程。")
        # exit(1)
        return 1, 2
    print(f'isky.exe 的 PID 是: {hex(target_pid)}')

    # 2. 获取主窗口标题（找带'OkF'关键词的第一个窗口标题）
    window_title = ''
    for t in get_windows_by_pid(target_pid):
        if 'OkF' in t:
            window_title = t
            break
    if not window_title:
        print("未找到目标窗口标题")
        return 2, 2

    print(f'窗口标题: {window_title}{target_pid}')

    return target_pid, window_title


def find_busing():
    # result_hwnds = find_window_by_title('OKFarm-only')
    result_hwnds = find_window_by_title('OkFarm-only')
    if result_hwnds:
        # print(1)
        hwnd = result_hwnds[0]
        tit = win32gui.GetWindowText(hwnd)
        print(f"找到窗口句柄: {hwnd}, 标题: '{win32gui.GetWindowText(hwnd)}'")
        window = auto.ControlFromHandle(hwnd)
        return window, tit, hwnd
    else:
        print("没有找到相关窗口")
        return 1, 0, 0


def find_window_by_title(title_part):
    hwnd_matches = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd) and title_part.lower() in win32gui.GetWindowText(hwnd).lower():
            hwnd_matches.append(hwnd)

    win32gui.EnumWindows(callback, None)
    return hwnd_matches


def dump_controls(control, indent=0):
    global asle_position

    print("*" * indent +
          f"[{control.ControlType}] Name: '{control.Name}', AutomationId: '{control.AutomationId}', Type: {control.LocalizedControlType}, Bounds: {control.BoundingRectangle}")
    for child in control.GetChildren():
        dump_controls(child, indent + 1)


# 临时辅助，用于发现按钮分区从哪个panel递归会快
def dump_panel_tree(control, indent=0, max_depth=3):
    if indent > max_depth:
        return
    print(" " * indent + f"[{control.LocalizedControlType}] '{control.Name}'")
    for child in control.GetChildren():
        dump_panel_tree(child, indent + 1, max_depth)


# 用法
# dump_panel_tree(window)
def scan_control_tree(control, rules, result, max_depth=5, cur_depth=0):
    if cur_depth > max_depth:
        return result
    for rule_fn, key in rules:
        if result[key] is None:
            value = rule_fn(control)
            if value is not None:
                result[key] = value
    if all([v is not None for v in result.values()]):
        return result
    for child in control.GetChildren():
        scan_control_tree(child, rules, result, max_depth, cur_depth + 1)
        if all([v is not None for v in result.values()]):  # 子分支完成后终止
            break
    return result


def producer_thread(win, hwnd):
    global button_UI
    while True:
        try:
            t = time.time()
            positions = scan_once_in_process(hwnd, UIA_PATHS, timeout=30.0)
            if positions is None:
                print('子进程扫描失败或超时')
                print('耗时', time.time() - t)
            else:

                print('扫描结果:', positions)
                print('耗时', time.time() - t)
                if positions['确认'] is None:  # 如果 确认 是空的 卖出价格 抓到的是 批量卖出价格
                    positions['卖出价格'] = None  # 数据不对 过滤
                if positions['确定'] is None:  # 如果 确定 是空的 批量卖出价格 抓到的是 卖出价格
                    positions['批量卖出价格'] = None  # 数据不对 过滤

                # 将 positions 按你之前的结构更新 button_UI
                with data_lock:
                    # 采购/销售/价格/数量/立即挂单
                    make_pos_result = {k: positions.get(k) for k in ["采购", "销售", "价格", "数量", "立即挂单"]}
                    # 批量转采/批量转销/单笔转货
                    batch_pos_result = {k: positions.get(k) for k in ["批量转采", "批量转销", "单笔转货"]}
                    # 平仓（对话框内）价格/数量/确认
                    sell_pos_result = {"出仓价格": positions.get("卖出价格"),
                                       "确认": positions.get("确认")}
                    # 批量平仓价格/确定（对话框）
                    batch_result = {"批量价格": positions.get("批量卖出价格"),
                                    "确定": positions.get("确定"),
                                    "取消": positions.get("取消")}
                    if batch_pos_result['单笔转货'] is None:
                        batch_pos_result['单笔转货'] = []
                    # print('扫描结果:', positions)
                    if make_pos_result.get("采购"):  # 如果不为空
                        button_UI['采购销售位置'] = make_pos_result
                        # print('采购销售位置 已更新')
                    if batch_pos_result.get("批量转采") or batch_pos_result.get("批量转销"):
                        button_UI['批量转位置'] = batch_pos_result
                        # print('批量转位置 已更新')
                    if batch_result.get("确定"):
                        button_UI['批量出仓位置'] = batch_result
                        # print('批量出仓位置 已更新')
                    if sell_pos_result.get("确认"):
                        button_UI['出仓位置'] = sell_pos_result
                        # print('出仓位置 已更新')



        except Exception:
            traceback.print_exc()
        time.sleep(1.0)  # 扫描间隔（可按需调整）


def get_window_handle(title_part):
    hwnds = []

    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and title_part.lower() in win32gui.GetWindowText(hwnd).lower():
            hwnds.append(hwnd)

    win32gui.EnumWindows(cb, None)
    return hwnds[0] if hwnds else None


def get_control_center(rect, left_top=None):
    cx = (rect.left + rect.right) // 2
    cy = (rect.top + rect.bottom) // 2
    if left_top:
        return (cx - left_top[0], cy - left_top[1])
    else:
        return (cx, cy)


# 定义各类规则（lambda控制筛选条件）
def make_asle_rules(left_top):
    return [
        (lambda c: get_control_center(c.BoundingRectangle,
                                      left_top) if c.Name == '采购' and c.LocalizedControlType == '按钮' else None,
         "采购"),
        (lambda c: get_control_center(c.BoundingRectangle,
                                      left_top) if c.Name == '销售' and c.LocalizedControlType == '按钮' else None,
         "销售"),
        (lambda c: get_control_center(c.BoundingRectangle, left_top) if c.LocalizedControlType == '编辑' else None,
         "价格"),
        (lambda c: get_control_center(c.BoundingRectangle, left_top) if c.LocalizedControlType == '调节按钮' else None,
         "数量"),
        (lambda c: get_control_center(c.BoundingRectangle,
                                      left_top) if c.Name == '立即挂单' and c.LocalizedControlType == '按钮' else None,
         "立即挂单"),
    ]


def close_batch_rules(left_top):
    return [
        (lambda c: get_control_center(c.BoundingRectangle,
                                      left_top) if c.Name == '批量转采' and c.LocalizedControlType == '按钮' else None,
         "批量转采"),
        (lambda c: get_control_center(c.BoundingRectangle,
                                      left_top) if c.Name == '批量转销' and c.LocalizedControlType == '按钮' else None,
         "批量转销"),
        (lambda c: get_control_center(c.BoundingRectangle,
                                      left_top) if c.Name == '单笔转货' and c.LocalizedControlType == '按钮' else None,
         "单笔转货"),
    ]


def sell_rules(left_top):
    return [
        (lambda c: get_control_center(c.BoundingRectangle, left_top) if c.LocalizedControlType == '调节按钮' else None,
         "价格"),
        (lambda c: get_control_center(c.BoundingRectangle, left_top) if c.LocalizedControlType == '调节按钮' else None,
         "数量"),
        (lambda c: get_control_center(c.BoundingRectangle,
                                      left_top) if c.Name == '确认' and c.ControlType == 50000 else None, "确认"),
    ]


import win32gui
import uiautomation as auto


def find_by_path_dfs(control, path, level=0, log_prefix=""):
    """
    支持多兄弟节点属性相同的DFS链式查找，并打印调试信息。
    """
    indent = "  " * level
    if not path:
        # print(f"{indent}✔️  完整链Path到达终点，找到控件: Name='{control.Name}' Type='{control.LocalizedControlType}'")
        return control
    layer = path[0]
    # print(f"{indent}进入层级 {level} @ Name='{control.Name}' Type='{control.LocalizedControlType}'，要求: {layer}")
    children = control.GetChildren()
    found_any = False
    for idx, child in enumerate(children):
        ok = True
        miss_attrs = []
        for k, v in layer.items():
            if v != "" and getattr(child, k, None) != v:
                ok = False
                miss_attrs.append((k, getattr(child, k, None), v))
        if ok:
            # print(f"{indent}  [{idx}] 匹配: Name='{child.Name}', Type='{child.LocalizedControlType}' (将递归下一级)")
            found_any = True
            res = find_by_path_dfs(child, path[1:], level + 1)
            if res is not None:
                return res
        else:
            if len(layer) > 0 and set(miss_attrs) != set(layer.items()):
                pass
                # print(f"{indent}  [{idx}] 不匹配: Name='{child.Name}', Type='{child.LocalizedControlType}', 差异:{miss_attrs}")
    if not found_any:
        pass
        # print(f"{indent}!! 本层没有任何子节点满足要求: {layer}")
    return None


def aa(hwnd, UIA_PATHS):
    t = time.time()
    positions = batch_grab_positions(hwnd, UIA_PATHS)
    print('扫描完成', time.time() - t)
    print(positions)


def center_relative(rect, left_top):
    return ((rect.left + rect.right) // 2 - left_top[0], (rect.top + rect.bottom) // 2 - left_top[1])


def batch_grab_positions(hwnd, paths_dict):
    window = auto.ControlFromHandle(hwnd)
    left, top, _, _ = win32gui.GetWindowRect(hwnd)
    result = {}
    for key, path in paths_dict.items():
        ctl = find_by_path_dfs(window, path)
        if ctl:
            result[key] = center_relative(ctl.BoundingRectangle, (left, top))
        else:
            result[key] = None
    return result


def batch_rules(left_top):
    pattern = [50025, 50026, 50026, 50016]

    def match_batch_price(control):
        if control.ControlType == 50016:
            # 控件链判断略去细节
            return get_control_center(control.BoundingRectangle, left_top)
        return None

    return [
        (match_batch_price, "价格"),
        (lambda c: get_control_center(c.BoundingRectangle, left_top) if c.Name == '确定' else None, "确定"),
    ]


def find_main_panel(control):
    # 遍历所有子孙节点，找到满足属性的
    for child in control.GetChildren():
        if child.Name == "OkFarm-only":  # 你目标名字
            return child
        res = find_main_panel(child)
        if res:
            return res
    return None


def get_controltype_chain(control):
    chain = []
    while control:
        chain.insert(0, control.ControlType)
        control = control.GetParentControl()
    return chain


def hhv(data, period):
    """计算最高价N周期最高值"""
    if len(data) < period:
        return max(data)
    return max(data[-period:])


def llv(data, period):
    """计算最低价N周期最低值"""
    if len(data) < period:
        return min(data)
    return min(data[-period:])


def barslast(condition_list):
    """计算最近一次条件成立的位置"""
    for i in range(len(condition_list) - 1, -1, -1):
        if condition_list[i]:
            return len(condition_list) - i - 1
    return float('inf')


def detect_signals(deep_copied, N, Q, Q1, N1):
    """
     包含时间戳和OHLC的列表，每个元素为[timestamp, {'c': '收盘价', 'o': '开盘价', 'l': '最低价', 'h': '最高价'}]
    N: 计算HH/LH的周期
    Q: 计算HHV(OPEN,Q)的周期
    Q1: 阈值参数
    N1: REF延迟周期
    """

    HH = [a[1]["HH"] for a in deep_copied]
    LH = [a[1]["LH"] for a in deep_copied]
    H1 = [a[1]["H1"] for a in deep_copied]
    L1 = [a[1]["L1"] for a in deep_copied]
    baa = [a[1]["baa"] for a in deep_copied]
    bab = [a[1]["bab"] for a in deep_copied]
    caa = [a[1]["caa"] for a in deep_copied]
    cab = [a[1]["cab"] for a in deep_copied]
    K1 = [a[1]["K1"] for a in deep_copied]
    K2 = [a[1]["K2"] for a in deep_copied]
    TMP = [a[1]["TMP"] for a in deep_copied]
    signals = []
    # 提取OHLC数据
    timestamps = [d[0] for d in deep_copied]
    opens = [float(d[1]['o']) for d in deep_copied]
    highs = [float(d[1]['h']) for d in deep_copied]
    lows = [float(d[1]['l']) for d in deep_copied]
    closes = [float(d[1]['c']) for d in deep_copied]
    # 正向遍历数据
    for i in range(len(deep_copied)):
        # 计算HH和LH
        if i >= N - 1:
            HH[i] = hhv(highs[:i + 1], N)  # N周期最高价
            LH[i] = llv(lows[:i + 1], N)  # N周期最低价

        # 计算H1和L1的条件
        if i >= 1 and i >= N:
            # H1条件
            cond_h1 = (
                    HH[i] < HH[i - 1] and
                    LH[i] < LH[i - 1] and
                    opens[i - 1] > closes[i - 1] and  # 前一日阴线
                    opens[i] > closes[i] and  # 当日阴线
                    (hhv(opens[:i + 1], Q) - closes[i]) > Q1
            )
            H1[i] = highs[i - N1] if cond_h1 else 0

            # L1条件
            cond_l1 = (
                    LH[i] > LH[i - 1] and
                    HH[i] > HH[i - 1] and
                    opens[i - 1] < closes[i - 1] and  # 前一日阳线
                    opens[i] < closes[i] and  # 当日阳线
                    (closes[i] - llv(opens[:i + 1], Q)) > Q1
            )
            L1[i] = lows[i - N1] if cond_l1 else 0

        # 计算baa/bab和caa/cab
        if i >= 1:
            # 计算H1信号的上一次位置
            baa[i] = barslast(H1[:i + 1])  # 上一次H1成立的位置
            if baa[i] < float('inf') and i - baa[i] >= 0:
                bab[i] = H1[i - baa[i]]  # 对应位置的H1值

            # 计算L1信号的上一次位置
            caa[i] = barslast(L1[:i + 1])  # 上一次L1成立的位置
            if caa[i] < float('inf') and i - caa[i] >= 0:
                cab[i] = L1[i - caa[i]]  # 对应位置的L1值

        # 计算K1和K2
        if i >= 1:
            if bab[i] != 0 and closes[i] > bab[i]:
                K1[i] = -3
            elif cab[i] != 0 and closes[i] < cab[i]:
                K1[i] = 1
            else:
                K1[i] = 0

            # K2逻辑：如果K1非零则取K1，否则取上一次非零值
            if K1[i] != 0:
                K2[i] = K1[i]
            else:
                last_nonzero = None
                for j in range(i - 1, -1, -1):
                    if K1[j] != 0:
                        last_nonzero = j
                        break
                K2[i] = K1[last_nonzero] if last_nonzero is not None else 0

        TMP[i] = K2[i]
        # 检测信号
        sig = ""
        if i >= 1:
            # TMP上穿0（做多信号）
            if TMP[i - 1] < 0 and TMP[i] > 0:
                signals.append('做空')
                sig = "做空"
                print('根据算法获取的趋势----------')
                deep_copied[i][1]["sig"] = sig
                # print("做空", deep_copied[i][1])

                with open('方向', 'w', encoding='utf-8') as f:
                    f.write("做空\n")
            # TMP下穿0（做空信号）
            elif TMP[i - 1] > 0 and TMP[i] < 0:
                signals.append('做多')
                sig = "做多"
                deep_copied[i][1]["sig"] = sig
                print('根据算法获取的趋势-------')
                # print("做多", deep_copied[i][1])

                with open('方向', 'w', encoding='utf-8') as f:
                    f.write("做多\n")
        # a = {"HH":HH[i],"LH":LH[i],"H1":H1[i],"L1":L1[i],"baa":baa[i],"bab":bab[i],"caa":caa[i],"cab":cab[i],"K1":K1[i],"K2":K2[i],"TMP":TMP[i],"sig":sig}
        deep_copied[i][1]["HH"] = HH[i]
        deep_copied[i][1]["LH"] = LH[i]
        deep_copied[i][1]["H1"] = H1[i]
        deep_copied[i][1]["L1"] = L1[i]
        deep_copied[i][1]["baa"] = baa[i]
        deep_copied[i][1]["bab"] = bab[i]
        deep_copied[i][1]["caa"] = caa[i]
        deep_copied[i][1]["cab"] = cab[i]
        deep_copied[i][1]["K1"] = K1[i]
        deep_copied[i][1]["K2"] = K2[i]
        deep_copied[i][1]["TMP"] = TMP[i]
        if sig == '' and i > 0:  # 优先获取上一个的趋势
            sig = deep_copied[i - 1][1]["sig"]
            # print('优先获取上一个的趋势')
        # if sig == '':
        #     #谁先出来听谁的
        #     if deep_copied[i][1]['cab'] != 0 and deep_copied[i][1]['cab'] <= deep_copied[i][1]["c"]:
        #         sig = '做多'
        #         # print('根据cab趋势')
        #     elif deep_copied[i][1]['bab'] != 0 and deep_copied[i][1]['bab'] >= deep_copied[i][1]["c"]:
        #         sig = '做空'
        # print('根据bab趋势')

        # print('sig为空取上一个',deep_copied[i-1][1]["sig"])

        deep_copied[i][1]["sig"] = sig
        if deep_copied[i][1]["sig"] == '做空':
            if deep_copied[i][1]["bab"] < deep_copied[i][1]["o"]:
                print('数据越界')
                deep_copied[i][1]["sig"] = '做多'
        if deep_copied[i][1]["sig"] == '做多':
            if deep_copied[i][1]["cab"] > deep_copied[i][1]["o"]:
                print('数据越界')
                deep_copied[i][1]["sig"] = '做空'
        # if deep_copied[i][1]["sig"] == '做多':
        # if
        # print('保存后数据',deep_copied[i][1]["sig"] )
    # print('计算完成')
    # for i in deep_copied:
    #     print(i)
    # input('暂停')
    return deep_copied, signals


def request_and_recv():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_HOST, SERVER_PORT))

    s.sendall(b'GET_LONG_DATA')
    chunks = {}
    total_chunks = None
    expected_hash = None
    while True:
        # 先接收头
        header = b''
        while not header.endswith(b'\n'):
            header += s.recv(1)
        # 解包头
        print('header:', header)
        idx, total, length, is_last, chunk_hash = header[:-1].decode().split("|")
        idx = int(idx)
        total = int(total)
        length = int(length)
        is_last = int(is_last)
        if expected_hash is None:
            expected_hash = chunk_hash
            total_chunks = total
        # 收chunk
        chunk = b""
        while len(chunk) < length:
            part = s.recv(length - len(chunk))
            if not part:
                break
            chunk += part
        chunks[idx] = chunk
        print(f"收到第{idx + 1}/{total}个分片")
        if is_last:
            break
    # 拼数据&校验
    data = b"".join([chunks[i] for i in range(total_chunks)])
    data_str = data.decode()
    local_hash = hashlib.sha256(data_str.encode()).hexdigest()
    if local_hash == expected_hash:
        print("数据校验成功！全部数据长度：", len(data_str))
        s.sendall(b"OK")
    else:
        print("数据校验失败！")
        s.sendall(b"FAIL")
    s.close()

    return data_str


if __name__ == "__main__":

    multiprocessing.freeze_support()
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        # 已经设置过则忽略
        pass

    app = QApplication(sys.argv)
    signal_bus = SignalBus()
    frame = MainFrame()
    frame.show()
    sys.exit(app.exec_())



