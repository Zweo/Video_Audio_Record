# coding=utf-8
import json
import subprocess
import time
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

from video_audio_cap import SoundRecThread, VideoCapThread

output_path = '文件输出路径/output_path'
url = 'url where you want visit'


def get_soup(url, headers):
    url_get = requests.get(url, headers=headers)
    return BeautifulSoup(url_get.text)


if __name__ == "__main__":
    option = webdriver.ChromeOptions()    # 打开浏览器
    # 设置成用户自己的数据目录
    option.add_argument(
        '--user-data-dir=C:\\Users\\Admin\\AppData\\Local\\Google\\Chrome\\User Data'
    )
    driver = webdriver.Chrome(options=option)
    driver.get('{}my/course/{}'.format(siki_url, cid))

    # 获取cookie后分析网页
    cookie = [i["name"] + "=" + i["value"] for i in driver.get_cookies()]
    headers = {
        'Accept':
        '*/*',
        'Accept-Language':
        'en-US,en;q=0.5',
        'Cookie':
        ''.join(cookie),
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
    }
    
    # 分析网页，得到对应链接
    html_soup = get_soup('url_1', headers)
    html_content = html_soup.find("class_1")
    html_content = json.loads(''.join(html_content))

    # 分析得到单个网址,分别进行处理
    for index, content in enumerate(html_content):
        url = '分析网页'
        if condition:
            driver.get(url)
            avi_file = output_path + 'tmp.avi'
            wav_file = output_path + 'tmp.wav'
            t1 = VideoCapThread(avi_file)
            t2 = SoundRecThread(wav_file)
            t1.start()
            t2.start()
          
            while conditon:
                time.sleep(1)
            t1.stoprecord()
            t2.stoprecord()
            mp4_file = output_path + '[{}]{}.mp4'.format(index, title)
            subprocess.call('ffmpeg -i {} -i {} -strict -2 -f mp4 {}'.format(
                avi_file, wav_file, mp4_file))
            os.remove(avi_file)
            os.remove(wav_file)
