#!/usr/bin/env python3
"""设备管理工具"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from airtest.core.android.adb import ADB


class DeviceManager:
    """设备管理器"""
    
    def __init__(self):
        self.adb = ADB()
        self.config_file = Path("config/devices.json")
    
    def get_available_devices(self) -> List[Dict[str, str]]:
        """获取所有可用设备"""
        devices = []
        
        try:
            # 获取Android设备
            android_devices = self.adb.devices()
            for device_id, status in android_devices:
                if status == "device":
                    device_info = self._get_android_device_info(device_id)
                    devices.append({
                        "id": device_id,
                        "platform": "android",
                        "status": status,
                        "name": device_info.get("name", "Unknown"),
                        "version": device_info.get("version", "Unknown"),
                        "uri": f"android://127.0.0.1:5037/{device_id}?touch_method=MAXTOUCH"
                    })
        except Exception as e:
            print(f"获取Android设备失败: {e}")
        
        try:
            # 获取iOS设备 (如果安装了tidevice)
            ios_devices = self._get_ios_devices()
            devices.extend(ios_devices)
        except Exception as e:
            print(f"获取iOS设备失败: {e}")
        
        return devices
    
    def _get_android_device_info(self, device_id: str) -> Dict[str, str]:
        """获取Android设备详细信息"""
        try:
            # 获取设备名称
            name_cmd = f"adb -s {device_id} shell getprop ro.product.model"
            name = subprocess.check_output(name_cmd, shell=True, text=True).strip()
            
            # 获取Android版本
            version_cmd = f"adb -s {device_id} shell getprop ro.build.version.release"
            version = subprocess.check_output(version_cmd, shell=True, text=True).strip()
            
            # 获取API级别
            api_cmd = f"adb -s {device_id} shell getprop ro.build.version.sdk"
            api_level = subprocess.check_output(api_cmd, shell=True, text=True).strip()
            
            return {
                "name": name,
                "version": f"Android {version} (API {api_level})",
                "manufacturer": self._get_manufacturer(device_id)
            }
        except Exception:
            return {"name": "Unknown", "version": "Unknown", "manufacturer": "Unknown"}
    
    def _get_manufacturer(self, device_id: str) -> str:
        """获取设备制造商"""
        try:
            cmd = f"adb -s {device_id} shell getprop ro.product.manufacturer"
            return subprocess.check_output(cmd, shell=True, text=True).strip()
        except Exception:
            return "Unknown"
    
    def _get_ios_devices(self) -> List[Dict[str, str]]:
        """获取iOS设备列表"""
        devices = []
        try:
            # 尝试使用tidevice
            result = subprocess.check_output(["tidevice", "list"], text=True)
            lines = result.strip().split('\n')
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        device_id = parts[0]
                        device_name = ' '.join(parts[1:])
                        devices.append({
                            "id": device_id,
                            "platform": "ios",
                            "status": "device",
                            "name": device_name,
                            "version": "iOS",
                            "uri": f"ios:///{device_id}"
                        })
        except (subprocess.CalledProcessError, FileNotFoundError):
            # tidevice未安装或执行失败
            pass
        
        return devices
    
    def save_device_config(self, devices: List[Dict[str, str]]):
        """保存设备配置到文件"""
        self.config_file.parent.mkdir(exist_ok=True)
        
        config = {
            "devices": devices,
            "default_device": devices[0]["id"] if devices else None,
            "updated_at": str(Path(__file__).stat().st_mtime)
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"设备配置已保存到: {self.config_file}")
    
    def load_device_config(self) -> Optional[Dict]:
        """从文件加载设备配置"""
        if not self.config_file.exists():
            return None
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载设备配置失败: {e}")
            return None
    
    def get_device_uri(self, device_id: str = None) -> str:
        """获取设备URI"""
        config = self.load_device_config()
        
        if not config:
            # 如果没有配置文件，自动检测设备
            devices = self.get_available_devices()
            if not devices:
                raise Exception("未找到可用设备")
            return devices[0]["uri"]
        
        # 使用指定设备或默认设备
        target_id = device_id or config.get("default_device")
        
        for device in config.get("devices", []):
            if device["id"] == target_id:
                return device["uri"]
        
        raise Exception(f"未找到设备: {target_id}")
    
    def print_device_list(self):
        """打印设备列表"""
        devices = self.get_available_devices()
        
        if not devices:
            print("❌ 未找到可用设备")
            return
        
        print("📱 可用设备列表:")
        print("-" * 80)
        
        for i, device in enumerate(devices, 1):
            status_icon = "✅" if device["status"] == "device" else "⚠️"
            print(f"{i}. {status_icon} {device['name']}")
            print(f"   ID: {device['id']}")
            print(f"   平台: {device['platform'].upper()}")
            print(f"   版本: {device['version']}")
            print(f"   URI: {device['uri']}")
            print()
    
    def generate_airtest_config(self, device_id: str = None, output_file: str = "airtest_config.py"):
        """生成Airtest配置代码"""
        try:
            uri = self.get_device_uri(device_id)
            
            config_code = f'''#!/usr/bin/env python3
"""Airtest自动生成的设备配置"""

from airtest.core.api import *
from airtest.cli.parser import cli_setup
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

def setup_airtest_device():
    """设置Airtest设备连接"""
    if not cli_setup():
        auto_setup(
            __file__, 
            logdir=True, 
            devices=["{uri}"]
        )
    else:
        auto_setup(__file__)
    
    # 连接设备
    device = connect_device("Android:///")
    
    # 初始化Poco
    poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
    
    return device, poco

if __name__ == "__main__":
    device, poco = setup_airtest_device()
    print(f"设备连接成功: {{device}}")
'''
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(config_code)
            
            print(f"Airtest配置已生成: {output_file}")
            
        except Exception as e:
            print(f"生成配置失败: {e}")


def main():
    """主函数"""
    import sys
    
    manager = DeviceManager()
    
    if len(sys.argv) == 1:
        # 默认显示设备列表
        manager.print_device_list()
        return
    
    command = sys.argv[1]
    
    if command == "list":
        manager.print_device_list()
    
    elif command == "save":
        devices = manager.get_available_devices()
        manager.save_device_config(devices)
        print(f"已保存 {len(devices)} 个设备配置")
    
    elif command == "config":
        device_id = sys.argv[2] if len(sys.argv) > 2 else None
        output_file = sys.argv[3] if len(sys.argv) > 3 else "airtest_config.py"
        manager.generate_airtest_config(device_id, output_file)
    
    elif command == "uri":
        device_id = sys.argv[2] if len(sys.argv) > 2 else None
        try:
            uri = manager.get_device_uri(device_id)
            print(f"设备URI: {uri}")
        except Exception as e:
            print(f"错误: {e}")
    
    else:
        print("使用方法:")
        print("  python device_manager.py list          # 显示设备列表")
        print("  python device_manager.py save          # 保存设备配置")
        print("  python device_manager.py config [id]   # 生成Airtest配置")
        print("  python device_manager.py uri [id]      # 获取设备URI")


if __name__ == "__main__":
    main()