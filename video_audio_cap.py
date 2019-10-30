# python + opencv 实现屏幕录制
import queue
import sys
import threading
import wave

from cv2 import cv2
import numpy as np
import sounddevice as sd
import soundfile as sf
from PIL import ImageGrab
from pyaudio import PyAudio, paInt16
from scipy.io import wavfile
'''*******************************屏幕录制*******************************'''


class VideoCapThread(threading.Thread):
    def __init__(self, videofile='record.avi'):
        threading.Thread.__init__(self)
        self.bRecord = True
        self.video = cv2.VideoWriter(videofile,
                                     cv2.VideoWriter_fourcc(*'XVID'), 32,
                                     ImageGrab.grab().size)  # 帧率为32，可以调节

    def run(self):
        while self.bRecord:
            im = ImageGrab.grab()
            imm = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
            self.video.write(imm)
        self.video.release()
        cv2.destroyAllWindows()

    def stoprecord(self):
        self.bRecord = False


'''*******************************麦克风输入-音频录制*******************************'''


class AudioRecThread(threading.Thread):
    def __init__(self, audiofile='record.wav'):
        threading.Thread.__init__(self)
        self.bRecord = True
        self.audiofile = audiofile
        self.chunk = 1024
        self.format = paInt16
        self.channels = 1
        self.rate = 16000

    def run(self):
        audio = PyAudio()
        wavfile = wave.open(self.audiofile, 'wb')
        wavfile.setnchannels(self.channels)
        wavfile.setsampwidth(audio.get_sample_size(self.format))
        wavfile.setframerate(self.rate)
        wavstream = audio.open(format=self.format,
                               channels=self.channels,
                               rate=self.rate,
                               input=True,
                               frames_per_buffer=self.chunk)
        while self.bRecord:
            wavfile.writeframes(wavstream.read(self.chunk))
        wavstream.stop_stream()
        wavstream.close()
        audio.terminate()

    def stoprecord(self):
        self.bRecord = False


'''*******************************系统输出音频录制*******************************'''


class SoundRecThread(threading.Thread):
    def __init__(self, audiofile='record.wav'):
        threading.Thread.__init__(self)
        self.bRecord = True
        self.filename = audiofile
        self.samplerate = 44100
        self.channels = 2

    def run(self):
        q = queue.Queue()

        def callback(indata, frames, time, status):
            """This is called (from a separate thread) for each audio block."""
            if status:
                print(status, file=sys.stderr)
            q.put(indata.copy())

        with sf.SoundFile(self.filename,
                          mode='x',
                          samplerate=self.samplerate,
                          channels=self.channels) as file:
            with sd.InputStream(samplerate=self.samplerate,
                                channels=self.channels,
                                callback=callback):
                while self.bRecord:
                    file.write(q.get())

    def stoprecord(self):
        self.bRecord = False
