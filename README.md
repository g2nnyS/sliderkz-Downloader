# slider.kz-Downloader
Download music for https://hayqbhgr.slider.kz/

- **base_url**: Slider.kz 的搜索 URL，不要修改。
- **max_duration**: 最大时长，单位为秒。
- **min_duration**: 最小时长，单位为秒。
- **debug**: 是否开启调试模式，如果你不是开发人员，将其设置为 `false`。
- **download_dir**: 下载目录。
- **temp_dir**: 临时文件目录，用于在多线程下载时存储临时文件。
- **user_agent**: 用户代理，用于伪装请求，最好不要修改。
- **referer**: HTTP 来源地址，用于伪装请求，最好不要修改。
- **use_proxy**: 是否使用代理。
- **proxy**: 代理服务器地址。
- **mode**: 模式，有黑名单模式和白名单模式。
  - **白名单模式**: 你需要输入要保留的曲目编号。
  - **黑名单模式**: 你需要输入要排除的曲目编号。
- **max_workers**: 最大线程数。
- **max_retries**: 最大重试次数。
- **chunk_size**: 块大小。
- **num_threads**: 每个文件的线程数。
- **use_multithreading**: 是否使用多线程下载。
- **disable_ssl_warnings**: 是否禁用 SSL 警告。
