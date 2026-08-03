#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


PRIMARY = "#2563eb"
NAVY = "#12355b"
TEAL = "#0f766e"
BG = "#edf2f7"
CARD = "#ffffff"
TEXT = "#0f172a"
MUTED = "#64748b"
BORDER = "#dbe4ef"


def label(text, size=11, color=TEXT, bold=False):
    item = QLabel(text)
    item.setWordWrap(True)
    item.setStyleSheet(f"color: {color}; background: transparent;")
    font = QFont("Noto Sans CJK SC", size)
    font.setBold(bold)
    item.setFont(font)
    return item


class Card(QFrame):
    def __init__(self, tone="white"):
        super().__init__()
        self.setObjectName("card")
        self.tone = tone


class DeviceMaintenanceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("设备检修App")
        self.resize(430, 720)
        self.setMinimumSize(390, 680)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main.addWidget(scroll, 1)

        page = QWidget()
        page.setObjectName("page")
        scroll.setWidget(page)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        layout.addWidget(self.hero())
        layout.addLayout(self.stats())
        layout.addWidget(self.features())
        layout.addWidget(self.tasks())
        layout.addWidget(self.knowledge())
        layout.addStretch(1)

        nav = QFrame()
        nav.setObjectName("nav")
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(8, 6, 8, 6)
        nav_layout.setSpacing(4)
        for i, name in enumerate(["首页", "检索", "任务", "知识", "我的"]):
            btn = QPushButton(name)
            btn.setObjectName("activeNav" if i == 0 else "navButton")
            btn.setCursor(Qt.PointingHandCursor)
            nav_layout.addWidget(btn)
        main.addWidget(nav)

        self.setStyleSheet(
            f"""
            QWidget#root, QWidget#page {{
                background: {BG};
                font-family: "Noto Sans CJK SC", "Microsoft YaHei";
            }}
            QScrollArea {{
                background: {BG};
                border: none;
            }}
            QFrame#hero {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {NAVY}, stop:0.58 {PRIMARY}, stop:1 {TEAL});
                border-radius: 14px;
            }}
            QFrame#card {{
                background: {CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
            QFrame#nav {{
                background: white;
                border-top: 1px solid {BORDER};
            }}
            QPushButton {{
                border: none;
                border-radius: 8px;
                padding: 9px 8px;
                color: {MUTED};
                background: transparent;
                font-size: 13px;
            }}
            QPushButton#activeNav {{
                color: {PRIMARY};
                background: #eff6ff;
                font-weight: 700;
            }}
            QLineEdit {{
                border: none;
                border-radius: 10px;
                background: white;
                padding: 12px 14px;
                color: {TEXT};
                font-size: 13px;
            }}
            """
        )

    def hero(self):
        hero = QFrame()
        hero.setObjectName("hero")
        layout = QVBoxLayout(hero)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        row = QHBoxLayout()
        mark = QLabel("检")
        mark.setAlignment(Qt.AlignCenter)
        mark.setFixedSize(44, 44)
        mark.setStyleSheet(
            "color:white; background:rgba(255,255,255,0.18); border-radius:12px; font-size:22px; font-weight:900;"
        )
        row.addWidget(mark)
        copy = QVBoxLayout()
        copy.addWidget(label("设备检修智能工作台", 18, "white", True))
        copy.addWidget(label("多模态检索 · 标准作业 · 知识沉淀", 10, "#dbeafe"))
        row.addLayout(copy, 1)
        layout.addLayout(row)

        search = QLineEdit()
        search.setPlaceholderText("输入故障现象、设备型号或检修问题")
        layout.addWidget(search)
        return hero

    def stats(self):
        grid = QGridLayout()
        grid.setSpacing(8)
        data = [("128", "在线设备"), ("8", "待处理"), ("3", "高风险"), ("156", "知识条目")]
        for col, (value, name) in enumerate(data):
            card = Card()
            inner = QVBoxLayout(card)
            inner.setContentsMargins(8, 12, 8, 12)
            inner.setSpacing(6)
            v = label(value, 19, TEXT, True)
            v.setAlignment(Qt.AlignCenter)
            n = label(name, 9, MUTED, True)
            n.setAlignment(Qt.AlignCenter)
            inner.addWidget(v)
            inner.addWidget(n)
            grid.addWidget(card, 0, col)
        return grid

    def features(self):
        box, inner = self.section("核心能力")
        grid = QGridLayout()
        grid.setSpacing(10)
        data = [
            ("智能检索", "按故障现象、图片、型号快速定位维修资料", "#eff6ff"),
            ("检修任务", "跟踪工单状态、风险等级和处理进度", "#ecfdf5"),
            ("知识库", "沉淀标准作业流程、案例和维修手册", "#fffbeb"),
            ("一键问修", "面向一线人员的检修问答入口", "#f8fafc"),
        ]
        for i, (title, desc, color) in enumerate(data):
            card = QFrame()
            card.setStyleSheet(f"background:{color}; border:1px solid {BORDER}; border-radius:10px;")
            c = QVBoxLayout(card)
            c.setContentsMargins(12, 12, 12, 12)
            c.addWidget(label(title, 12, TEXT, True))
            c.addWidget(label(desc, 9, "#475569"))
            grid.addWidget(card, i // 2, i % 2)
        inner.addLayout(grid)
        return box

    def tasks(self):
        box, inner = self.section("今日检修任务", "按风险等级排序，优先处理红色项")
        data = [
            ("发动机基础检修", "发动机总成 · 一号工位", "进行中", PRIMARY),
            ("点火系统复核", "火花塞 / 点火线圈 · 二号工位", "高风险", "#dc2626"),
            ("燃油供给检查", "油路 / 化油器 · 三号工位", "待处理", "#d97706"),
        ]
        for title, meta, state, color in data:
            inner.addWidget(self.row_card(title, meta, state, color))
        return box

    def knowledge(self):
        box, inner = self.section("知识库更新")
        data = [
            ("摩托车发动机维修手册已入库", "覆盖结构说明、故障排查、拆装标准和扭矩规范"),
            ("新增异响故障诊断链路", "关联气门间隙、链条磨损、轴承磨损等排查路径"),
            ("现场案例待审核", "一线人员上传的启动困难处置案例等待归档"),
        ]
        for title, desc in data:
            inner.addWidget(self.row_card(title, desc, "", TEAL))
        return box

    def section(self, title, subtitle=""):
        card = Card()
        inner = QVBoxLayout(card)
        inner.setContentsMargins(14, 14, 14, 14)
        inner.setSpacing(10)
        inner.addWidget(label(title, 14, TEXT, True))
        if subtitle:
            inner.addWidget(label(subtitle, 9, MUTED))
        return card, inner

    def row_card(self, title, meta, state, color):
        row = QFrame()
        row.setStyleSheet(f"background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 10, 10, 10)
        bar = QFrame()
        bar.setFixedSize(5, 42)
        bar.setStyleSheet(f"background:{color}; border-radius:3px;")
        layout.addWidget(bar)
        copy = QVBoxLayout()
        copy.addWidget(label(title, 11, TEXT, True))
        copy.addWidget(label(meta, 9, MUTED))
        layout.addLayout(copy, 1)
        if state:
            badge = QLabel(state)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(
                f"color:{color}; background:white; border:1px solid {color}; border-radius:10px; padding:4px 8px;"
            )
            layout.addWidget(badge)
        return row


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeviceMaintenanceApp()
    window.show()
    sys.exit(app.exec_())
