# -*- coding: utf-8 -*-

import os
import json
import requests

def main():
    config_file = 'config.json'
    default_config = {
        "base_url": "https://hayqbhgr.slider.kz/vk_auth.php?q=",
        "max_duration": 3600  # 默认最大时长
    }

    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        # 写入默认配置
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f'配置文件 {config_file} 不存在，已创建默认配置。')
    else:
        print(f'配置文件 {config_file} 已存在。')
    
    # 读取配置文件
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # 更新 base_url 和 max_duration
    global base_url, max_duration
    base_url = config.get('base_url', default_config['base_url'])
    max_duration = config.get('max_duration', default_config['max_duration'])
    
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
        
        # 解析音频信息
        parse_audio_info(json_data)
        
        # 返回解析后的JSON数据
        return json_data
    else:
        print(f'请求失败，状态码：{response.status_code}')
        return None

def parse_audio_info(json_data):
    audios = json_data.get('audios', [])
    for index, audio in enumerate(audios):
        duration = audio.get('duration')
        tit_art = audio.get('tit_art')
        
        # 排除配置文件中认为过长的音频
        if duration > max_duration:
            continue
        
        # 时间格式转换
        minutes = duration // 60
        seconds = duration % 60
        
        print(f"编号: {index + 1}")
        print(f"时长: {minutes} 分 {seconds} 秒")
        print(f"曲名: {tit_art}")
        print("-" * 40)

# 调用 main 函数
if __name__ == "__main__":
    main()