# -*- coding: utf-8 -*-
import os
import json
import requests
import re
from urllib.parse import quote
import threading
import warnings
from time import sleep
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
from tqdm import tqdm

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
config = None

# 初始化配置
def Init():
    default_config = {
        "base_url": "https://hayqbhgr.slider.kz/vk_auth.php?q=",
        "max_duration": 3600,
        "min_duration": 0,
        "debug": False,
        "download_dir": "downloads",
        "temp_dir": "Temp",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        "referer": "https://hayqbhgr.slider.kz/",
        "use_proxy": False,
        "proxy": "http://127.0.0.1:8080",
        "mode": "blacklist",
        "max_workers": 5,
        "max_retries": 3,
        "chunk_size": 8192,
        "num_threads": 4,
        "use_multithreading": False,
        "disable_ssl_warnings": True  # 添加多线程开关
    }
    config_file = 'config.json'
    config_error = "配置项有误！请检查配置文件。如果你不知道发生了什么故障，请删除目录下的config.json，程序会自动按照默认配置新建配置文件。"

    global base_url, max_duration, min_duration, debug, download_dir, temp_dir, user_agent, referer, use_proxy, proxy, mode, max_workers, max_retries, chunk_size, num_threads, use_multithreading, disable_ssl_warnings

    print("正在检查配置文件...")
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f'配置文件 {config_file} 不存在，已创建默认配置。')
        teach()
        return default_config

    with open(config_file, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            print("配置文件格式错误，请确保文件为有效的 JSON 格式。")
            print(config_error)
            input("按任意键退出")
            return default_config

    for key, value in default_config.items():
        if key not in config:
            print(f"配置文件中缺少配置项：{key}")
            print(config_error)
            input("按任意键退出")
        if not isinstance(config[key], type(value)):
            print(f"配置项 {key} 的类型无效，期望类型为 {type(value).__name__}，但得到的是 {type(config[key]).__name__}")
            print(config_error)
            input("按任意键退出")
        if config.get('mode') not in ["blacklist", "whitelist"]:
            print(f"模式 {config.get('mode')} 无效，请输入有效的模式（blacklist/whitelist）")
            input("按任意键退出")

    base_url = config.get('base_url')
    max_duration = config.get('max_duration')
    min_duration = config.get('min_duration')
    debug = config.get('debug')
    download_dir = config.get('download_dir')
    temp_dir = config.get('temp_dir')
    user_agent = config.get('user_agent')
    referer = config.get('referer')
    use_proxy = config.get('use_proxy')
    proxy = config.get('proxy')
    mode = config.get('mode')
    max_workers = config.get('max_workers')
    max_retries = config.get('max_retries')
    chunk_size = config.get('chunk_size')
    num_threads = config.get('num_threads')
    use_multithreading = config.get('use_multithreading')
    disable_ssl_warnings = config.get('disable_ssl_warnings')

    if disable_ssl_warnings:
        warnings.simplefilter('ignore', InsecureRequestWarning)

    if debug:
        print("[重要提醒]本次运行开启了调试模式。")
        print("如果你不知道这是什么，请在config.json中将debug设置为False。")
        print("以下是配置信息：")
        print(f"Debug：请求的URL: {base_url}")
        print(f"Debug：最大时长: {max_duration}")
        print(f"Debug：最小时长: {min_duration}")
        print(f"Debug：下载目录: {download_dir}")
        print(f"Debug：临时目录: {temp_dir}")
        print(f"Debug：用户代理: {user_agent}")
        print(f"Debug：HTTP来源地址: {referer}")
        print(f"Debug：是否使用代理: {use_proxy}")
        print(f"Debug：代理服务器地址: {proxy}")
        print(f"Debug：调试模式: {debug}")
        print(f"Debug：模式: {mode}")
        print(f"Debug：最大线程数: {max_workers}")
        print(f"Debug：最大重试次数: {max_retries}")
        print(f"Debug：块大小: {chunk_size}")
        print(f"Debug：每个文件的线程数: {num_threads}")
        print(f"Debug：是否使用多线程: {use_multithreading}")
        print(f"Debug：是否禁用 SSL 警告: {disable_ssl_warnings}")

    print("初始化检查已完成！")
    print("作者在此严肃提醒：在使用本工具时，请认真留意每一行输出，以免造成不可挽回的后果！  @Ganyu_Genshin")
    if mode == "blacklist":
        print("现在我们正工作在黑名单模式下。")
        print("在黑名单模式下，在筛选时，你需要输入要排除的曲目编号。")
    elif mode == "whitelist":
        print("现在我们正工作在白名单模式下。")
        print("在白名单模式下，在筛选时，你需要输入要保留的曲目编号。")
    return config

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

def parse_audio_info(json_data, max_duration, min_duration):
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
                
                # 排除时长在 max_duration 以上、min_duration 以下的音频
                if duration >= max_duration or duration <= min_duration:
                    if debug:
                        print(f"调试信息：音频 {tit_art} 的时长 {duration} 秒不在范围内，跳过该音频。")
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

def exclude_tracks(audio_urls, config):
    excluded_indices = set()
    included_indices = set()
    all_excluded_tracks = []
    all_included_tracks = []

    # 打印初始的音频文件列表
    print("音频文件列表:")
    for audio in audio_urls:
        print(f"编号: {audio['index']}, 曲名: {audio['title']}, 时长: {audio['duration']}")
    
    while True:
        exclude_input = input('请输入要排除或保留的曲目编号（用逗号隔开），或按回车键跳过：')
        
        if not exclude_input:
            break
        
        try:
            indices = [int(i.strip()) for i in exclude_input.split(',')]
            if config["mode"] == "blacklist":
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
            
            elif config["mode"] == "whitelist":
                new_inclusions = [index for index in indices if index not in included_indices]
                ignored_inclusions = [index for index in indices if index in included_indices]
                
                # 更新已保留的索引集合
                included_indices.update(new_inclusions)
                
                # 更新所有被保留的曲目列表
                for index in new_inclusions:
                    audio = next((audio for audio in audio_urls if audio['index'] == index), None)
                    if audio:
                        all_included_tracks.append(audio)
                
                # 显示已保留的曲目
                if new_inclusions:
                    print("你已经保留：")
                    for audio in all_included_tracks:
                        print(f"编号: {audio['index']}, 曲名: {audio['title']}, 时长: {audio['duration']}")
                
                # 提示被忽略的保留项目（如果有）
                if ignored_inclusions:
                    print("以下编号已经被保留，忽略它们：")
                    print(", ".join(map(str, ignored_inclusions)))
            
            if debug:
                # 调试信息：打印排除或保留后的剩余曲目
                print("调试信息：剩余的音频文件列表:")
                for audio in audio_urls:
                    if config["mode"] == "blacklist" and audio['index'] not in excluded_indices:
                        print(f"编号: {audio['index']}, 曲名: {audio['title']}, 时长: {audio['duration']}")
                    elif config["mode"] == "whitelist" and audio['index'] in included_indices:
                        print(f"编号: {audio['index']}, 曲名: {audio['title']}, 时长: {audio['duration']}")
            
        except ValueError as e:
            print("输入无效，请输入有效的编号。")
            if debug:
                print(f"调试信息：输入处理错误：{e}")
            continue
        
        while True:
            more_exclude = input('是否需要再次输入要排除或保留的曲目？(y/n)：').strip().lower()
            if more_exclude in ['y', 'n']:
                break
            else:
                print("无效输入，请输入 'y' 或 'n'。")
        
        if more_exclude != 'y':
            break
    
    # 根据模式过滤曲目
    if config["mode"] == "blacklist":
        filtered_urls = [audio for audio in audio_urls if audio['index'] not in excluded_indices]
    elif config["mode"] == "whitelist":
        filtered_urls = [audio for audio in audio_urls if audio['index'] in included_indices]
    
    if debug:
        # 调试信息：打印最终保留的曲目列表
        print("调试信息：最终保留的音频文件列表:")
        for audio in filtered_urls:
            print(f"编号: {audio['index']}, 曲名: {audio['title']}, 时长: {audio['duration']}")
    
    return filtered_urls

# 清理文件名中的非法字符
def clean_filename(filename):
    # 移除非法字符
    filename = re.sub(r'[\/:*?"<>|]', '_', filename)
    # 确保文件名不包含路径分隔符
    filename = os.path.basename(filename)
    return filename

def download_audio(audio, download_dir, headers, proxies, retries=0, failed_downloads=None, chunk_size=8192):
    url = audio['url']
    title = clean_filename(audio['title'])  # 清理文件名
    filename = os.path.join(download_dir, f"{title}.mp3")
    temp_filename = os.path.join(temp_dir, f"{title}.part")

    print(f"正在下载: {title}")

    if use_multithreading:
        try:
            response = requests.head(url, headers=headers, proxies=proxies, timeout=10, verify=False)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))

            def download_chunk(start, end, index, retries=0):
                headers_range = headers.copy()
                headers_range['Range'] = f"bytes={start}-{end}"
                chunk_filename = f"{temp_filename}.part{index}"
                while retries < max_retries:
                    try:
                        with requests.get(url, headers=headers_range, proxies=proxies, timeout=10, stream=True, verify=False) as response:
                            response.raise_for_status()
                            with open(chunk_filename, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=chunk_size):
                                    f.write(chunk)
                        break
                    except requests.exceptions.RequestException as e:
                        retries += 1
                        print(f"下载块 {index} 失败，重试中... ({retries}/{max_retries})")
                        if debug:
                            print(f"失败原因: {e}")
                else:
                    raise Exception(f"下载块 {index} 失败，已达到最大重试次数。")

            chunk_size = total_size // num_threads
            threads = []
            for i in range(num_threads):
                start = i * chunk_size
                end = start + chunk_size - 1 if i < num_threads - 1 else total_size - 1
                thread = threading.Thread(target=download_chunk, args=(start, end, i))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            with open(filename, 'wb') as f:
                for i in range(num_threads):
                    chunk_filename = f"{temp_filename}.part{i}"
                    if not os.path.exists(chunk_filename):
                        raise FileNotFoundError(f"块文件 {chunk_filename} 不存在，")
                    with open(chunk, 'rb') as chunk_file:
                        f.write(chunk_file.read())
                    os.remove(chunk_filename)

            print(f"\n已保存: {filename}")
        except Exception as e:
            error_message = str(e)
            if retries < max_retries:
                print(f"下载 {title} 失败，重试中... ({retries + 1}/{max_retries})")
                if debug:
                    print(f"失败原因: {error_message}")
                download_audio(audio, download_dir, headers, proxies, retries + 1, failed_downloads, chunk_size)
            else:
                print(f"下载 {title} 失败，已达到最大重试次数。失败原因: {error_message}")
                if failed_downloads is not None:
                    failed_downloads.append((audio, error_message))
    else:
        try:
            with requests.get(url, headers=headers, proxies=proxies, timeout=10, stream=True, verify=False) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                with open(filename, 'wb') as f, tqdm(
                    total=total_size, unit='B', unit_scale=True, desc=title
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        pbar.update(len(chunk))

            print(f"\n已保存: {filename}")
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            if retries < max_retries:
                print(f"下载 {title} 失败，重试中... ({retries + 1}/{max_retries})")
                if debug:
                    print(f"失败原因: {error_message}")
                download_audio(audio, download_dir, headers, proxies, retries + 1, failed_downloads, chunk_size)
            else:
                print(f"下载 {title} 失败，已达到最大重试次数。失败原因: {error_message}")
                if failed_downloads is not None:
                    failed_downloads.append((audio, error_message))

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

    failed_downloads = []

    for audio in audio_urls:
        download_audio(audio, download_dir, headers, proxies, 0, failed_downloads, chunk_size)

    if failed_downloads:
        print("以下文件下载失败，正在重新尝试下载：")
        for audio, error_message in failed_downloads:
            print(f"曲名: {audio['title']}, URL: {audio['url']}")
            if debug:
                print(f"失败原因: {error_message}")
        
        for audio, _ in failed_downloads:
            download_audio(audio, download_dir, headers, proxies, 0, None, chunk_size)

    print("所有文件下载完成！")

def main():
    global config
    config = Init()
    # 调用 search 函数获取 JSON 数据
    json_data = search()

    # 解析音频信息
    audio_urls = parse_audio_info(json_data, max_duration, min_duration)

    # 让用户排除不需要的音频
    audio_urls = exclude_tracks(audio_urls, config)

    # 下载剩余的音频文件
    download_audio_files(audio_urls)

    # 询问是否再次搜索
    while True:
        search_again = input('是否需要再次搜索？(y/n)：')
        if search_again == 'y':
            main()
        elif search_again == 'n':
            print("感谢使用！")
            input("按任意键退出")
        else:
            print("无效输入，请输入 'y' 或 'n'。")

def teach(): # 教程
    print("侦测到初次启动，教程准备中...")
    sleep(3)
    print("欢迎使用Slider.kz下载工具！")
    sleep(2)
    print("本工具可以帮助你下载Slider.kz上的音频文件。")
    sleep(2)
    print("为了你能更好的使用该工具，我们将花一点时间向你解释配置文件中各个项目的作用")
    sleep(2)
    print("base_url: Slider.kz的搜索URL，不要修改。")
    sleep(2)
    print("max_duration: 最大时长，单位为秒。")
    sleep(2)
    print("min_duration: 最小时长，单位为秒。")
    sleep(2)
    print("debug: 是否开启调试模式，如果你不是开发人员，将其设置为false。")
    sleep(2)
    print("download_dir: 下载目录。")
    sleep(2)
    print("temp_dir: 临时文件目录，用于在多线程下载时存储临时文件。")
    sleep(2)
    print("user_agent: 用户代理，用于伪装请求，最好不要修改。")
    sleep(2)
    print("referer: HTTP来源地址，用于伪装请求，最好不要修改。")
    sleep(2)
    print("use_proxy: 是否使用代理。")
    sleep(2)
    print("proxy: 代理服务器地址。")
    sleep(2)
    print("mode: 模式，有黑名单模式和白名单模式。")
    sleep(2)
    print("白名单模式: 你需要输入要保留的曲目编号。")
    sleep(2)
    print("黑名单模式: 你需要输入要排除的曲目编号。")
    sleep(2)
    print("max_workers: 最大线程数。")
    sleep(2)
    print("max_retries: 最大重试次数。")
    sleep(2)
    print("chunk_size: 块大小。")
    sleep(2)
    print("num_threads: 每个文件的线程数。")
    sleep(2)
    print("use_multithreading: 是否使用多线程下载。")
    sleep(2)
    print("disable_ssl_warnings: 是否禁用 SSL 警告。")
    sleep(2)
    print("以上是配置文件的各个项目的作用，请你仔细阅读并理解每个配置项的作用，如果你有任何问题，请联系作者。")
    sleep(2)
    print("如果配置文件出错，你可以删除config.json文件，程序会自动按照默认配置新建配置文件。")
    sleep(2)
    print("教程已结束，程序将会退出，在重启后你可以开始使用本工具。另外，你可以在README.md中再次查看这些信息。")
    input("按任意键退出")
    quit()

if __name__ == "__main__":
    main()