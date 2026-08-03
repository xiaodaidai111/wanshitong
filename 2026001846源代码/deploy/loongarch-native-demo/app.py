#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk


APP_TITLE = "设备检修知识作业系统"
PRIMARY = "#2563eb"
BG = "#f4f7fb"
CARD = "#ffffff"
TEXT = "#172033"
MUTED = "#64748b"


class NativeMaintenanceDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("390x720")
        self.minsize(360, 640)
        self.configure(bg=BG)
        self.active_page = "home"
        self._setup_style()
        self._build_shell()
        self.show_page("home")

    def _setup_style(self):
        self.option_add("*Font", ("Noto Sans CJK SC", 11))
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD, relief="flat")
        style.configure("Title.TLabel", background=CARD, foreground=TEXT, font=("Noto Sans CJK SC", 16, "bold"))
        style.configure("Sub.TLabel", background=CARD, foreground=MUTED, font=("Noto Sans CJK SC", 10))
        style.configure("Body.TLabel", background=CARD, foreground=TEXT, font=("Noto Sans CJK SC", 11))
        style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Noto Sans CJK SC", 10))
        style.configure("Accent.TButton", background=PRIMARY, foreground="white", borderwidth=0, padding=(12, 8))

    def _build_shell(self):
        self.header = tk.Frame(self, bg=PRIMARY, height=84)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        tk.Label(
            self.header,
            text="设备检修知识作业系统",
            bg=PRIMARY,
            fg="white",
            font=("Noto Sans CJK SC", 17, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 2))
        tk.Label(
            self.header,
            text="多模态检索 · 标准作业 · 智能问修",
            bg=PRIMARY,
            fg="#dbeafe",
            font=("Noto Sans CJK SC", 10),
        ).pack(anchor="w", padx=20)

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(fill="both", expand=True)

        self.nav = tk.Frame(self, bg="white", height=58)
        self.nav.pack(fill="x")
        self.nav.pack_propagate(False)

        self.nav_buttons = {}
        for key, label in [
            ("home", "首页"),
            ("tasks", "任务"),
            ("knowledge", "知识库"),
            ("qa", "问修"),
            ("me", "我的"),
        ]:
            btn = tk.Button(
                self.nav,
                text=label,
                bd=0,
                relief="flat",
                cursor="hand2",
                command=lambda name=key: self.show_page(name),
            )
            btn.pack(side="left", fill="both", expand=True)
            self.nav_buttons[key] = btn

    def show_page(self, page):
        self.active_page = page
        for child in self.content.winfo_children():
            child.destroy()

        for key, btn in self.nav_buttons.items():
            btn.configure(
                bg="white",
                fg=PRIMARY if key == page else MUTED,
                font=("Noto Sans CJK SC", 11, "bold" if key == page else "normal"),
            )

        if page == "home":
            self._home()
        elif page == "tasks":
            self._tasks()
        elif page == "knowledge":
            self._knowledge()
        elif page == "qa":
            self._qa()
        else:
            self._me()

    def _scroll_page(self):
        canvas = tk.Canvas(self.content, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=370)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return inner

    def _card(self, parent, pady=8):
        frame = tk.Frame(parent, bg=CARD, padx=14, pady=12)
        frame.pack(fill="x", padx=14, pady=pady)
        return frame

    def _label(self, parent, text, size=11, color=TEXT, bold=False, bg=CARD):
        label = tk.Label(
            parent,
            text=text,
            bg=bg,
            fg=color,
            font=("Noto Sans CJK SC", size, "bold" if bold else "normal"),
            anchor="w",
            justify="left",
            wraplength=330,
        )
        label.pack(anchor="w", fill="x")
        return label

    def _home(self):
        page = self._scroll_page()
        search = self._card(page, pady=(14, 8))
        row = tk.Frame(search, bg=CARD)
        row.pack(fill="x")
        entry = tk.Entry(row, relief="flat", bg="#eef2ff", fg=TEXT)
        entry.insert(0, "搜索设备型号、故障现象、检修手册...")
        entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        tk.Button(row, text="检索", bg=PRIMARY, fg="white", bd=0, padx=14, command=lambda: self.show_page("knowledge")).pack(side="right")

        banner = self._card(page)
        self._label(banner, "标准化检修作业指引", 15, TEXT, True)
        self._label(banner, "点火系统、燃油供给、机油润滑、异响排查", 10, MUTED)

        quick = tk.Frame(page, bg=BG)
        quick.pack(fill="x", padx=14, pady=8)
        for title in ["智能检索", "检修任务", "知识库", "智能问修"]:
            box = tk.Frame(quick, bg=CARD, padx=8, pady=10)
            box.pack(side="left", expand=True, fill="x", padx=3)
            tk.Label(box, text=title, bg=CARD, fg=TEXT, font=("Noto Sans CJK SC", 10, "bold")).pack()

        stats = self._card(page)
        self._label(stats, "系统概览", 14, TEXT, True)
        for line in ["今日任务 8 项    高风险 3 项", "知识条目 128 条    待审核 12 条", "闭环率 85%        平均响应 3 分钟"]:
            self._label(stats, line, 10, MUTED)

    def _tasks(self):
        page = self._scroll_page()
        top = self._card(page, pady=(14, 8))
        self._label(top, "任务闭环率 85%", 17, PRIMARY, True)
        self._label(top, "实时统计任务达成、风险与超时状态", 10, MUTED)

        for status, title, desc in [
            ("高风险", "发动机怠速抖动排查", "建议先检查火花塞间隙与喷油嘴积碳状态"),
            ("进行中", "制动系统异响复核", "按标准作业流程完成轮端与制动盘检查"),
            ("待处理", "冷却液异常消耗", "上传现场图片后生成检修建议"),
        ]:
            card = self._card(page)
            self._label(card, f"{status} · {title}", 13, TEXT, True)
            self._label(card, desc, 10, MUTED)

    def _knowledge(self):
        page = self._scroll_page()
        search = self._card(page, pady=(14, 8))
        self._label(search, "知识库检索", 14, TEXT, True)
        self._label(search, "按设备、故障现象、流程、手册章节或案例快速定位", 10, MUTED)

        for title, tag in [
            ("点火系统标准检修流程", "发动机 / 标准作业"),
            ("燃油供给异常诊断案例", "案例 / 故障树"),
            ("机油润滑系统检查规范", "手册 / 安全要求"),
            ("传感器信号异常处理", "电控 / 风险提示"),
        ]:
            card = self._card(page)
            self._label(card, title, 13, TEXT, True)
            self._label(card, tag, 10, MUTED)

    def _qa(self):
        page = self._scroll_page()
        card = self._card(page, pady=(14, 8))
        self._label(card, "智能问修", 16, TEXT, True)
        self._label(card, "输入现场现象，系统给出排查路径、风险提醒和手册依据。", 10, MUTED)
        text = tk.Text(card, height=5, bg="#f8fafc", fg=TEXT, bd=0, wrap="word")
        text.insert("1.0", "示例：发动机热车后怠速不稳，伴随轻微异响")
        text.pack(fill="x", pady=10)
        tk.Button(card, text="生成检修建议", bg=PRIMARY, fg="white", bd=0, pady=8).pack(fill="x")

        result = self._card(page)
        self._label(result, "建议排查路径", 13, TEXT, True)
        for line in ["1. 读取故障码并记录冻结帧", "2. 检查进气管路是否漏气", "3. 测量火花塞间隙并查看积碳", "4. 对喷油嘴进行雾化状态复核"]:
            self._label(result, line, 10, MUTED)

    def _me(self):
        page = self._scroll_page()
        card = self._card(page, pady=(14, 8))
        self._label(card, "演示账号", 16, TEXT, True)
        self._label(card, "检修工程师 · 现场作业组", 10, MUTED)

        data = self._card(page)
        self._label(data, "演示数据", 13, TEXT, True)
        for line in ["累计检修任务：46", "本周知识沉淀：9", "高风险闭环：100%", "离线资料包：已同步"]:
            self._label(data, line, 10, MUTED)


if __name__ == "__main__":
    app = NativeMaintenanceDemo()
    app.mainloop()
