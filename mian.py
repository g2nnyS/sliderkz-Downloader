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
    config_file = 'config.json'
    default_config = {
        "base_url": "https://hayqbhgr.slider.kz/vk_auth.php?q=",
        "max_duration": 3600  # 默认最大时长
    }
    
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
    
    # 更新 base_url 和 max_duration
    global base_url, max_duration
    base_url = config.get('base_url', default_config['base_url'])
    max_duration = config.get('max_duration', default_config['max_duration'])
    print("初始化检查已完成！")

    # 调用 search 函数
    search()

def search():
    input_prompt = input('请输入要搜索的内容：')
    while not input_prompt:
        input_prompt = input('搜索关键词不能为空，请重新输入：')
    
    url = base_url + input_prompt
    
    # 发送HTTP请求获取JSON响应
    response = requests.get(url)
    
    # 检查请求是否成功
    if response.status_code == 200:
        print('请求成功')
        # 将响应内容存储到变量并解析JSON
        json_data = response.json()
        
        # 打印所有 JSON 数据
        print(json.dumps(json_data, indent=4, ensure_ascii=False))
        
        # 解析音频信息
        audio_urls = parse_audio_info(json_data)
        
        # 询问用户排除哪些编号的曲目
        exclude_tracks(audio_urls)
    else:
        print(f'请求失败，状态码：{response.status_code}')

def parse_audio_info(json_data):
    audios = json_data.get('audios', [])
    audio_urls = []
    for index, audio in enumerate(audios):
        if isinstance(audio, dict):
            duration = audio.get('duration')
            tit_art = audio.get('tit_art')
            url = audio.get('url')
            
            # 检查音频数据是否包含所有必要字段
            if duration is None or tit_art is None or url is None:
                print(f"音频数据缺少必要字段: {audio}")
                continue
            
            # 排除时长在 max_duration 以上的音频
            if duration > max_duration:
                continue
            
            # 将时长从秒转换为分钟和秒
            minutes = duration // 60
            seconds = duration % 60
            
            print(f"编号: {index}")
            print(f"曲名: {tit_art}")
            print(f"时长: {minutes} 分 {seconds} 秒")
            print("-" * 40)
            
            # 存储音频的 URL
            audio_urls.append((index, url))
        else:
            print(f"音频数据格式错误: {audio}")
    return audio_urls

def exclude_tracks(audio_urls):
    excluded_indices = set()
    while True:
        exclude_input = input('请输入要排除的曲目编号（用逗号隔开），或按回车键结束：')
        if not exclude_input:
            break
        try:
            indices = [int(i.strip()) for i in exclude_input.split(',')]
            excluded_indices.update(indices)
        except ValueError:
            print("输入格式错误，请输入有效的编号。")
    
    # 过滤掉被排除的曲目
    filtered_urls = [url for index, url in audio_urls if index not in excluded_indices]
    
    # 开始下载
    download_tracks(filtered_urls)

def sanitize_filename(filename):
    # 移除任何不安全的字符
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    return filename

def download_tracks(urls):
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            filename = url.split('/')[-1]
            filename = sanitize_filename(filename)
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"已下载: {filename}")
        else:
            print(f"下载失败: {url}")

# 调用 main 函数
if __name__ == "__main__":
    main()