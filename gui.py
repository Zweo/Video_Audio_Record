'''
github:Zweo
2019.12.12
'''
import datetime
import os
import sys
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QCursor

from video_audio_cap import FFmpegThread, SoundRecThread, VideoCapThread

SCREEN_WEIGHT = 1920 * 2
SCREEN_HEIGHT = 1080
WINDOW_WEIGHT = 180
WINDOW_HEIGHT = 50
RESULT_PATH = './res'  # 存储录屏和录音的位置


def create_dirs():
    if not os.path.exists(RESULT_PATH):
        os.mkdir(RESULT_PATH)
    video_path = os.path.join(RESULT_PATH, 'video')
    sound_path = os.path.join(RESULT_PATH, 'sound')
    if not os.path.exists(video_path):
        os.mkdir(video_path)
    if not os.path.exists(sound_path):
        os.mkdir(sound_path)
    return video_path, sound_path


class qt_window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.start_pressed = False
        self.file_path = None
        self.dragPosition = QtCore.QPoint(0, 0)
        self.video_path, self.sound_path = create_dirs()

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.Tool
                            | QtCore.Qt.WindowStaysOnTopHint)  # 去掉标题栏
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
        self.start_pressed = not self.start_pressed
        if self.start_pressed:
            self.button_start_pause.setText('暂停')
            now = str(datetime.datetime.now()).split('.')[0]
            now = now.replace(' ', '_').replace(':', '.')
            self.file_path = {
                'video': os.path.join(self.video_path, now + '.avi'),
                'sound': os.path.join(self.sound_path, now + '.wav'),
                'output': os.path.join(RESULT_PATH, now + '.mp4')
            }
            self.video_recorder = VideoCapThread(self.file_path['video'])
            self.sound_recorder = SoundRecThread(self.file_path['sound'])
            self.video_recorder.start()
            self.sound_recorder.start()
        else:
            self.video_recorder.stoprecord()
            self.sound_recorder.stoprecord()
            self.button_start_pause.setText('开始')

    def stop(self):
        self.button_start_pause.setText('开始')
        self.start_pressed = False
        if self.file_path and os.path.exists(self.file_path['video']):
            self.video_recorder.stoprecord()
            self.sound_recorder.stoprecord()
            ffmpeg_th = FFmpegThread(self.video_path, self.sound_path,
                                     self.file_path['output'])
            ffmpeg_th.start()

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
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.stop()  # 开始转换
            # self.showMinimized()
            self.hide()
            while True:
                nums = threading.activeCount()
                if nums == 7:
                    exit(0)
        elif event.key() == Qt.Key_F6:
            self.start_pause()
        elif event.key() == Qt.Key_F7:
            self.stop()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = qt_window()
    ex.show()
    sys.exit(app.exec_())
