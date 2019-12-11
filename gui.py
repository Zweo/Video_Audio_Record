import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QEvent

SCREEN_WEIGHT = 1920 * 2
SCREEN_HEIGHT = 1080
WINDOW_WEIGHT = 180
WINDOW_HEIGHT = 50


class qt_window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.press_start = True

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.WindowStaysOnTopHint
                            | QtCore.Qt.Tool)  # 去掉标题栏
        # 控件布局
        self.button_start_pause = QtWidgets.QPushButton(u"开始")
        self.button_stop = QtWidgets.QPushButton(u"结束")

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(self.button_start_pause)
        main_layout.addWidget(self.button_stop)
        self.setLayout(main_layout)

        # 界面美化
        style = """
            QPushButton {
                color: rgb(137, 221, 255);
                background-color: rgb(37, 121, 255);
                border-style:none;
                border:1px solid #3f3f3f;
                padding:5px;
                min-height:20px;
                border-radius:15px;
            }
        """
        self.setStyleSheet(style)
        palette1 = QtGui.QPalette()
        palette1.setColor(self.backgroundRole(),
                          QtGui.QColor("#F8F8FF"))  # 设置背景颜色
        self.setPalette(palette1)
        self.setFixedSize(WINDOW_WEIGHT, WINDOW_HEIGHT)

        # 绑定信号和槽
        self.button_start_pause.clicked.connect(self.start_pause)
        self.button_stop.clicked.connect(self.stop)

    def start_pause(self):
        if self.press_start:
            self.button_start_pause.setText('暂停')
            self.press_start = False
        else:
            self.button_start_pause.setText('开始')
            self.press_start = True

    def stop(self):
        exit(0)

    def enterEvent(self, event):
        print('enter')
        self.hide_or_show('show', event)

    def leaveEvent(self, event):
        print('leave')
        self.hide_or_show('hide', event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry(
            ).topLeft()
            QtWidgets.QApplication.postEvent(self, QEvent(174))
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            try:
                self.move(event.globalPos() - self.dragPosition)
                event.accept()
            except:
                print('Error:Move before Press')

    def mouseReleaseEvent(self, event):
        self.hide_or_show('hide', event)

    def hide_or_show(self, mode, event):
        pos = self.frameGeometry().topLeft()
        print(pos)
        if mode == 'show':
            if pos.x() + WINDOW_WEIGHT >= SCREEN_WEIGHT:  # 右侧隐藏
                self.move(
                    QtCore.QPoint(SCREEN_WEIGHT - WINDOW_WEIGHT + 2, pos.y()))
                event.accept()
            elif pos.x() <= 2:  # 左侧隐藏
                self.move(QtCore.QPoint(0, pos.y()))
                event.accept()
        elif mode == 'hide':
            if pos.x() + WINDOW_WEIGHT >= SCREEN_WEIGHT:  # 右侧隐藏
                self.move(QtCore.QPoint(SCREEN_WEIGHT - 2, pos.y()))
                event.accept()
            elif pos.x() <= 2:  # 左侧隐藏
                self.move(QtCore.QPoint(2 - WINDOW_WEIGHT, pos.y()))
                event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = qt_window()
    ex.show()
    sys.exit(app.exec_())
