#!/usr/bin/env python3
"""Demo应用下载和管理工具"""

import os
import requests
import hashlib
from pathlib import Path
from typing import Dict, List
import json


class DemoAppDownloader:
    """Demo应用下载器"""
    
    def __init__(self):
        self.apps_dir = Path("demo_apps")
        self.apps_dir.mkdir(exist_ok=True)
        
        # 常用的测试应用列表
        self.demo_apps = {
            "calculator": {
                "name": "Android Calculator",
                "description": "Android系统计算器，适合基础UI测试",
                "package": "com.android.calculator2",
                "activity": "com.android.calculator2.Calculator",
                "download_url": None,  # 系统应用，无需下载
                "local_path": None,
                "test_elements": {
                    "digit_1": "com.android.calculator2:id/digit_1",
                    "digit_2": "com.android.calculator2:id/digit_2",
                    "op_add": "com.android.calculator2:id/op_add",
                    "eq": "com.android.calculator2:id/eq",
                    "result": "com.android.calculator2:id/result"
                }
            },
            "contacts": {
                "name": "Android Contacts",
                "description": "Android联系人应用，适合列表和表单测试",
                "package": "com.android.contacts",
                "activity": "com.android.contacts.activities.PeopleActivity",
                "download_url": None,
                "local_path": None,
                "test_elements": {
                    "add_contact": "com.android.contacts:id/floating_action_button",
                    "name_field": "com.android.contacts:id/editors"
                }
            },
            "settings": {
                "name": "Android Settings",
                "description": "Android设置应用，适合导航和配置测试",
                "package": "com.android.settings",
                "activity": "com.android.settings.Settings",
                "download_url": None,
                "local_path": None,
                "test_elements": {
                    "search": "com.android.settings:id/search_action_bar",
                    "wifi": "android:id/title"
                }
            },
            "chrome": {
                "name": "Chrome Browser",
                "description": "Chrome浏览器，适合Web测试",
                "package": "com.android.chrome",
                "activity": "com.google.android.apps.chrome.Main",
                "download_url": None,
                "local_path": None,
                "test_elements": {
                    "url_bar": "com.android.chrome:id/url_bar",
                    "menu": "com.android.chrome:id/menu_button"
                }
            },
            "demo_calculator": {
                "name": "Demo Calculator APK",
                "description": "第三方计算器Demo，用于自动化测试练习",
                "package": "com.example.calculator",
                "activity": "com.example.calculator.MainActivity",
                "download_url": "https://github.com/android/testing-samples/raw/main/ui/espresso/BasicSample/app/build/outputs/apk/debug/app-debug.apk",
                "local_path": "demo_apps/calculator_demo.apk",
                "test_elements": {
                    "button_1": "com.example.calculator:id/button1",
                    "button_plus": "com.example.calculator:id/buttonPlus",
                    "button_equals": "com.example.calculator:id/buttonEquals",
                    "display": "com.example.calculator:id/display"
                }
            }
        }
    
    def list_apps(self):
        """列出所有可用的Demo应用"""
        print("📱 可用的Demo测试应用:")
        print("=" * 80)
        
        for app_id, app_info in self.demo_apps.items():
            status = "✅ 系统应用" if not app_info["download_url"] else "📦 需要下载"
            
            if app_info["local_path"] and Path(app_info["local_path"]).exists():
                status = "✅ 已下载"
            elif app_info["download_url"]:
                status = "❌ 未下载"
            
            print(f"{app_id}:")
            print(f"  名称: {app_info['name']}")
            print(f"  描述: {app_info['description']}")
            print(f"  包名: {app_info['package']}")
            print(f"  状态: {status}")
            print()
    
    def download_app(self, app_id: str) -> bool:
        """下载指定的应用"""
        if app_id not in self.demo_apps:
            print(f"❌ 未找到应用: {app_id}")
            return False
        
        app_info = self.demo_apps[app_id]
        
        if not app_info["download_url"]:
            print(f"ℹ️  {app_info['name']} 是系统应用，无需下载")
            return True
        
        if app_info["local_path"] and Path(app_info["local_path"]).exists():
            print(f"✅ {app_info['name']} 已存在")
            return True
        
        print(f"📥 正在下载 {app_info['name']}...")
        
        try:
            response = requests.get(app_info["download_url"], stream=True)
            response.raise_for_status()
            
            local_path = Path(app_info["local_path"])
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ 下载完成: {local_path}")
            return True
            
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return False
    
    def install_app(self, app_id: str, device_id: str = None) -> bool:
        """安装应用到设备"""
        if app_id not in self.demo_apps:
            print(f"❌ 未找到应用: {app_id}")
            return False
        
        app_info = self.demo_apps[app_id]
        
        if not app_info["download_url"]:
            print(f"ℹ️  {app_info['name']} 是系统应用，无需安装")
            return True
        
        local_path = Path(app_info["local_path"])
        if not local_path.exists():
            print(f"❌ APK文件不存在，请先下载: {local_path}")
            return False
        
        # 构建adb安装命令
        adb_cmd = ["adb"]
        if device_id:
            adb_cmd.extend(["-s", device_id])
        adb_cmd.extend(["install", "-r", str(local_path)])
        
        print(f"📲 正在安装 {app_info['name']} 到设备...")
        
        try:
            import subprocess
            result = subprocess.run(adb_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 安装成功: {app_info['name']}")
                return True
            else:
                print(f"❌ 安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 安装过程出错: {e}")
            return False
    
    def generate_test_config(self, app_id: str, output_file: str = None):
        """生成测试配置文件"""
        if app_id not in self.demo_apps:
            print(f"❌ 未找到应用: {app_id}")
            return
        
        app_info = self.demo_apps[app_id]
        
        if not output_file:
            output_file = f"config/test_config_{app_id}.py"
        
        config_content = f'''"""
{app_info['name']} 测试配置
自动生成的配置文件
"""

class {app_id.title().replace('_', '')}Config:
    """测试配置类"""
    
    # 应用信息
    APP_PACKAGE = "{app_info['package']}"
    APP_ACTIVITY = "{app_info['activity']}"
    APP_NAME = "{app_info['name']}"
    
    # 元素选择器
    ELEMENTS = {{'''
        
        for element_name, element_id in app_info['test_elements'].items():
            config_content += f'''
        "{element_name.upper()}": "{element_id}",'''
        
        config_content += f'''
    }}
    
    # 测试数据
    TEST_DATA = {{
        "sample_input": "123",
        "expected_result": "123"
    }}
    
    @classmethod
    def get_element(cls, element_name: str) -> str:
        """获取元素选择器"""
        return cls.ELEMENTS.get(element_name.upper(), "")
    
    @classmethod
    def get_device_uri(cls, device_id: str = None) -> str:
        """获取设备URI"""
        if device_id:
            return f"android://127.0.0.1:5037/{{device_id}}?touch_method=MAXTOUCH"
        return "Android:///"
'''
        
        # 确保目录存在
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ 测试配置已生成: {output_file}")
    
    def generate_sample_test(self, app_id: str, output_file: str = None):
        """生成示例测试用例"""
        if app_id not in self.demo_apps:
            print(f"❌ 未找到应用: {app_id}")
            return
        
        app_info = self.demo_apps[app_id]
        
        if not output_file:
            output_file = f"tests/test_{app_id}_demo.py"
        
        test_content = f'''"""
{app_info['name']} 示例测试用例
自动生成的测试文件
"""

import pytest
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


class Test{app_id.title().replace('_', '')}:
    """测试类"""
    
    @pytest.fixture(scope="class")
    def app_setup(self):
        """应用启动设置"""
        # 连接设备
        auto_setup(__file__)
        device = connect_device("Android:///")
        poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
        
        # 启动应用
        start_app("{app_info['package']}")
        sleep(2)
        
        yield device, poco
        
        # 清理
        stop_app("{app_info['package']}")
    
    @pytest.mark.smoke
    def test_app_launch(self, app_setup):
        """测试应用启动"""
        device, poco = app_setup
        
        # 验证应用已启动
        assert poco(packageName="{app_info['package']}").exists()
        
        # 截图记录
        snapshot("app_launched.png")
    
    @pytest.mark.ui
    def test_basic_interaction(self, app_setup):
        """测试基本交互"""
        device, poco = app_setup
        
        # 这里添加具体的测试步骤
        # 根据应用类型自定义测试逻辑
        
        # 截图记录
        snapshot("basic_interaction.png")
        
        # 添加断言
        assert True  # 替换为实际的断言
'''
        
        # 确保目录存在
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"✅ 示例测试已生成: {output_file}")
    
    def create_demo_project(self, app_id: str, project_name: str = None):
        """创建完整的Demo测试项目"""
        if not project_name:
            project_name = f"{app_id}_demo_project"
        
        project_dir = Path(project_name)
        project_dir.mkdir(exist_ok=True)
        
        print(f"🚀 创建Demo项目: {project_name}")
        
        # 生成配置文件
        config_file = project_dir / f"config_{app_id}.py"
        self.generate_test_config(app_id, str(config_file))
        
        # 生成测试用例
        test_file = project_dir / f"test_{app_id}.py"
        self.generate_sample_test(app_id, str(test_file))
        
        # 创建运行脚本
        run_script = project_dir / "run_test.py"
        with open(run_script, 'w', encoding='utf-8') as f:
            f.write(f'''#!/usr/bin/env python3
"""运行 {app_id} 测试"""

import subprocess
import sys

def main():
    """运行测试"""
    cmd = [
        "python", "-m", "pytest", 
        "test_{app_id}.py",
        "-v",
        "--html=report.html",
        "--self-contained-html"
    ]
    
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
''')
        
        print(f"✅ Demo项目创建完成: {project_dir}")
        print(f"📁 项目结构:")
        print(f"  {project_dir}/")
        print(f"  ├── config_{app_id}.py")
        print(f"  ├── test_{app_id}.py")
        print(f"  └── run_test.py")


def main():
    """主函数"""
    import sys
    
    downloader = DemoAppDownloader()
    
    if len(sys.argv) == 1:
        downloader.list_apps()
        return
    
    command = sys.argv[1]
    
    if command == "list":
        downloader.list_apps()
    
    elif command == "download":
        if len(sys.argv) < 3:
            print("使用方法: python demo_app_downloader.py download <app_id>")
            return
        app_id = sys.argv[2]
        downloader.download_app(app_id)
    
    elif command == "install":
        if len(sys.argv) < 3:
            print("使用方法: python demo_app_downloader.py install <app_id> [device_id]")
            return
        app_id = sys.argv[2]
        device_id = sys.argv[3] if len(sys.argv) > 3 else None
        downloader.install_app(app_id, device_id)
    
    elif command == "config":
        if len(sys.argv) < 3:
            print("使用方法: python demo_app_downloader.py config <app_id> [output_file]")
            return
        app_id = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        downloader.generate_test_config(app_id, output_file)
    
    elif command == "test":
        if len(sys.argv) < 3:
            print("使用方法: python demo_app_downloader.py test <app_id> [output_file]")
            return
        app_id = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        downloader.generate_sample_test(app_id, output_file)
    
    elif command == "project":
        if len(sys.argv) < 3:
            print("使用方法: python demo_app_downloader.py project <app_id> [project_name]")
            return
        app_id = sys.argv[2]
        project_name = sys.argv[3] if len(sys.argv) > 3 else None
        downloader.create_demo_project(app_id, project_name)
    
    else:
        print("可用命令:")
        print("  list                    # 列出所有Demo应用")
        print("  download <app_id>       # 下载指定应用")
        print("  install <app_id> [device] # 安装应用到设备")
        print("  config <app_id>         # 生成测试配置")
        print("  test <app_id>           # 生成示例测试")
        print("  project <app_id>        # 创建完整Demo项目")


if __name__ == "__main__":
    main()