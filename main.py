# coding=utf-8
import os
import subprocess
import time

from selenium import webdriver

from video_audio_cap import SoundRecThread, VideoCapThread

if __name__ == "__main__":
    url = 'https://github.com/Zweo/Video_Audio_Record'
    output_path = ''
    option = webdriver.ChromeOptions()  # 打开浏览器
    option.add_argument(  # 设置成用户自己的数据目录
        '--user-data-dir=C:\\Users\\Admin\\AppData\\Local\\Google\\Chrome\\User Data'
    )
    driver = webdriver.Chrome(options=option)
    driver.get(url)

    avi_file = output_path + 'tmp.avi'
    wav_file = output_path + 'tmp.wav'
    t1 = VideoCapThread(avi_file)
    t2 = SoundRecThread(wav_file)
    t1.start()
    t2.start()
    time.sleep(5)  # 录制5s
    t1.stoprecord()
    t2.stoprecord()
    mp4_file = output_path + 'result.mp4'
    subprocess.call('ffmpeg -i {} -i {} -strict -2 -f mp4 {}'.format(
        avi_file, wav_file, mp4_file))
    os.remove(avi_file)
    os.remove(wav_file)
