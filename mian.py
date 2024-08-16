# -*- coding: utf-8 -*-

import os
import json
import requests
import re
from urllib.parse import quote

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

def Init():
    default_config = {
        "base_url": "https://hayqbhgr.slider.kz/vk_auth.php?q=",
        "max_duration": 3600,
        "debug": False,
        "download_dir": "downloads",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        "referer": "https://hayqbhgr.slider.kz/",
        "use_proxy": False,  # 默认不使用代理
        "proxy": "http://127.0.0.1:8080"  # 默认代理服务器地址
    }
    config_file = 'config.json'
    config_error = "配置项有误！请检查配置文件。如果你不知道发生了什么故障，请删除目录下的config.json，程序会自动按照默认配置新建配置文件。"

    # 检查配置文件是否存在
    print("正在检查配置文件...")
    if not os.path.exists(config_file):
        # 写入默认配置
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f'配置文件 {config_file} 不存在，已创建默认配置。')
        return

    # 读取配置文件
    with open(config_file, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            print("配置文件格式错误，请确保文件为有效的 JSON 格式。")
            print(config_error)
            input("按任意键退出")

    # 检查每个配置项是否存在并有效
    for key, value in default_config.items():
        if key not in config:
            print(f"配置文件中缺少配置项：{key}")
            print(config_error)
            input("按任意键退出")
        if not isinstance(config[key], type(value)):
            print(f"配置项 {key} 的类型无效，期望类型为 {type(value).__name__}，但得到的是 {type(config[key]).__name__}")
            print(config_error)
            input("按任意键退出")

    # 如果所有配置项均有效，更新全局变量
    global base_url, max_duration, debug, download_dir, user_agent, referer, use_proxy, proxy
    base_url = config.get('base_url')
    max_duration = config.get('max_duration')
    debug = config.get('debug')
    download_dir = config.get('download_dir')
    user_agent = config.get('user_agent')
    referer = config.get('referer')
    use_proxy = config.get('use_proxy')
    proxy = config.get('proxy')
    
    if debug:
        print("本次运行开启了调试模式。")
        print(f"Debug：请求的URL: {base_url}")
        print(f"Debug：最大时长: {max_duration}")
        print(f"Debug：下载目录: {download_dir}")
        print(f"Debug：用户代理: {user_agent}")
        print(f"Debug：HTTP来源地址: {referer}")
        print(f"Debug：是否使用代理: {use_proxy}")
        print(f"Debug：代理服务器地址: {proxy}")
        print(f"Debug：调试模式: {debug}")
    
    print("初始化检查已完成！")


def main():
    # 调用 search 函数获取 JSON 数据
    json_data = search()

    # 解析音频信息
    audio_urls = parse_audio_info(json_data, max_duration)

    # 让用户排除不需要的音频
    audio_urls = exclude_tracks(audio_urls)

    # 下载剩余的音频文件
    download_audio_files(audio_urls)

def search():
    input_prompt = input('请输入要搜索的内容：')
    while not input_prompt:
        input_prompt = input('搜索关键词不能为空，请重新输入：')
    
    # 对用户输入进行URL编码
    encoded_prompt = quote(input_prompt)
    search_url = base_url + encoded_prompt
    
    # 发送HTTP请求获取JSON响应
    headers = {
        'User-Agent': user_agent,
        'Referer': referer
    }
    response = requests.get(search_url, headers=headers)
    
    # 检查请求是否成功
    if response.status_code == 200:
        print('请求成功')
        # 将响应内容存储到变量并解析JSON
        json_data = response.json()
        if not isinstance(json_data, dict):
            print(f"调试信息：json_data 不是字典类型，实际为: {type(json_data)}")
            return None

        if debug:
            print(f"调试信息：获取到的JSON数据：{json_data}")
        return json_data
    else:
        print(f'请求失败，状态码：{response.status_code}')
        return None

def parse_audio_info(json_data, max_duration):
    audios_container = json_data.get('audios', {})
    audio_urls = []
    
    for key, audios in audios_container.items():
        if not isinstance(audios, list):
            if debug:
                print(f"调试信息：键 {key} 的值不是列表类型，跳过该键。")
            continue
        
        if debug:
            print(f"调试信息：获取到 {len(audios)} 个音频文件。")
        
        for index, audio in enumerate(audios):
            if isinstance(audio, dict):
                # 输出音频对象的原始数据
                if debug:
                    print(f"调试信息：音频数据: {audio}")
                
                duration = audio.get('duration')
                tit_art = audio.get('tit_art')
                url = audio.get('url')
                
                # 检查音频数据是否包含所有必要字段
                if duration is None or tit_art is None or url is None:
                    if debug:
                        print(f"调试信息：音频数据缺少必要字段 (duration: {duration}, tit_art: {tit_art}, url: {url})")
                    continue
                
                # 排除时长在 max_duration 以上的音频
                if duration > max_duration:
                    if debug:
                        print(f"调试信息：音频时长 {duration} 秒超过最大时长 {max_duration} 秒，已排除。")
                    continue
                
                # 将编号、曲名和URL添加到列表中
                audio_info = {
                    'index': index,
                    'title': tit_art,
                    'url': url,
                    'duration': f"{duration // 60} 分 {duration % 60} 秒"
                }
                audio_urls.append(audio_info)
    
    return audio_urls

def exclude_tracks(audio_urls):
    excluded_indices = set()
    all_excluded_tracks = []

    # 打印初始的音频文件列表
    print("音频文件列表:")
    for audio in audio_urls:
        print(f"编号: {audio['index']}, 曲名: {audio['title']}, 时长: {audio['duration']}")
    
    while True:
        exclude_input = input('请输入要排除的曲目编号（用逗号隔开），或按回车键跳过排除：')
        
        if not exclude_input:
            break
        
        try:
            indices = [int(i.strip()) for i in exclude_input.split(',')]
            new_exclusions = [index for index in indices if index not in excluded_indices]
            ignored_exclusions = [index for index in indices if index in excluded_indices]
            
            # 更新已排除的索引集合
            excluded_indices.update(new_exclusions)
            
            # 更新所有被排除的曲目列表
            for index in new_exclusions:
                audio = next((audio for audio in audio_urls if audio['index'] == index), None)
                if audio:
                    all_excluded_tracks.append(audio)
            
            # 显示已排除的曲目
            if new_exclusions:
                print("你已经排除：")
                for audio in all_excluded_tracks:
                    print(f"编号: {audio['index']}, 曲名: {audio['title']}, 时长: {audio['duration']}")
            
            # 提示被忽略的排除项目（如果有）
            if ignored_exclusions:
                print("以下编号已经被排除，忽略它们：")
                print(", ".join(map(str, ignored_exclusions)))
            
            if debug:
                # 调试信息：打印排除后的剩余曲目
                print("调试信息：剩余的音频文件列表:")
                for audio in audio_urls:
                    if audio['index'] not in excluded_indices:
                        print(f"编号: {audio['index']}, 曲名: {audio['title']}, 时长: {audio['duration']}")
            
        except ValueError as e:
            print("输入无效，请输入有效的编号。")
            if debug:
                print(f"调试信息：输入处理错误：{e}")
            continue
        
        more_exclude = input('是否需要再次输入要排除的曲目？(y/n)：').strip().lower()
        if more_exclude != 'y':
            break
    
    # 过滤掉排除的曲目
    filtered_urls = [audio for audio in audio_urls if audio['index'] not in excluded_indices]
    
    if debug:
        # 调试信息：打印最终保留的曲目列表
        print("调试信息：最终保留的音频文件列表:")
        for audio in filtered_urls:
            print(f"编号: {audio['index']}, 曲名: {audio['title']}, 时长: {audio['duration']}")
    
    return filtered_urls

def download_audio_files(audio_urls):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    headers = {
        'User-Agent': user_agent,
        'Referer': referer
    }

    proxies = {
        "http": proxy,
        "https": proxy
    } if use_proxy else None

    for audio in audio_urls:
        url = audio['url']
        title = audio['title'].replace("/", "_")
        filename = f"{download_dir}/{title}.mp3"
        
        print(f"正在下载: {title}")

        try:
            with requests.get(url, headers=headers, proxies=proxies, timeout=10, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                chunk_size = 8192
                downloaded_size = 0
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        progress = downloaded_size / total_size * 100
                        downloaded_mb = downloaded_size / (1024 * 1024)
                        total_mb = total_size / (1024 * 1024)
                        print(f"已下载: {downloaded_mb:.2f}/{total_mb:.2f} MB ({progress:.2f}%)", end='\r')

            print(f"\n已保存: {filename}")
        except requests.exceptions.RequestException as e:
            print(f"下载 {title} 失败")
    
    print("所有文件下载完成！")

Init()

if __name__ == "__main__":
    main()
