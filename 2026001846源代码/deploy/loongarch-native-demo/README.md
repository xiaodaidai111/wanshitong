# 龙芯麒麟原生桌面演示版

这个目录提供一个不依赖 HBuilderX 的桌面 App 演示壳，适合在 Kylin Server V11 / LoongArch64 虚拟机里展示“设备检修 APP 界面”。

## 为什么不用 HBuilderX

HBuilderX 官方下载页目前没有 LoongArch/Linux 桌面版入口。比赛虚拟机是 LoongArch64，直接安装 HBuilderX 很可能因为架构不兼容失败。

## 运行方式

进入本目录后运行：

```bash
python3 app.py
```

如果提示缺少 Tkinter，在麒麟系统中安装：

```bash
sudo apt install python3-tk
```

## 演示建议

- 用这个程序展示“原生桌面 App 界面”，不要打开浏览器。
- 如果要提交手机 APK，仍建议在 Windows 本机用 HBuilderX 打开 `frontend` 目录，然后进行 App 云打包。
- 如果要把这个演示壳做成桌面图标，可以创建 `.desktop` 文件指向 `python3 app.py`。
