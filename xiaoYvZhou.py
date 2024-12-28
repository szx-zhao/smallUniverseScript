import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
import time
import re  # 用于处理文件名中的非法字符
import os  # 用于处理路径
import tkinter as tk
import logging
from tkinter import filedialog, messagebox, ttk

# 设置日志记录
logging.basicConfig(filename='download_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 自动安装ChromeDriver
chromedriver_autoinstaller.install()

# 设置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 下载音频的函数
def download_audio():
    urls = url_entry.get("1.0", tk.END).strip().splitlines()  # 获取多行输入的URL
    save_directory = save_path_entry.get()

    if not urls or not any(urls):
        logging.error("请输入至少一个目标URL")
        messagebox.showerror("错误", "请输入至少一个目标URL")
        return

    if not save_directory:
        logging.error("请输入保存路径")
        messagebox.showerror("错误", "请输入保存路径")
        return

    # 创建WebDriver实例
    driver = webdriver.Chrome(options=chrome_options)

    try:
        for url in urls:
            if not url.strip():
                continue  # 跳过空行

            # 打开页面
            driver.get(url)

            # 等待页面加载
            time.sleep(1)  # 根据需要调整等待时间

            # 查找audio标签并提取src属性
            audio_tag = driver.find_element(By.TAG_NAME, 'audio')
            audio_url = audio_tag.get_attribute('src') if audio_tag else None

            # 查找h1标签并提取文本内容
            h1_tag = driver.find_element(By.TAG_NAME, 'h1')
            h1_text = h1_tag.text if h1_tag else "音频"  # 默认名称为"音频"

            # 处理文件名，去掉非法字符
            file_name = re.sub(r'[<>:"/\\|?*]', '', h1_text) + '.m4a'

            # 完整的文件路径
            file_path = os.path.join(save_directory, file_name)

            logging.info(f"音频文件URL: {audio_url}")
            logging.info(f"文件名: {file_name}")
            
            # 更新标签显示当前文件名
            file_name_label.config(text=f"正在下载: {file_name}")
            
            # 下载音频文件
            if audio_url:
                audio_response = requests.get(audio_url, stream=True)  # 使用stream=True以便逐块下载
                total_size = int(audio_response.headers.get('content-length', 0))  # 获取文件总大小
                downloaded_size = 0

                # 显示进度条
                progress_bar['value'] = 0
                progress_bar['maximum'] = 100
                progress_bar.pack(pady=20)  # 显示进度条

                # 检查请求是否成功
                if audio_response.status_code == 200:
                    with open(file_path, 'wb') as audio_file:
                        for data in audio_response.iter_content(chunk_size=1024):  # 每次下载1KB
                            audio_file.write(data)
                            downloaded_size += len(data)
                            progress = (downloaded_size / total_size) * 100  # 计算下载进度
                            progress_bar['value'] = progress  # 更新进度条
                            root.update_idletasks()  # 更新界面

                    logging.info(f"音频文件下载成功，保存路径: {file_path}")
                else:
                    logging.error(f"下载失败，状态码: {audio_response.status_code}")
            else:
                logging.error("未找到音频文件的URL。")
    except Exception as e:
        logging.error(f"错误: {str(e)}")
    finally:
        # 关闭WebDriver
        driver.quit()
        progress_bar.pack_forget()  # 隐藏进度条
        file_name_label.config(text="")  # 清空文件名标签

# 选择文件保存的目录
def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        save_path_entry.delete(0, tk.END)  # 清空当前输入
        save_path_entry.insert(0, directory)  

# 清空URL输入框    
def clear_url():
    url_entry.delete("1.0", tk.END)  
    
# 创建主窗口
root = tk.Tk()
root.title("中文播客榜音频下载器")

# 设置窗口大小
window_width = 600
window_height = 400

# 获取屏幕宽度和高度
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# 计算窗口位置
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)

# 设置窗口大小和位置
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# URL输入框和清除按钮的框架
url_frame = tk.Frame(root)
url_frame.pack(pady=5)

tk.Label(url_frame, text="请输入目标URL（每行一个）:").pack(side=tk.LEFT)

# 使用Text控件以支持多行输入
url_entry = tk.Text(url_frame, width=50, height=10)
url_entry.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(url_frame, text="清除", command=clear_url)
clear_button.pack(side=tk.LEFT)

# 保存路径输入框和浏览按钮的框架
frame = tk.Frame(root)
frame.pack(pady=5)

tk.Label(frame, text="请输入文件保存地址:").pack(side=tk.LEFT)

save_path_entry = tk.Entry(frame, width=50)
save_path_entry.insert(0, r'D:\BaiduNetdiskDownload\RSS播客')  # 设置默认路径
save_path_entry.pack(side=tk.LEFT, padx=5)

browse_button = tk.Button(frame, text="浏览", command=browse_directory)
browse_button.pack(side=tk.LEFT)

# 下载按钮
download_button = tk.Button(root, text="下载音频", command=download_audio)
download_button.pack(pady=20)

# 创建进度条
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
# 初始时隐藏进度条
progress_bar.pack_forget()

# 创建标签以显示当前下载的文件名
file_name_label = tk.Label(root, text="", font=("Arial", 12))
file_name_label.pack(pady=10)

# 运行主循环
root.mainloop() 