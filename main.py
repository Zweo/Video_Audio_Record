# coding=utf-8
import json
import subprocess
import time
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

from video_audio_cap import SoundRecThread, VideoCapThread

output_path = 'E:\\python\\MyTools\\res\\result\\'
siki_url = 'http://www.sikiedu.com/'


def get_soup(url, headers):
    url_get = requests.get(url, headers=headers)
    return BeautifulSoup(url_get.text)


if __name__ == "__main__":
    cid = 95

    # 打开浏览器
    option = webdriver.ChromeOptions()
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
    html_soup = get_soup('{}course/{}'.format(siki_url, cid), headers)
    html_content = html_soup.find("div", "hidden js-hidden-cached-data")
    html_content = json.loads(''.join(html_content))

    # 得到单个课程网址,分别进行处理
    for index, content in enumerate(html_content):
        itemType, taksId = content['itemType'], content['taskId']
        file_type, title = content['type'], content['title'].split(' ')[-1]
        url = '{}course/{}/{}/{}/show'.format(siki_url, cid, itemType, taksId)
        # if file_type == 'download':
        if index in [1, 2]:
            pass
        else:
            driver.get(url)
            driver.switch_to.frame('task-content-iframe')
            driver.switch_to.frame(0)
            driver.find_element_by_class_name('vjs-fullscreen-control').click()
            cur = driver.find_element_by_class_name('vjs-current-time-display')
            total = driver.find_element_by_class_name('vjs-duration-display')
            play = driver.find_element_by_class_name('vjs-play-control')

            #
            play.click()
            avi_file = output_path + 'tmp.avi'
            wav_file = output_path + 'tmp.wav'
            t1 = VideoCapThread(avi_file)
            t2 = SoundRecThread(wav_file)
            while total.text == '0:00':
                pass

            t1.start()
            t2.start()
            total_time = total.text
            json_cmd = "return arguments[0].textContent"
            cur_time = driver.execute_script(json_cmd, cur).split(' ')[1]
            while cur_time != total_time:
                time.sleep(1)
                cur_time = driver.execute_script(json_cmd, cur).split(' ')[1]
                print(cur_time + '/' + total_time)
            print('Over')
            t1.stoprecord()
            t2.stoprecord()
            mp4_file = output_path + '[{}]{}.mp4'.format(index, title)
            subprocess.call('ffmpeg -i {} -i {} -strict -2 -f mp4 {}'.format(
                avi_file, wav_file, mp4_file))
            os.remove(avi_file)
            os.remove(wav_file)
