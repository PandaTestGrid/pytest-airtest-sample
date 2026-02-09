"""
云真机测试平台配置文件
支持通过环境变量动态配置设备和测试参数
"""

import os
from typing import Dict, Any, Optional


class Config:
    """云真机测试平台配置类"""
    
    # 设备配置
    DEVICE_ID = os.getenv("DEVICE_ID", "62f57575")  # 设备序列号，默认使用本地设备ID
    DEVICE_PLATFORM = os.getenv("DEVICE_PLATFORM", "Android")  # 设备平台: Android/iOS
    DEVICE_TIMEOUT = float(os.getenv("DEVICE_TIMEOUT", "10.0"))  # 设备操作超时时间
    DEVICE_HOST = os.getenv("DEVICE_HOST", "127.0.0.1")  # 设备连接主机
    DEVICE_PORT = int(os.getenv("DEVICE_PORT", "5037"))  # 设备连接端口
    
    # 容器环境配置（默认启用）
    CONTAINER_MODE = os.getenv("CONTAINER_MODE", "true").lower() == "true"  # 默认容器模式
    DISPLAY = os.getenv("DISPLAY", None)  # X11显示配置
    
    # 云平台配置
    CLOUD_PLATFORM = os.getenv("CLOUD_PLATFORM", "local")  # 云平台类型: local/aws/tencent/alibaba/container
    CLOUD_TOKEN = os.getenv("CLOUD_TOKEN", None)  # 云平台访问令牌
    CLOUD_PROJECT_ID = os.getenv("CLOUD_PROJECT_ID", None)  # 云平台项目ID
    
    # 应用配置
    APP_PACKAGE = os.getenv("APP_PACKAGE", "com.google.android.calculator")  # 应用包名
    APP_ACTIVITY = os.getenv("APP_ACTIVITY", ".Calculator")  # 应用主 Activity
    APP_PATH = os.getenv("APP_PATH", None)  # 应用安装包路径
    
    # 测试配置
    TEST_TIMEOUT = float(os.getenv("TEST_TIMEOUT", "30.0"))  # 测试超时时间
    TEST_RETRY_COUNT = int(os.getenv("TEST_RETRY_COUNT", "3"))  # 测试重试次数
    SCREENSHOT_ON_FAILURE = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
    
    # 报告配置
    REPORT_DIR = os.getenv("REPORT_DIR", "reports")
    SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    
    # 等待配置
    IMPLICIT_WAIT = float(os.getenv("IMPLICIT_WAIT", "10.0"))  # 隐式等待时间
    EXPLICIT_WAIT = float(os.getenv("EXPLICIT_WAIT", "10.0"))  # 显式等待时间
    
    # 网络配置
    NETWORK_TIMEOUT = float(os.getenv("NETWORK_TIMEOUT", "30.0"))  # 网络超时时间
    MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))  # 最大重试次数
    
    @classmethod
    def get_device_config(cls) -> Dict[str, Any]:
        """获取设备配置
        
        Returns:
            设备配置字典
        """
        config = {
            "platform": cls.DEVICE_PLATFORM,
            "timeout": cls.DEVICE_TIMEOUT,
            "host": cls.DEVICE_HOST,
            "port": cls.DEVICE_PORT,
        }
        
        if cls.DEVICE_ID:
            config["serial"] = cls.DEVICE_ID
            
        return config
    
    @classmethod
    def get_app_config(cls) -> Dict[str, Any]:
        """获取应用配置
        
        Returns:
            应用配置字典
        """
        config = {
            "package": cls.APP_PACKAGE,
            "activity": cls.APP_ACTIVITY,
        }
        
        if cls.APP_PATH:
            config["path"] = cls.APP_PATH
            
        return config
    
    @classmethod
    def get_cloud_config(cls) -> Dict[str, Any]:
        """获取云平台配置
        
        Returns:
            云平台配置字典
        """
        return {
            "platform": cls.CLOUD_PLATFORM,
            "token": cls.CLOUD_TOKEN,
            "project_id": cls.CLOUD_PROJECT_ID,
        }
    
    @classmethod
    def get_device_uri(cls) -> str:
        """获取设备连接URI
        
        容器环境中 DEVICE_HOST 必须指向宿主机地址:
        - macOS Docker Desktop: host.docker.internal
        - Linux Docker (host网络): 127.0.0.1
        - Linux Docker (bridge网络): 172.17.0.1 或宿主机IP
        
        URI 中的 host 不仅用于 adb 命令的 -H 参数，
        还用于 Airtest 连接 forward 端口 (javacap/minicap 等)。
        容器内 forward 端口在宿主机上，所以 host 必须指向宿主机。
        
        Returns:
            设备连接字符串
        """
        host = cls.DEVICE_HOST
        port = cls.DEVICE_PORT
        
        if cls.DEVICE_ID:
            return f"Android://{host}:{port}/{cls.DEVICE_ID}"
        else:
            return f"Android://{host}:{port}"
    
    @classmethod
    def get_safe_device_uri(cls) -> str:
        """获取安全的设备连接URI - 用于容器环境兼容
        
        Returns:
            简化的设备连接字符串
        """
        # 容器环境使用更简单的连接方式
        if cls.DEVICE_ID:
            return f"Android:///{cls.DEVICE_ID}"
        else:
            return "Android:///"
    
    @classmethod
    def is_cloud_platform(cls) -> bool:
        """判断是否为云平台环境
        
        Returns:
            是否为云平台
        """
        return cls.CLOUD_PLATFORM != "local"
    
    @classmethod
    def is_container_mode(cls) -> bool:
        """判断是否为容器环境
        
        Returns:
            是否为容器环境
        """
        return cls.CONTAINER_MODE
    
    @classmethod
    def print_config(cls) -> None:
        """打印当前配置信息"""
        print("=== Airtest 测试框架配置 ===")
        print(f"设备ID: {cls.DEVICE_ID or '自动检测'}")
        print(f"应用包名: {cls.APP_PACKAGE}")
        print(f"设备URI: {cls.get_device_uri()}")
        print(f"测试超时: {cls.TEST_TIMEOUT}秒")
        print("=" * 30)


# 元素选择器配置（保持向后兼容）
class ElementSelectors:
    """元素选择器配置类"""
    
    # 计算器应用元素
    CALCULATOR_DIGIT_0 = "com.google.android.calculator:id/digit_0"
    CALCULATOR_DIGIT_1 = "com.google.android.calculator:id/digit_1"
    CALCULATOR_DIGIT_2 = "com.google.android.calculator:id/digit_2"
    CALCULATOR_DIGIT_3 = "com.google.android.calculator:id/digit_3"
    CALCULATOR_DIGIT_4 = "com.google.android.calculator:id/digit_4"
    CALCULATOR_DIGIT_5 = "com.google.android.calculator:id/digit_5"
    CALCULATOR_DIGIT_6 = "com.google.android.calculator:id/digit_6"
    CALCULATOR_DIGIT_7 = "com.google.android.calculator:id/digit_7"
    CALCULATOR_DIGIT_8 = "com.google.android.calculator:id/digit_8"
    CALCULATOR_DIGIT_9 = "com.google.android.calculator:id/digit_9"
    
    CALCULATOR_OP_ADD = "com.google.android.calculator:id/op_add"
    CALCULATOR_OP_SUB = "com.google.android.calculator:id/op_sub"
    CALCULATOR_OP_MUL = "com.google.android.calculator:id/op_mul"
    CALCULATOR_OP_DIV = "com.google.android.calculator:id/op_div"
    CALCULATOR_EQ = "com.google.android.calculator:id/eq"
    CALCULATOR_CLR = "com.google.android.calculator:id/clr"
    CALCULATOR_RESULT = "com.google.android.calculator:id/result"
    CALCULATOR_FORMULA = "com.google.android.calculator:id/formula"
    
    # Unity 游戏元素
    UNITY_START_BUTTON = "text=Start"
    UNITY_BASIC_BUTTON = "text=basic"
    UNITY_BACK_BUTTON = "text=Back"
    UNITY_INPUT_FIELD = "type=InputField"
    UNITY_TEXT_ELEMENT = "type=Text"
    
    # 通用元素
    LOADING_INDICATOR = "loading"
    BACK_BUTTON = "back"
    MENU_BUTTON = "menu"


# 向后兼容的配置变量
APP_PACKAGE = Config.APP_PACKAGE
APP_ACTIVITY = Config.APP_ACTIVITY
DEVICE_SERIAL = Config.DEVICE_ID
DEVICE_TIMEOUT = Config.DEVICE_TIMEOUT
TEST_TIMEOUT = Config.TEST_TIMEOUT
SCREENSHOT_ON_FAILURE = Config.SCREENSHOT_ON_FAILURE
REPORT_DIR = Config.REPORT_DIR
SCREENSHOT_DIR = Config.SCREENSHOT_DIR
LOG_DIR = Config.LOG_DIR
IMPLICIT_WAIT = Config.IMPLICIT_WAIT
EXPLICIT_WAIT = Config.EXPLICIT_WAIT


# 保持向后兼容的 TestConfig 类
class TestConfig:
    """测试配置类（向后兼容）"""
    
    # 设备配置
    DEVICE_PLATFORM = Config.DEVICE_PLATFORM
    DEVICE_URI = Config.get_device_uri()
    
    # 应用配置
    APP_PACKAGE = Config.APP_PACKAGE
    APP_ACTIVITY = Config.APP_ACTIVITY
    
    # 超时配置
    DEFAULT_TIMEOUT = int(Config.DEVICE_TIMEOUT)
    LONG_TIMEOUT = int(Config.TEST_TIMEOUT)
    SHORT_TIMEOUT = 5
    
    # 截图配置
    SCREENSHOT_DIR = Config.SCREENSHOT_DIR
    SCREENSHOT_ON_FAILURE = Config.SCREENSHOT_ON_FAILURE
    
    # 报告配置
    REPORT_DIR = Config.REPORT_DIR
    HTML_REPORT = True
    
    # 重试配置
    MAX_RETRY_COUNT = Config.TEST_RETRY_COUNT
    RETRY_DELAY = 2
    
    # 环境配置
    TEST_ENV = os.getenv("TEST_ENV", "dev")
    
    @classmethod
    def get_test_user(cls, user_type="valid_user"):
        """获取测试用户信息（向后兼容）"""
        return {"username": "test", "password": "test"}