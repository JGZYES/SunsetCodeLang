#!/usr/bin/env python3
"""
SCL 插件下载器 (scd)
用于下载和更新 SCL 插件的工具
"""

import os
import sys
import json
import time
import argparse
import threading
import concurrent.futures
import urllib.request
import urllib.error
import platform
import subprocess
from datetime import datetime

# 版本信息
VERSION = "1.0.0"

# 默认镜像源
DEFAULT_MIRROR = "https://scl.ecuil.com/run/plugins/"

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".scd_config.json")

# 多语言支持
LANGUAGES = {
    "en": {
        "installing_plugin": "Installing plugin: {}",
        "downloading_from": "Downloading from: {}",
        "plugin_installed": "Plugin {} installed successfully!",
        "install_failed": "Failed to install plugin {}",
        "installing_from_file": "Installing plugins from file: {}",
        "file_not_found": "File {} not found",
        "no_plugins_in_file": "No plugins found in file",
        "all_plugins_installed": "All plugins installed!",
        "reading_file_failed": "Failed to read file: {}",
        "updating_plugin": "Updating plugin: {}",
        "updating_scd": "Updating scd...",
        "local_version": "Local version: {}",
        "remote_version": "Remote version: {}",
        "found_new_version": "Found new version, downloading...",
        "unsupported_os": "Unsupported operating system",
        "update_failed": "Failed to download update",
        "scd_updated": "scd updated successfully!",
        "run_new_scd": "Please run the new scd{}",
        "already_latest": "{} is already up to date",
        "listing_local_plugins": "Listing local plugins...",
        "installed_plugins": "Installed plugins:",
        "no_plugins_installed": "No plugins installed",
        "plugins_dir_not_found": "Plugins directory not found",
        "listing_web_plugins": "Listing web plugins...",
        "fetching_plugins_from": "Fetching plugins from: {}",
        "available_plugins": "Available plugins:",
        "no_available_plugins": "No available plugins",
        "invalid_api_response": "Invalid API response",
        "install_required_packages": "Error: Please install required packages: pip install requests",
        "fetch_failed": "Failed to fetch plugins list: {}",
        "check_network": "Please check your network connection or mirror URL",
        "available_mirrors": "Available mirrors:",
        "adding_mirror": "Mirror {} added and set as current mirror",
        "mirror_exists": "Mirror {} already exists",
        "scd_info": "SCL Plugin Downloader (scd)",
        "version": "Version: 1.0.0",
        "current_mirror": "Current mirror: {}",
        "available_mirrors_count": "Available mirrors: {}",
        "cpu_cores": "CPU cores: {}",
        "download_threads": "Download threads: {}",
        "loading_config_failed": "Failed to load config file: {}",
        "saving_config_failed": "Failed to save config file: {}",
        "downloading_file": "Downloading: {}",
        "download_failed": "Failed to download file: {}",
        "error": "Error: {}",
        "warning_fallback": "Warning: Using fallback download method. Install requests and tqdm for better progress bars.",
        "language_set": "Language set to: {}",
        "language_not_supported": "Language not supported. Available languages: en, zh",
        "setting_language": "Setting language to: {}",
        "current_language": "Current language: {}"
    },
    "zh": {
        "installing_plugin": "正在安装插件: {}",
        "downloading_from": "从以下地址下载: {}",
        "plugin_installed": "插件 {} 安装成功！",
        "install_failed": "安装插件 {} 失败",
        "installing_from_file": "从文件安装插件: {}",
        "file_not_found": "文件 {} 不存在",
        "no_plugins_in_file": "文件中未找到插件",
        "all_plugins_installed": "所有插件安装完成！",
        "reading_file_failed": "读取文件失败: {}",
        "updating_plugin": "正在更新插件: {}",
        "updating_scd": "正在更新 scd...",
        "local_version": "本地版本: {}",
        "remote_version": "远程版本: {}",
        "found_new_version": "发现新版本，正在下载...",
        "unsupported_os": "不支持的操作系统",
        "update_failed": "下载更新失败",
        "scd_updated": "scd 更新成功！",
        "run_new_scd": "请运行新的 scd{}",
        "already_latest": "{} 已是最新版本，无需更新",
        "listing_local_plugins": "正在列出本地插件...",
        "installed_plugins": "已安装的插件:",
        "no_plugins_installed": "没有安装插件",
        "plugins_dir_not_found": "未找到插件目录",
        "listing_web_plugins": "正在列出网络插件...",
        "fetching_plugins_from": "从以下地址获取插件: {}",
        "available_plugins": "可用的插件:",
        "no_available_plugins": "没有可用的插件",
        "invalid_api_response": "API 响应无效",
        "install_required_packages": "错误: 请安装必要的包: pip install requests",
        "fetch_failed": "获取插件列表失败: {}",
        "check_network": "请检查网络连接或镜像 URL",
        "available_mirrors": "可用的镜像源:",
        "adding_mirror": "镜像 {} 已添加并设为当前镜像",
        "mirror_exists": "镜像 {} 已存在",
        "scd_info": "SCL 插件下载器 (scd)",
        "version": "版本: 1.0.0",
        "current_mirror": "当前镜像: {}",
        "available_mirrors_count": "可用镜像: {}",
        "cpu_cores": "CPU 核心数: {}",
        "download_threads": "下载线程数: {}",
        "loading_config_failed": "加载配置文件失败: {}",
        "saving_config_failed": "保存配置文件失败: {}",
        "downloading_file": "下载中: {}",
        "download_failed": "下载文件失败: {}",
        "error": "错误: {}",
        "warning_fallback": "警告: 使用后备下载方法。安装 requests 和 tqdm 以获得更好的进度条。",
        "language_set": "语言已设置为: {}",
        "language_not_supported": "不支持的语言。可用语言: en, zh",
        "setting_language": "正在设置语言为: {}",
        "current_language": "当前语言: {}"
    }
}

class SCDownloader:
    def __init__(self):
        self.config = self.load_config()
        self.mirrors = self.config.get("mirrors", [DEFAULT_MIRROR])
        self.current_mirror = self.config.get("current_mirror", DEFAULT_MIRROR)
        self.language = self.config.get("language", "zh")  # 默认中文
        # 获取 CPU 核心数，用于多线程下载
        self.cpu_cores = os.cpu_count() or 4
        self.threads = max(1, self.cpu_cores // 2)
    
    def _(self, key, *args):
        """获取翻译文本"""
        lang = self.language if self.language in LANGUAGES else "zh"
        return LANGUAGES[lang].get(key, key).format(*args)
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(self._("loading_config_failed", e))
        return {"mirrors": [DEFAULT_MIRROR], "current_mirror": DEFAULT_MIRROR, "language": "zh"}
    
    def save_config(self):
        """保存配置文件"""
        self.config["mirrors"] = self.mirrors
        self.config["current_mirror"] = self.current_mirror
        self.config["language"] = self.language
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(self._("saving_config_failed", e))
    
    def add_mirror(self, mirror_url):
        """添加镜像源"""
        if mirror_url not in self.mirrors:
            self.mirrors.append(mirror_url)
            self.current_mirror = mirror_url
            self.save_config()
            print(self._("adding_mirror", mirror_url))
        else:
            print(self._("mirror_exists", mirror_url))
    
    def set_language(self, lang):
        """设置语言"""
        if lang in LANGUAGES:
            print(self._("setting_language", lang))
            self.language = lang
            self.save_config()
            print(self._("language_set", lang))
        else:
            print(self._("language_not_supported"))
    
    def download_file(self, url, output_path, show_progress=True):
        """下载文件并显示进度（模范 PIP 风格）"""
        try:
            import requests
            from tqdm import tqdm
            
            # 发送 HEAD 请求获取文件大小
            response = requests.head(url)
            total_size = int(response.headers.get('content-length', 0))
            
            # 下载文件并显示进度条
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(output_path, 'wb') as f:
                    with tqdm(
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=os.path.basename(output_path),
                        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{rate_fmt}]'
                    ) as pbar:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
            return True
        except ImportError:
            # 如果没有 requests 和 tqdm，使用 urllib 作为后备
            print(self._("warning_fallback"))
            
            def progress_hook(count, block_size, total_size):
                if total_size > 0:
                    percent = int(count * block_size * 100 / total_size)
                    if show_progress:
                        # 动画效果：旋转指示器 + 进度条
                        spinner = "|/-\\"
                        spinner_pos = int(time.time() * 10) % 4
                        bar_length = 40
                        filled_length = int(bar_length * percent / 100)
                        bar = "█" * filled_length + "-" * (bar_length - filled_length)
                        sys.stdout.write(f"\r{spinner[spinner_pos]} 下载中: [{bar}] {percent}% ")
                        sys.stdout.flush()
            
            # 使用 urllib 下载文件
            urllib.request.urlretrieve(url, output_path, reporthook=progress_hook)
            if show_progress:
                sys.stdout.write("\r" + " " * 80 + "\r")
                sys.stdout.flush()
            return True
        except urllib.error.URLError as e:
            print(f"\n{self._('download_failed', e)}")
            return False
        except Exception as e:
            print(f"\n{self._('error', e)}")
            return False
    
    def install_plugin(self, plugin_name):
        """安装插件"""
        print(self._("installing_plugin", plugin_name))
        
        # 构建插件下载 URL
        plugin_url = f"{self.current_mirror}{plugin_name}.py"
        plugin_path = os.path.join("plugins", f"{plugin_name}.py")
        
        # 确保 plugins 目录存在
        os.makedirs("plugins", exist_ok=True)
        
        # 下载插件
        print(self._("downloading_from", plugin_url))
        if self.download_file(plugin_url, plugin_path):
            print(self._("plugin_installed", plugin_name))
            return True
        else:
            print(self._("install_failed", plugin_name))
            return False
    
    def install_from_file(self, file_path):
        """从文件安装多个插件"""
        print(self._("installing_from_file", file_path))
        
        if not os.path.exists(file_path):
            print(self._("file_not_found", file_path))
            return False
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                plugins = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
            
            if not plugins:
                print(self._("no_plugins_in_file"))
                return False
            
            # 使用线程池下载插件
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
                future_to_plugin = {executor.submit(self.install_plugin, plugin): plugin for plugin in plugins}
                
                for future in concurrent.futures.as_completed(future_to_plugin):
                    plugin = future_to_plugin[future]
                    try:
                        future.result()
                    except Exception as e:
                        print(f"{self._('error', e)}")
            
            print(self._("all_plugins_installed"))
            return True
        except Exception as e:
            print(self._("reading_file_failed", e))
            return False
    
    def get_plugin_version(self, plugin_name):
        """获取插件版本信息"""
        # 尝试从本地插件文件中提取版本信息
        plugin_path = os.path.join("plugins", f"{plugin_name}.py")
        if os.path.exists(plugin_path):
            try:
                with open(plugin_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 查找版本信息
                    import re
                    version_match = re.search(r'VERSION\s*=\s*["\'](.*?)["\']', content)
                    if version_match:
                        return version_match.group(1)
            except Exception as e:
                pass
        return "0.0.0"
    
    def get_remote_plugin_version(self, plugin_name):
        """获取远程插件版本信息"""
        try:
            import requests
            version_url = f"{self.current_mirror}{plugin_name}.json"
            response = requests.get(version_url)
            response.raise_for_status()
            version_data = response.json()
            return version_data.get("version", "0.0.0")
        except Exception as e:
            print(self._("error", e))
            return "0.0.0"
    
    def compare_versions(self, v1, v2):
        """比较版本号"""
        def normalize_version(v):
            return [int(x) for x in v.split(".") if x.isdigit()]
        
        v1_parts = normalize_version(v1)
        v2_parts = normalize_version(v2)
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1_part = v1_parts[i] if i < len(v1_parts) else 0
            v2_part = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1_part < v2_part:
                return -1
            elif v1_part > v2_part:
                return 1
        return 0
    
    def get_scd_version(self):
        """获取 scd 版本信息"""
        # 尝试从当前文件中提取版本信息
        scd_path = os.path.abspath(__file__)
        try:
            with open(scd_path, "r", encoding="utf-8") as f:
                content = f.read()
                # 查找版本信息
                import re
                version_match = re.search(r'VERSION\s*=\s*["\'](.*?)["\']', content)
                if version_match:
                    return version_match.group(1)
        except Exception as e:
            pass
        return "0.0.0"
    
    def get_remote_scd_version(self):
        """获取远程 scd 版本信息"""
        try:
            import requests
            version_url = "https://scl.ecuil.com/scd.json"
            response = requests.get(version_url)
            response.raise_for_status()
            version_data = response.json()
            return version_data.get("v", "0.0.0")
        except Exception as e:
            print(self._("error", e))
            return "0.0.0"
    
    def update_plugin(self, plugin_name):
        """更新插件"""
        if plugin_name == "scd":
            # 更新 scd 本身
            print(self._("updating_scd"))
            
            # 获取本地版本
            local_version = self.get_scd_version()
            print(self._("local_version", local_version))
            
            # 获取远程版本
            remote_version = self.get_remote_scd_version()
            print(self._("remote_version", remote_version))
            
            # 比较版本
            if self.compare_versions(local_version, remote_version) < 0:
                print(self._("found_new_version"))
                
                # 根据操作系统类型选择下载文件
                import platform
                system = platform.system()
                
                if system == "Windows":
                    scd_url = "https://scl.ecuil.com/scd.exe"
                    scd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scd.exe")
                elif system == "Linux":
                    scd_url = "https://scl.ecuil.com/scd"
                    scd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scd")
                else:
                    print(self._("unsupported_os"))
                    return False
                
                # 下载更新
                if self.download_file(scd_url, scd_path):
                    # 如果是 Linux，设置可执行权限
                    if system == "Linux":
                        try:
                            import os
                            os.chmod(scd_path, 0o755)
                        except Exception as e:
                            print(self._("error", e))
                    
                    print(self._("scd_updated"))
                    print(self._("run_new_scd", "文件" if system == "Windows" else "可执行文件"))
                    return True
                else:
                    print(self._("update_failed"))
                    return False
            else:
                print(self._("already_latest", "scd"))
                return True
        else:
            # 更新普通插件
            print(self._("updating_plugin", plugin_name))
            
            # 获取本地版本
            local_version = self.get_plugin_version(plugin_name)
            print(self._("local_version", local_version))
            
            # 获取远程版本
            remote_version = self.get_remote_plugin_version(plugin_name)
            print(self._("remote_version", remote_version))
            
            # 比较版本
            if self.compare_versions(local_version, remote_version) < 0:
                print(self._("found_new_version"))
                return self.install_plugin(plugin_name)
            else:
                print(self._("already_latest", f"插件 {plugin_name}"))
                return True
    
    def list_plugins(self, mode="local"):
        """列出可用插件"""
        if mode == "local":
            print(self._("listing_local_plugins"))
            plugins_dir = "plugins"
            if os.path.exists(plugins_dir):
                plugins = [f[:-3] for f in os.listdir(plugins_dir) if f.endswith(".py")]
                if plugins:
                    print(self._("installed_plugins"))
                    for plugin in plugins:
                        print(f"  - {plugin}")
                else:
                    print(self._("no_plugins_installed"))
            else:
                print(self._("plugins_dir_not_found"))
        elif mode == "web":
            print(self._("listing_web_plugins"))
            print(self._("fetching_plugins_from", self.current_mirror))
            try:
                # 尝试从 API 获取插件列表
                import requests
                plugins_url = f"{self.current_mirror}plugins.php"
                response = requests.get(plugins_url)
                response.raise_for_status()
                plugins_data = response.json()
                
                if plugins_data.get("status") == "success" and "plugins" in plugins_data:
                    plugins = plugins_data["plugins"]
                    if plugins:
                        print(self._("available_plugins"))
                        for plugin in plugins:
                            print(f"  - {plugin}")
                    else:
                        print(self._("no_available_plugins"))
                else:
                    print(self._("invalid_api_response"))
            except ImportError:
                print(self._("install_required_packages"))
            except Exception as e:
                print(self._("fetch_failed", e))
                print(self._("check_network"))
    
    def show_mirrors(self):
        """显示可用镜像源"""
        print(self._("available_mirrors"))
        for i, mirror in enumerate(self.mirrors):
            marker = "*" if mirror == self.current_mirror else " "
            print(f"{marker} [{i+1}] {mirror}")
    
    def run(self, args):
        """运行命令"""
        if args.command == "install":
            if args.file:
                self.install_from_file(args.file)
            else:
                for plugin in args.plugins:
                    self.install_plugin(plugin)
        elif args.command == "update":
            for plugin in args.plugins:
                self.update_plugin(plugin)
        elif args.command == "mirror":
            if args.url:
                self.add_mirror(args.url)
            else:
                self.show_mirrors()
        elif args.command == "list":
            if hasattr(args, 'mode') and args.mode:
                self.list_plugins(args.mode)
            else:
                self.list_plugins()
        elif args.command == "info":
            print(self._("scd_info"))
            print(self._("version"))
            print(self._("current_mirror", self.current_mirror))
            print(self._("available_mirrors_count", len(self.mirrors)))
            print(self._("cpu_cores", self.cpu_cores))
            print(self._("download_threads", self.threads))
            print(self._("current_language", self.language))
        elif args.command == "language":
            if args.lang:
                self.set_language(args.lang)
            else:
                print(self._("current_language", self.language))


def main():
    parser = argparse.ArgumentParser(description="SCL 插件下载器")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # install 命令
    install_parser = subparsers.add_parser("install", help="安装插件")
    install_parser.add_argument("plugins", nargs="*", help="要安装的插件名称")
    install_parser.add_argument("-f", "--file", help="包含插件名称的文件")
    install_parser.add_argument("-t", action="store_true", help="从 plugins.txt 安装")
    
    # update 命令
    update_parser = subparsers.add_parser("update", help="更新插件")
    update_parser.add_argument("plugins", nargs="*", help="要更新的插件名称")
    
    # mirror 命令
    mirror_parser = subparsers.add_parser("mirror", help="管理镜像源")
    mirror_parser.add_argument("url", nargs="?", help="要添加的镜像 URL")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出插件")
    list_parser.add_argument("mode", nargs="?", choices=["local", "web"], default="local", help="列出模式: local 或 web")
    
    # info 命令
    subparsers.add_parser("info", help="显示 scd 信息")
    
    # language 命令
    language_parser = subparsers.add_parser("language", help="管理语言设置")
    language_parser.add_argument("lang", nargs="?", choices=["en", "zh"], help="要设置的语言: en 或 zh")
    
    args = parser.parse_args()
    
    # 处理 -t 参数
    if args.command == "install" and args.t:
        args.file = "plugins.txt"
    
    if not args.command:
        parser.print_help()
        return
    
    downloader = SCDownloader()
    downloader.run(args)


if __name__ == "__main__":
    main()
