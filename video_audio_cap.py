# 录音录屏，合成
import queue
import sys
import threading
import wave
import subprocess
import os
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
        wavfile = wave.open(self.audiofile, 'ab')
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


'''*******************************FFmpeg音视频合成*******************************'''


class FFmpegThread(threading.Thread):
    def __init__(self, avi_file, wav_file, mp4_file):
        threading.Thread.__init__(self)
        self.avi_file = avi_file
        self.wav_file = wav_file
        self.mp4_file = mp4_file
        self.mode = 'dir' if os.path.isdir(self.avi_file) else 'file'

    def combine_to_mp4(self, avi_file, wav_file, mp4_file):
        subprocess.call('ffmpeg -i {} -i {} -strict -2 -f mp4 {}'.format(
            avi_file, wav_file, mp4_file))
        os.remove(avi_file)
        os.remove(wav_file)

    def run(self):
        print('FFmpeg Start ……')
        if self.mode == 'file':
            self.combine_to_mp4(self.avi_file, self.wav_file, self.mp4_file)
        elif self.mode == 'dir':
            avi_files = os.listdir(self.avi_file)
            wav_files = os.listdir(self.wav_file)
            mp4_files = []
            file_num = len(avi_files)
            for i in range(file_num):
                avi_file = os.path.join(self.avi_file, avi_files[i])
                wav_file = os.path.join(self.wav_file, wav_files[i])
                if file_num == 1:
                    self.combine_to_mp4(avi_file, wav_file, self.mp4_file)
                    return
                mp4_file = self.mp4_file + '_{}.mp4'.format(i)
                mp4_files.append(mp4_file)
                self.combine_to_mp4(avi_file, wav_file, mp4_file)
            self.ts_to_mp4(mp4_files)

    def ts_to_mp4(self, files):
        ts_files = []
        for file in files:
            ts_file = file[:-3] + 'ts'
            ts_files.append(ts_file)
            command = 'ffmpeg -i {} -c copy -vbsf h264_mp4toannexb {}'
            command = command.format(file, ts_file)
            subprocess.call(command)
        input_files = '|'.join(ts_files)
        command = 'ffmpeg.exe -i "concat:{}" -c copy -absf aac_adtstoasc {}'
        command = command.format(input_files, self.mp4_file)
        subprocess.call(command)
        for item in files:
            os.remove(item)
        for item in ts_files:
            os.remove(item)

        print('FFmpeg Finish ……')
