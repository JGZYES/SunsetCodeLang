#!/usr/bin/env python3
"""
SCL Package Manager (SDP)
Package manager for SCL plugins - similar to apt/yum/composer
"""

import os
import sys
import json
import urllib.request
import urllib.parse

class SCLEPackageManager:
    # Language translations
    TRANSLATIONS = {
        "english": {
            "installing": "Installing",
            "updating": "Updating",
            "reinstalling": "Reinstalling",
            "removing": "Removing",
            "downloading": "Downloading",
            "downloaded": "Downloaded",
            "installed": "installed successfully",
            "updated": "updated successfully",
            "reinstalled": "reinstalled successfully",
            "removed": "removed successfully",
            "already_installed": "is already installed",
            "not_installed": "is not installed",
            "use_install": "Use 'sdp install' to install",
            "use_update": "Use 'sdp update' to update",
            "no_plugins": "No plugins installed",
            "local_plugins": "Local plugins:",
            "community_plugins": "Community plugins:",
            "upgradable_plugins": "Plugins available for upgrade:",
            "testing_network": "Testing network connectivity...",
            "network_ok": "Network connection OK",
            "network_fail": "Network connection failed",
            "config_saved": "Configuration saved",
            "config_created": "Created",
            "language_set": "Language set to",
            "available_languages": "Available languages:",
            "unknown_command": "Unknown command",
            "usage": "Usage",
            "options": "Options",
            "commands": "Commands"
        },
        "chinese_simplified": {
            "installing": "正在安装",
            "updating": "正在更新",
            "reinstalling": "正在重新安装",
            "removing": "正在删除",
            "downloading": "正在下载",
            "downloaded": "已下载",
            "installed": "安装成功",
            "updated": "更新成功",
            "reinstalled": "重新安装成功",
            "removed": "删除成功",
            "already_installed": "已安装",
            "not_installed": "未安装",
            "use_install": "使用 'sdp install' 安装",
            "use_update": "使用 'sdp update' 更新",
            "no_plugins": "没有已安装的插件",
            "local_plugins": "本地插件:",
            "community_plugins": "社区插件:",
            "upgradable_plugins": "可升级的插件:",
            "testing_network": "测试网络连接...",
            "network_ok": "网络连接正常",
            "network_fail": "网络连接失败",
            "config_saved": "配置已保存",
            "config_created": "已创建",
            "language_set": "语言已设置为",
            "available_languages": "可用语言:",
            "unknown_command": "未知命令",
            "usage": "用法",
            "options": "选项",
            "commands": "命令"
        },
        "chinese_hongkong": {
            "installing": "正在安裝",
            "updating": "正在更新",
            "reinstalling": "正在重新安裝",
            "removing": "正在移除",
            "downloading": "正在下載",
            "downloaded": "已下載",
            "installed": "安裝成功",
            "updated": "更新成功",
            "reinstalled": "重新安裝成功",
            "removed": "移除成功",
            "already_installed": "已安裝",
            "not_installed": "未安裝",
            "use_install": "使用 'sdp install' 安裝",
            "use_update": "使用 'sdp update' 更新",
            "no_plugins": "沒有已安裝的插件",
            "local_plugins": "本地插件:",
            "community_plugins": "社區插件:",
            "upgradable_plugins": "可升級的插件:",
            "testing_network": "測試網絡連接...",
            "network_ok": "網絡連接正常",
            "network_fail": "網絡連接失敗",
            "config_saved": "配置已保存",
            "config_created": "已創建",
            "language_set": "語言已設置為",
            "available_languages": "可用語言:",
            "unknown_command": "未知指令",
            "usage": "用法",
            "options": "選項",
            "commands": "指令"
        },
        "classical_chinese": {
            "installing": "正在安裝",
            "updating": "正在更新",
            "reinstalling": "正在重裝",
            "removing": "正在移除",
            "downloading": "正在下載",
            "downloaded": "已下載",
            "installed": "安裝畢",
            "updated": "更新畢",
            "reinstalled": "重裝畢",
            "removed": "移除畢",
            "already_installed": "已安裝矣",
            "not_installed": "未安裝",
            "use_install": "以 'sdp install' 安裝之",
            "use_update": "以 'sdp update' 更新之",
            "no_plugins": "無已安裝之插件",
            "local_plugins": "本地插件:",
            "community_plugins": "社群插件:",
            "upgradable_plugins": "可升級之插件:",
            "testing_network": "測試網絡...",
            "network_ok": "網絡通暢",
            "network_fail": "網絡不通",
            "config_saved": "配置已存",
            "config_created": "已創建",
            "language_set": "語言已設為",
            "available_languages": "可用語言:",
            "unknown_command": "未知之令",
            "usage": "用法",
            "options": "選項",
            "commands": "指令"
        },
        "latin": {
            "installing": "Installans",
            "updating": "Actualizans",
            "reinstalling": "Reinstallans",
            "removing": "Removens",
            "downloading": "Downloadens",
            "downloaded": "Downloadatum",
            "installed": "installatum est",
            "updated": "actualizatum est",
            "reinstalled": "reinstallatum est",
            "removed": "removitum est",
            "already_installed": "iam installatum est",
            "not_installed": "non installatum est",
            "use_install": "Utere 'sdp install' ad installandum",
            "use_update": "Utere 'sdp update' ad actualizandum",
            "no_plugins": "Nulla plugins installata",
            "local_plugins": "Plugins locales:",
            "community_plugins": "Plugins communitatis:",
            "upgradable_plugins": "Plugins actualizabiles:",
            "testing_network": "Testans conexionem rete...",
            "network_ok": "Conexio retis bona est",
            "network_fail": "Conexio retis fallita est",
            "config_saved": "Configuratio servata est",
            "config_created": "Creatum est",
            "language_set": "Lingua posita est ad",
            "available_languages": "Linguae disponibiles:",
            "unknown_command": "Commandum ignotum",
            "usage": "Usus",
            "options": "Optiones",
            "commands": "Commanda"
        },
        "portuguese": {
            "installing": "Instalando",
            "updating": "Atualizando",
            "reinstalling": "Reinstalando",
            "removing": "Removendo",
            "downloading": "Baixando",
            "downloaded": "Baixado",
            "installed": "instalado com sucesso",
            "updated": "atualizado com sucesso",
            "reinstalled": "reinstalado com sucesso",
            "removed": "removido com sucesso",
            "already_installed": "já está instalado",
            "not_installed": "não está instalado",
            "use_install": "Use 'sdp install' para instalar",
            "use_update": "Use 'sdp update' para atualizar",
            "no_plugins": "Nenhum plugin instalado",
            "local_plugins": "Plugins locais:",
            "community_plugins": "Plugins da comunidade:",
            "upgradable_plugins": "Plugins disponíveis para atualização:",
            "testing_network": "Testando conectividade de rede...",
            "network_ok": "Conexão de rede OK",
            "network_fail": "Falha na conexão de rede",
            "config_saved": "Configuração salva",
            "config_created": "Criado",
            "language_set": "Idioma definido para",
            "available_languages": "Idiomas disponíveis:",
            "unknown_command": "Comando desconhecido",
            "usage": "Uso",
            "options": "Opções",
            "commands": "Comandos"
        },
        "korean": {
            "installing": "설치 중",
            "updating": "업데이트 중",
            "reinstalling": "재설치 중",
            "removing": "제거 중",
            "downloading": "다운로드 중",
            "downloaded": "다운로드 완료",
            "installed": "설치 성공",
            "updated": "업데이트 성공",
            "reinstalled": "재설치 성공",
            "removed": "제거 성공",
            "already_installed": "이미 설치됨",
            "not_installed": "설치되지 않음",
            "use_install": "'sdp install'로 설치하세요",
            "use_update": "'sdp update'로 업데이트하세요",
            "no_plugins": "설치된 플러그인 없음",
            "local_plugins": "로컬 플러그인:",
            "community_plugins": "커뮤니티 플러그인:",
            "upgradable_plugins": "업그레이드 가능한 플러그인:",
            "testing_network": "네트워크 연결 테스트 중...",
            "network_ok": "네트워크 연결 정상",
            "network_fail": "네트워크 연결 실패",
            "config_saved": "설정 저장됨",
            "config_created": "생성됨",
            "language_set": "언어가 설정됨",
            "available_languages": "사용 가능한 언어:",
            "unknown_command": "알 수 없는 명령",
            "usage": "사용법",
            "options": "옵션",
            "commands": "명령"
        }
    }

    LANGUAGE_NAMES = {
        "english": "English",
        "chinese_simplified": "简体中文",
        "chinese_hongkong": "中文(香港)",
        "classical_chinese": "文言文",
        "latin": "Latin",
        "portuguese": "Português",
        "korean": "한국어"
    }

    # Acknowledgments list
    ACKNOWLEDGMENTS = [
        "JGZ_YES - Create SunsetCodeLang(scl) & SunsetCodeLang-DownloadPlugins(sdp)",
        "XiaoXiaoBai - Termux Adapt"
    ]

    def __init__(self):
        self.base_url = "https://scl.ecuil.com/forum/api/download.php"
        self.api_url = "https://scl.ecuil.com/forum/api/packages.php"
        self.run_plugins_url = "https://scl.ecuil.com/run/plugins/"
        self.plugins_dir = "./plugins"
        self.config_file = "composer.json"
        self.settings_file = "sdp_settings.json"
        self.version = "1.0"
        self.language = self.load_language()
        self.repositories = self.load_repositories()
        
    def t(self, key):
        """Get translation for a key"""
        return self.TRANSLATIONS.get(self.language, self.TRANSLATIONS["english"]).get(key, key)
    
    def load_language(self):
        """Load language from settings file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    lang = settings.get('language', 'english')
                    if lang in self.TRANSLATIONS:
                        return lang
            except Exception:
                pass
        return "english"
    
    def save_language(self, language):
        """Save language to settings file"""
        if language not in self.TRANSLATIONS:
            return False
        
        settings = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except Exception:
                pass
        
        settings['language'] = language
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            self.error(f"Failed to save language setting: {e}")
            return False
    
    def set_language(self, language):
        """Set the interface language"""
        lang_map = {
            "english": "english",
            "chinese": "chinese_simplified",
            "chinese_simplified": "chinese_simplified",
            "简体中文": "chinese_simplified",
            "chinese_hongkong": "chinese_hongkong",
            "中文(香港)": "chinese_hongkong",
            "classical_chinese": "classical_chinese",
            "文言文": "classical_chinese",
            "latin": "latin",
            "portuguese": "portuguese",
            "korean": "korean"
        }
        
        normalized_lang = lang_map.get(language.lower(), language.lower())
        
        if normalized_lang not in self.TRANSLATIONS:
            self.error(f"Unknown language: {language}")
            self.show_available_languages()
            return False
        
        if self.save_language(normalized_lang):
            self.language = normalized_lang
            self.success(f"{self.t('language_set')} {self.LANGUAGE_NAMES[normalized_lang]}")
            return True
        return False
    
    def show_available_languages(self):
        """Show available languages"""
        self.log(self.t("available_languages"))
        for key, name in self.LANGUAGE_NAMES.items():
            marker = " *" if key == self.language else ""
            self.log(f"  {key}: {name}{marker}")
    
    def load_repositories(self):
        """Load repositories from settings file"""
        default_repos = [
            {
                "name": "official",
                "base_url": "https://scl.ecuil.com/forum/api/download.php",
                "api_url": "https://scl.ecuil.com/forum/api/packages.php",
                "run_plugins_url": "https://scl.ecuil.com/run/plugins/"
            },
            {
                "name": "official_hk",
                "base_url": "https://hk-api.ecuil.com/scl/repo/api/download.php",
                "api_url": "https://hk-api.ecuil.com/scl/repo/api/packages.php",
                "run_plugins_url": "https://hk-api.ecuil.com/scl/repo/"
            }
        ]
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    repos = settings.get('repositories', [])
                    if repos:
                        return repos
            except Exception:
                pass
        return default_repos
    
    def save_repositories(self):
        """Save repositories to settings file"""
        settings = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except Exception:
                pass
        
        settings['repositories'] = self.repositories
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            self.error(f"Failed to save repositories: {e}")
            return False
    
    def add_repository(self, repo_url):
        """Add a new repository"""
        # Normalize URL
        repo_url = repo_url.rstrip('/')
        
        # Check if already exists
        for repo in self.repositories:
            if repo.get('run_plugins_url', '').rstrip('/') == repo_url or \
               repo.get('base_url', '').rstrip('/') == repo_url:
                self.warning(f"Repository already exists: {repo_url}")
                return False
        
        # Try to detect repository structure
        # Support formats:
        # 1. https://example.com/run/plugins/ -> direct plugin URL
        # 2. https://example.com/ -> try to detect API endpoints
        
        new_repo = {
            "name": f"repo_{len(self.repositories)}",
            "base_url": f"{repo_url}/api/download.php" if not repo_url.endswith('.php') else repo_url,
            "api_url": f"{repo_url}/api/packages.php" if not repo_url.endswith('.php') else repo_url.replace('download.php', 'packages.php'),
            "run_plugins_url": repo_url if '/run/plugins' in repo_url else f"{repo_url}/run/plugins/"
        }
        
        # Test repository
        try:
            test_url = f"{new_repo['run_plugins_url']}test.py"
            req = urllib.request.Request(test_url, method='HEAD')
            req.add_header('User-Agent', 'SCL-PackageManager/1.0')
            with urllib.request.urlopen(req, timeout=5) as response:
                pass
        except:
            pass  # Ignore test failure, repository might still work
        
        self.repositories.append(new_repo)
        
        if self.save_repositories():
            self.success(f"Repository added: {repo_url}")
            return True
        return False
    
    def remove_repository(self, repo_name_or_url):
        """Remove a repository"""
        for i, repo in enumerate(self.repositories):
            if repo.get('name') == repo_name_or_url or \
               repo.get('run_plugins_url', '').rstrip('/') == repo_name_or_url.rstrip('/') or \
               repo.get('base_url', '').rstrip('/') == repo_name_or_url.rstrip('/'):
                if i == 0 and len(self.repositories) == 1:
                    self.error("Cannot remove the last repository")
                    return False
                removed = self.repositories.pop(i)
                if self.save_repositories():
                    self.success(f"Repository removed: {removed.get('name', repo_name_or_url)}")
                    return True
                return False
        
        self.error(f"Repository not found: {repo_name_or_url}")
        return False
    
    def list_repositories(self):
        """List all repositories"""
        self.log("Configured repositories:")
        self.log("-" * 60)
        for i, repo in enumerate(self.repositories, 1):
            name = repo.get('name', f'repo_{i}')
            url = repo.get('run_plugins_url', repo.get('base_url', 'Unknown'))
            marker = " (default)" if i == 1 else ""
            self.log(f"{i}. {name}{marker}")
            self.log(f"   URL: {url}")
    
    def log(self, message):
        print(message)
    
    def error(self, message):
        print(f"Error: {message}", file=sys.stderr)
    
    def success(self, message):
        print(f"✓ {message}")
    
    def warning(self, message):
        print(f"⚠ {message}")
    
    def ensure_plugins_dir(self):
        os.makedirs(self.plugins_dir, exist_ok=True)
    
    def get_installed_plugins(self):
        if not os.path.exists(self.plugins_dir):
            return []
        
        plugins = []
        for file in os.listdir(self.plugins_dir):
            if file.endswith('.py') and file != '__init__.py':
                plugin_name = file[:-3]
                plugins.append(plugin_name.lower())
        return plugins
    
    def get_plugin_info(self, plugin_name):
        try:
            req = urllib.request.Request(f"{self.api_url}?action=info&name={plugin_name.lower()}")
            req.add_header('User-Agent', 'SCL-PackageManager/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if data.get('success'):
                        return data.get('package', None)
        except Exception as e:
            self.error(f"Failed to get plugin info: {e}")
        return None
    
    def download_plugin(self, plugin_name):
        self.log(f"{self.t('downloading')} {plugin_name}...")
        
        # Try each repository in order
        for i, repo in enumerate(self.repositories):
            repo_name = repo.get('name', f'repo_{i}')
            run_plugins_url = repo.get('run_plugins_url', '')
            base_url = repo.get('base_url', '')
            
            try:
                # Try run_plugins_url first
                if run_plugins_url:
                    run_url = f"{run_plugins_url}{plugin_name.lower()}.py"
                    req = urllib.request.Request(run_url)
                    req.add_header('User-Agent', 'SCL-PackageManager/1.0')
                    
                    try:
                        with urllib.request.urlopen(req, timeout=15) as response:
                            if response.status == 200:
                                content = response.read()
                                self.success(f"{self.t('downloaded')} {len(content)} bytes from {repo_name}")
                                return content
                    except urllib.error.HTTPError as e:
                        if e.code != 404:
                            raise
                
                # Try base_url as fallback
                if base_url:
                    url = f"{base_url}?name={plugin_name.lower()}"
                    req = urllib.request.Request(url)
                    req.add_header('User-Agent', 'SCL-PackageManager/1.0')
                    
                    with urllib.request.urlopen(req, timeout=30) as response:
                        content = response.read()
                        content_type = response.headers.get('Content-Type', '')
                        
                        if 'application/json' in content_type:
                            data = json.loads(content.decode('utf-8'))
                            if data.get('error'):
                                continue  # Try next repository
                            return None
                        
                        self.success(f"{self.t('downloaded')} {len(content)} bytes from {repo_name}")
                        return content
                        
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue  # Try next repository
                self.warning(f"{repo_name}: HTTP {e.code}")
            except Exception as e:
                self.warning(f"{repo_name}: {e}")
                continue
        
        self.error(f"Plugin '{plugin_name}' not found in any repository")
        return None
    
    def install_plugin(self, plugin_name):
        self.ensure_plugins_dir()
        
        installed = self.get_installed_plugins()
        if plugin_name.lower() in installed:
            self.warning(f"Plugin '{plugin_name}' {self.t('already_installed')}")
            self.log(self.t('use_update'))
            return False
        
        content = self.download_plugin(plugin_name)
        if not content:
            return False
        
        dest_path = os.path.join(self.plugins_dir, f"{plugin_name.lower()}.py")
        with open(dest_path, 'wb') as f:
            f.write(content)
        
        self.success(f"Plugin '{plugin_name}' {self.t('installed')}")
        self.log(f"Usage: simp{{{plugin_name}}}")
        return True

    def install_plugins(self, plugin_names):
        """Install multiple plugins at once"""
        self.ensure_plugins_dir()
        
        installed_count = 0
        failed_count = 0
        
        for plugin_name in plugin_names:
            self.log(f"\n=== Installing {plugin_name} ===")
            if self.install_plugin(plugin_name):
                installed_count += 1
            else:
                failed_count += 1
        
        self.log(f"\n=== Summary ===")
        self.success(f"Successfully installed: {installed_count}")
        if failed_count > 0:
            self.error(f"Failed to install: {failed_count}")
        
        return installed_count > 0
    
    def update_plugin(self, plugin_name):
        self.ensure_plugins_dir()
        
        installed = self.get_installed_plugins()
        if plugin_name.lower() not in installed:
            self.error(f"Plugin '{plugin_name}' {self.t('not_installed')}")
            self.log(self.t('use_install'))
            return False
        
        content = self.download_plugin(plugin_name)
        if not content:
            return False
        
        dest_path = os.path.join(self.plugins_dir, f"{plugin_name.lower()}.py")
        with open(dest_path, 'wb') as f:
            f.write(content)
        
        self.success(f"Plugin '{plugin_name}' {self.t('updated')}")
        return True

    def update_plugins(self, plugin_names=None):
        """Update multiple plugins at once. If no plugins specified, update all installed plugins"""
        self.ensure_plugins_dir()
        
        if not plugin_names:
            plugin_names = self.get_installed_plugins()
            if not plugin_names:
                self.log(self.t('no_plugins'))
                return False
        
        updated_count = 0
        failed_count = 0
        
        for plugin_name in plugin_names:
            self.log(f"\n=== Updating {plugin_name} ===")
            if self.update_plugin(plugin_name):
                updated_count += 1
            else:
                failed_count += 1
        
        self.log(f"\n=== Summary ===")
        self.success(f"Successfully updated: {updated_count}")
        if failed_count > 0:
            self.error(f"Failed to update: {failed_count}")
        
        return updated_count > 0
    
    def reinstall_plugin(self, plugin_name):
        self.ensure_plugins_dir()
        
        installed = self.get_installed_plugins()
        if plugin_name.lower() not in installed:
            self.error(f"Plugin '{plugin_name}' {self.t('not_installed')}")
            self.log(self.t('use_install'))
            return False
        
        self.log(f"{self.t('reinstalling')} {plugin_name}...")
        
        content = self.download_plugin(plugin_name)
        if not content:
            return False
        
        dest_path = os.path.join(self.plugins_dir, f"{plugin_name.lower()}.py")
        with open(dest_path, 'wb') as f:
            f.write(content)
        
        self.success(f"Plugin '{plugin_name}' {self.t('reinstalled')}")
        return True
    
    def remove_plugin(self, plugin_name):
        installed = self.get_installed_plugins()
        if plugin_name.lower() not in installed:
            self.error(f"Plugin '{plugin_name}' {self.t('not_installed')}")
            return False
        
        dest_path = os.path.join(self.plugins_dir, f"{plugin_name.lower()}.py")
        os.remove(dest_path)
        
        self.success(f"Plugin '{plugin_name}' {self.t('removed')}")
        return True
    
    def autoremove_plugins(self):
        installed = self.get_installed_plugins()
        if not installed:
            self.log(self.t('no_plugins'))
            return True
        
        self.log("Checking for unused plugins...")
        self.warning("This feature requires dependency tracking")
        self.log("Currently removing all installed plugins")
        
        for plugin_name in installed:
            self.remove_plugin(plugin_name)
        
        self.success("All plugins removed")
        return True
    
    def test_network(self):
        self.log(self.t('testing_network'))
        
        test_urls = [
            "https://scl.ecuil.com",
            "https://ssl.ecuil.com",
            "https://tg.ecuil.com"
        ]
        
        for url in test_urls:
            try:
                req = urllib.request.Request(url, method='HEAD')
                req.add_header('User-Agent', 'SCL-PackageManager/1.0')
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status == 200:
                        self.success(f"{url} - OK")
                    else:
                        self.warning(f"{url} - HTTP {response.status}")
            except Exception as e:
                self.error(f"{url} - Failed: {e}")
        
        return True
    
    def list_plugins(self, mode='community'):
        if mode == 'local':
            self.list_local_plugins()
        elif mode == 'upgraded':
            self.list_upgraded_plugins()
        else:
            self.list_community_plugins()
    
    def list_local_plugins(self):
        self.log(self.t('local_plugins'))
        self.log("-" * 60)
        
        installed = self.get_installed_plugins()
        if not installed:
            self.log(self.t('no_plugins'))
            return
        
        for i, plugin in enumerate(installed, 1):
            plugin_path = os.path.join(self.plugins_dir, f"{plugin}.py")
            size = os.path.getsize(plugin_path) if os.path.exists(plugin_path) else 0
            self.log(f"{i}. {plugin} ({size} bytes)")
    
    def search_plugins(self, query):
        """Search for plugins by name or description"""
        self.log(f"Searching for plugins matching '{query}'...")
        self.log("-" * 60)
        
        try:
            req = urllib.request.Request(f"{self.api_url}?action=search&query={urllib.parse.quote(query)}")
            req.add_header('User-Agent', 'SCL-PackageManager/1.0')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status != 200:
                    self.error(f"Failed to search: HTTP {response.status}")
                    return
                
                data = json.loads(response.read().decode('utf-8'))
                
                if data.get('success'):
                    packages = data.get('packages', [])
                    installed = self.get_installed_plugins()
                    
                    if not packages:
                        self.log("No plugins found matching your query")
                        return
                    
                    for i, pkg in enumerate(packages, 1):
                        rating = pkg['rating_count'] > 0 and round(pkg['rating'] / pkg['rating_count'], 1) or 'N/A'
                        status = "✓ Installed" if pkg['name'].lower() in installed else ""
                        
                        self.log(f"{i}. {pkg['name']}")
                        self.log(f"   Description: {pkg['description']}")
                        self.log(f"   Category: {pkg['category']} | Version: {pkg['version']} | Author: {pkg['author_name']}")
                        self.log(f"   Downloads: {pkg['downloads']} | Rating: {rating} {status}")
                        self.log("")
                else:
                    self.error(f"Failed to search: {data.get('error', 'Unknown error')}")
                    
        except Exception as e:
            self.error(f"Failed to search: {e}")

    def list_community_plugins(self):
        self.log(self.t('community_plugins'))
        self.log("-" * 60)
        
        try:
            req = urllib.request.Request(f"{self.api_url}?action=list")
            req.add_header('User-Agent', 'SCL-PackageManager/1.0')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status != 200:
                    self.error(f"Failed to fetch list: HTTP {response.status}")
                    return
                
                data = json.loads(response.read().decode('utf-8'))
                
                if data.get('success'):
                    packages = data.get('packages', [])
                    installed = self.get_installed_plugins()
                    
                    for i, pkg in enumerate(packages, 1):
                        rating = pkg['rating_count'] > 0 and round(pkg['rating'] / pkg['rating_count'], 1) or 'N/A'
                        status = "✓ Installed" if pkg['name'].lower() in installed else ""
                        
                        self.log(f"{i}. {pkg['name']}")
                        self.log(f"   Description: {pkg['description']}")
                        self.log(f"   Category: {pkg['category']} | Version: {pkg['version']} | Author: {pkg['author_name']}")
                        self.log(f"   Downloads: {pkg['downloads']} | Rating: {rating} {status}")
                        self.log("")
                else:
                    self.error(f"Failed to fetch list: {data.get('error', 'Unknown error')}")
                    
        except Exception as e:
            self.error(f"Failed to fetch list: {e}")
    
    def list_upgraded_plugins(self):
        self.log(self.t('upgradable_plugins'))
        self.log("-" * 60)
        
        installed = self.get_installed_plugins()
        if not installed:
            self.log(self.t('no_plugins'))
            return
        
        for plugin_name in installed:
            info = self.get_plugin_info(plugin_name)
            if info:
                self.log(f"{plugin_name} - Latest: {info.get('version', 'Unknown')}")
            else:
                self.log(f"{plugin_name} - Version info unavailable")
    
    def load_composer_config(self):
        if not os.path.exists(self.config_file):
            return None
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.error(f"Failed to load {self.config_file}: {e}")
            return None
    
    def save_composer_config(self, config):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            self.success(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.error(f"Failed to save {self.config_file}: {e}")
    
    def init_composer(self):
        if os.path.exists(self.config_file):
            self.warning(f"{self.config_file} already exists")
            return
        
        config = {
            "name": "scl-project",
            "description": "SCL Project",
            "require": {},
            "version": "1.0.0"
        }
        
        self.save_composer_config(config)
        self.log(f"Created {self.config_file}")
    
    def show_acknowledgments(self):
        """Show acknowledgments list"""
        self.log("=" * 60)
        self.log("SCL Package Manager - Acknowledgments")
        self.log("=" * 60)
        self.log("Special thanks to everyone who has contributed to SCL:")
        print()
        for i, person in enumerate(self.ACKNOWLEDGMENTS, 1):
            self.log(f"{i}. {person}")
        print()
        self.log("Without your contributions, SCL wouldn't be what it is today!")
        self.log("=" * 60)

    def show_help(self):
        self.log("=" * 60)
        self.log("SCL Package Manager (SDP) v" + self.version)
        self.log("=" * 60)
        print()
        self.log("Usage: sdp [command] [options]")
        print()
        self.log("Commands:")
        self.log("  install <plugin>     Install a plugin")
        self.log("  install-multi <plugin1> <plugin2>... Install multiple plugins")
        self.log("  update <plugin>      Update a plugin")
        self.log("  update-all          Update all installed plugins")
        self.log("  update-multi <plugin1> <plugin2>... Update multiple plugins")
        self.log("  reinstall <plugin>   Reinstall a plugin")
        self.log("  remove <plugin>      Remove a plugin")
        self.log("  autoremove           Auto-remove unused plugins")
        print()
        self.log("  search <query>       Search for plugins")
        self.log("  test                Test network connectivity")
        self.log("  list [option]       List plugins")
        self.log("    -lw               List community plugins (default)")
        self.log("    -local            List local plugins")
        self.log("    -upgraded         List upgradable plugins")
        self.log("  -u, --upgrade       List plugins available for upgrade")
        self.log("  -a, --all           List all plugins in current repository")
        print()
        self.log("  init                Initialize composer.json")
        self.log("  add <url>           Add a plugin repository")
        self.log("  remove-repo <name>  Remove a repository")
        self.log("  repos               List all repositories")
        self.log("  setting -lang       Set language (english/chinese_simplified/chinese_hongkong/classical_chinese/latin/portuguese/korean)")
        self.log("  ae                  Show acknowledgments")
        self.log("  help                Show this help")
        print()
        self.log("Examples:")
        self.log("  sdp install basic")
        self.log("  sdp install-multi basic color fileio")
        self.log("  sdp update basic")
        self.log("  sdp update-all")
        self.log("  sdp search text")
        self.log("  sdp list -local")
        self.log("  sdp test")
        self.log("  sdp add https://scl.ecuil.com/run/plugins/")
        self.log("  sdp repos")
        self.log("  sdp ae")
        print()
        self.log("Configuration:")
        self.log("  composer.json - Local package configuration")
        self.log("  sdp_settings.json - SDP settings")
        self.log("  Use 'sdp init' to create composer.json")
        self.log("=" * 60)

def main():
    if len(sys.argv) < 2:
        manager = SCLEPackageManager()
        manager.show_help()
        return
    
    # Check for short options first
    if sys.argv[1] in ['-u', '--upgrade']:
        manager = SCLEPackageManager()
        manager.list_plugins('upgraded')
        return
    elif sys.argv[1] in ['-a', '--all']:
        manager = SCLEPackageManager()
        manager.list_plugins('community')
        return
    
    command = sys.argv[1].lower()
    manager = SCLEPackageManager()
    
    if command == 'help' or command == '-h' or command == '--help':
        manager.show_help()
    
    elif command == 'ae':
        manager.show_acknowledgments()
    
    elif command == 'install':
        if len(sys.argv) < 3:
            manager.error("Usage: sdp install <plugin_name>")
            return
        manager.install_plugin(sys.argv[2])
    
    elif command == 'install-multi':
        if len(sys.argv) < 3:
            manager.error("Usage: sdp install-multi <plugin1> <plugin2> ...")
            return
        manager.install_plugins(sys.argv[2:])
    
    elif command == 'update':
        if len(sys.argv) < 3:
            manager.error("Usage: sdp update <plugin_name>")
            return
        manager.update_plugin(sys.argv[2])
    
    elif command == 'update-all':
        manager.update_plugins()
    
    elif command == 'update-multi':
        if len(sys.argv) < 3:
            manager.error("Usage: sdp update-multi <plugin1> <plugin2> ...")
            return
        manager.update_plugins(sys.argv[2:])
    
    elif command == 'reinstall':
        if len(sys.argv) < 3:
            manager.error("Usage: sdp reinstall <plugin_name>")
            return
        manager.reinstall_plugin(sys.argv[2])
    
    elif command == 'remove':
        if len(sys.argv) < 3:
            manager.error("Usage: sdp remove <plugin_name>")
            return
        manager.remove_plugin(sys.argv[2])
    
    elif command == 'autoremove':
        manager.autoremove_plugins()
    
    elif command == 'search':
        if len(sys.argv) < 3:
            manager.error("Usage: sdp search <query>")
            return
        manager.search_plugins(sys.argv[2])
    
    elif command == 'test':
        manager.test_network()
    
    elif command == 'list':
        if len(sys.argv) >= 3:
            option = sys.argv[2].lower()
            if option == '-lw':
                manager.list_plugins('community')
            elif option == '-local':
                manager.list_plugins('local')
            elif option == '-upgraded':
                manager.list_plugins('upgraded')
            else:
                manager.error(f"Unknown option: {option}")
                manager.log("Use -lw, -local, or -upgraded")
        else:
            manager.list_plugins('community')
    
    elif command == 'init':
        manager.init_composer()
    
    elif command == 'add':
        if len(sys.argv) < 3:
            manager.error("Usage: sdp add <repository_url>")
            manager.log("Example: sdp add https://scl.ecuil.com/run/plugins/")
            return
        manager.add_repository(sys.argv[2])
    
    elif command == 'remove-repo':
        if len(sys.argv) < 3:
            manager.error("Usage: sdp remove-repo <repository_name_or_url>")
            manager.list_repositories()
            return
        manager.remove_repository(sys.argv[2])
    
    elif command == 'repos':
        manager.list_repositories()
    
    elif command == 'setting':
        if len(sys.argv) < 3:
            manager.error("Usage: sdp setting -lang <language>")
            manager.log("Available languages:")
            manager.show_available_languages()
            return
        
        subcommand = sys.argv[2].lower()
        if subcommand == '-lang' or subcommand == '--lang' or subcommand == 'lang':
            if len(sys.argv) < 4:
                manager.error("Usage: sdp setting -lang <language>")
                manager.show_available_languages()
                return
            manager.set_language(sys.argv[3])
        else:
            manager.error(f"Unknown setting: {subcommand}")
            manager.log("Use 'sdp setting -lang <language>'")
    
    else:
        manager.error(f"Unknown command: {command}")
        manager.log("Use 'sdp help' for usage information")

if __name__ == "__main__":
    main()
