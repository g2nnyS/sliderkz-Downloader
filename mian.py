# -*- coding: utf-8 -*-

import os
import json
import requests
import re

start_text = """
      _  _      _                 _         
     | |(_)    | |               | |        
 ___ | | _   __| |  ___  _ __    | | __ ____
/ __|| || | / _` | / _ \| '__|   | |/ /|_  /
\__ \| || || (_| ||  __/| |    _ |   <  / / 
|___/|_||_| \__,_| \___||_|   (_)|_|\_\/___|
        Download Tool for Slider.kz                                                                                                                                                                                          
    Thanks for using!     by Ganyu_Genshin

"""

print(start_text)

def main():
    default_config = {
        "base_url": "https://hayqbhgr.slider.kz/vk_auth.php?q=",
        "max_duration": 3600,
        "debug": False
    }
    config_file = 'config.json'

    # 检查配置文件是否存在
    print("正在检查默认配置...")
    if not os.path.exists(config_file):
        # 写入默认配置
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f'配置文件 {config_file} 不存在，已创建默认配置。')
    else:
        print(f'通过!')

    # 读取配置文件
    with open(config_file, 'r') as f:
        config = json.load(f)

    # 更新 base_url, max_duration 和 debug
    global base_url, max_duration, debug
    base_url = config.get('base_url')
    max_duration = config.get('max_duration')
    debug = config.get('debug', False)
    print("本次搜索将会排除时长超过 %d 秒的音频文件。" % max_duration)
    print("初始化检查已完成！")

    # 调用 search 函数
    search()

def search():
    input_prompt = input('请输入要搜索的内容：')
    while not input_prompt:
        input_prompt = input('搜索关键词不能为空，请重新输入：')
    
    search_url = base_url + input_prompt
    
    # 发送HTTP请求获取JSON响应
    response = requests.get(search_url)
    
    # 检查请求是否成功
    if response.status_code == 200:
        print('请求成功')
        # 将响应内容存储到变量并解析JSON
        json_data = response.json()
        if debug:
            print(f"调试信息：获取到的JSON数据：{json_data}")
        # 解析音频信息
        audio_urls = parse_audio_info(json_data, max_duration)
        if not audio_urls:
            print("没有符合条件的音频文件。")
    else:
        print(f'请求失败，状态码：{response.status_code}')

if __name__ == "__main__":
    main()