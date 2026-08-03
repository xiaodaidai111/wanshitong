#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


PRIMARY = "#2563eb"
BG = "#f4f7fb"
CARD = "#ffffff"
TEXT = "#172033"
MUTED = "#64748b"


class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.NoFrame)


def label(text, size=11, color=TEXT, bold=False):
    item = QLabel(text)
    item.setWordWrap(True)
    item.setStyleSheet(f"color: {color};")
    font = QFont("Noto Sans CJK SC", size)
    font.setBold(bold)
    item.setFont(font)
    return item


class MaintenanceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("设备检修知识作业系统")
        self.resize(430, 760)
        self.setMinimumSize(390, 680)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(22, 16, 22, 14)
        header_layout.addWidget(label("设备检修知识作业系统", 17, "white", True))
        header_layout.addWidget(label("多模态检索 · 标准作业 · 智能问修", 10, "#dbeafe"))
        layout.addWidget(header)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)
        self.pages = [
            self.home_page(),
            self.task_page(),
            self.knowledge_page(),
            self.qa_page(),
            self.mine_page(),
        ]
        for page in self.pages:
            self.stack.addWidget(page)

        nav = QFrame()
        nav.setObjectName("nav")
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(6, 5, 6, 5)
        nav_layout.setSpacing(4)
        self.nav_buttons = []
        for i, name in enumerate(["首页", "任务", "知识库", "问修", "我的"]):
            btn = QPushButton(name)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, index=i: self.switch_page(index))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        layout.addWidget(nav)
        self.switch_page(0)

        self.setStyleSheet(
            f"""
            QMainWindow, QWidget {{ background: {BG}; font-family: "Noto Sans CJK SC"; }}
            #header {{ background: {PRIMARY}; }}
            #nav {{ background: white; border-top: 1px solid #e2e8f0; }}
            QPushButton {{
                border: none;
                border-radius: 6px;
                padding: 8px 10px;
                color: {MUTED};
                background: transparent;
            }}
            QPushButton#activeNav {{ color: {PRIMARY}; font-weight: 700; background: #eff6ff; }}
            QPushButton#primary {{
                background: {PRIMARY};
                color: white;
                font-weight: 700;
                padding: 10px 14px;
            }}
            QFrame#card {{
                background: {CARD};
                border: 1px solid #e5edf7;
                border-radius: 8px;
            }}
            QLineEdit {{
                border: none;
                border-radius: 7px;
                background: #eef2ff;
                padding: 11px 12px;
                color: {TEXT};
            }}
            QListWidget {{
                background: transparent;
                border: none;
            }}
            QListWidget::item {{
                background: white;
                border: 1px solid #e5edf7;
                border-radius: 8px;
                margin: 5px 0;
                padding: 12px;
                color: {TEXT};
            }}
            """
        )

    def page_root(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        return page, layout

    def add_card(self, layout):
        card = Card()
        inner = QVBoxLayout(card)
        inner.setContentsMargins(14, 12, 14, 12)
        inner.setSpacing(7)
        layout.addWidget(card)
        return inner

    def home_page(self):
        page, layout = self.page_root()
        search_card = self.add_card(layout)
        row = QHBoxLayout()
        entry = QLineEdit("搜索设备型号、故障现象、检修手册...")
        btn = QPushButton("检索")
        btn.setObjectName("primary")
        row.addWidget(entry, 1)
        row.addWidget(btn)
        search_card.addLayout(row)

        banner = self.add_card(layout)
        banner.addWidget(label("标准化检修作业指引", 15, TEXT, True))
        banner.addWidget(label("点火系统、燃油供给、机油润滑、异响排查", 10, MUTED))

        grid_card = self.add_card(layout)
        grid = QGridLayout()
        for idx, title in enumerate(["智能检索", "检修任务", "知识库", "智能问修"]):
            tile = QLabel(title)
            tile.setAlignment(Qt.AlignCenter)
            tile.setStyleSheet("background:#f8fafc;border-radius:8px;padding:18px 6px;color:#172033;font-weight:700;")
            grid.addWidget(tile, idx // 2, idx % 2)
        grid_card.addLayout(grid)

        stats = self.add_card(layout)
        stats.addWidget(label("系统概览", 14, TEXT, True))
        for text in ["今日任务 8 项    高风险 3 项", "知识条目 128 条    待审核 12 条", "闭环率 85%        平均响应 3 分钟"]:
            stats.addWidget(label(text, 10, MUTED))
        layout.addStretch(1)
        return page

    def task_page(self):
        page, layout = self.page_root()
        top = self.add_card(layout)
        top.addWidget(label("任务闭环率 85%", 17, PRIMARY, True))
        top.addWidget(label("实时统计任务达成、风险与超时状态", 10, MUTED))
        tasks = QListWidget()
        for title in [
            "高风险 · 发动机怠速抖动排查\n建议先检查火花塞间隙与喷油嘴积碳状态",
            "进行中 · 制动系统异响复核\n按标准作业流程完成轮端与制动盘检查",
            "待处理 · 冷却液异常消耗\n上传现场图片后生成检修建议",
        ]:
            QListWidgetItem(title, tasks)
        layout.addWidget(tasks, 1)
        return page

    def knowledge_page(self):
        page, layout = self.page_root()
        intro = self.add_card(layout)
        intro.addWidget(label("知识库检索", 15, TEXT, True))
        intro.addWidget(label("按设备、故障现象、流程、手册章节或案例快速定位", 10, MUTED))
        items = QListWidget()
        for title in [
            "点火系统标准检修流程\n发动机 / 标准作业",
            "燃油供给异常诊断案例\n案例 / 故障树",
            "机油润滑系统检查规范\n手册 / 安全要求",
            "传感器信号异常处理\n电控 / 风险提示",
        ]:
            QListWidgetItem(title, items)
        layout.addWidget(items, 1)
        return page

    def qa_page(self):
        page, layout = self.page_root()
        card = self.add_card(layout)
        card.addWidget(label("智能问修", 16, TEXT, True))
        card.addWidget(label("输入现场现象，系统给出排查路径、风险提醒和手册依据。", 10, MUTED))
        entry = QLineEdit("发动机热车后怠速不稳，伴随轻微异响")
        card.addWidget(entry)
        btn = QPushButton("生成检修建议")
        btn.setObjectName("primary")
        card.addWidget(btn)
        result = self.add_card(layout)
        result.addWidget(label("建议排查路径", 13, TEXT, True))
        for text in ["1. 读取故障码并记录冻结帧", "2. 检查进气管路是否漏气", "3. 测量火花塞间隙并查看积碳", "4. 对喷油嘴进行雾化状态复核"]:
            result.addWidget(label(text, 10, MUTED))
        layout.addStretch(1)
        return page

    def mine_page(self):
        page, layout = self.page_root()
        profile = self.add_card(layout)
        profile.addWidget(label("演示账号", 16, TEXT, True))
        profile.addWidget(label("检修工程师 · 现场作业组", 10, MUTED))
        data = self.add_card(layout)
        data.addWidget(label("演示数据", 13, TEXT, True))
        for text in ["累计检修任务：46", "本周知识沉淀：9", "高风险闭环：100%", "离线资料包：已同步"]:
            data.addWidget(label(text, 10, MUTED))
        layout.addStretch(1)
        return page

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setObjectName("activeNav" if i == index else "")
            btn.style().unpolish(btn)
            btn.style().polish(btn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("设备检修知识作业系统")
    win = MaintenanceWindow()
    win.show()
    sys.exit(app.exec_())
