import sys

from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
screen = app.primaryScreen()
pixmap = screen.grabWindow(0)
ok = pixmap.save("/home/vmuser/desktop-capture.png", "png")
print("saved", ok, pixmap.width(), pixmap.height())
