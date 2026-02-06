"""
pytest配置文件和全局fixture
"""

import pytest
import os
import time
from pathlib import Path
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from poco.drivers.unity3d import UnityPoco
from config.test_config import Config


@pytest.fixture(scope="session")
def setup_test_environment():
    """设置测试环境"""
    # 创建必要的目录
    os.makedirs("reports", exist_ok=True)
    os.makedirs("reports/screenshots", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # 设置容器环境优化
    os.environ.setdefault('AIRTEST_CAP_METHOD', 'JAVACAP')
    os.environ.setdefault('AIRTEST_TOUCH_METHOD', 'ADBTOUCH')
    os.environ.setdefault('AIRTEST_NO_MINICAP', '1')
    os.environ.setdefault('AIRTEST_NO_MINITOUCH', '1')
    
    yield


@pytest.fixture(scope="session")
def global_device_setup(setup_test_environment):
    """全局设备连接设置"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            device_uri = Config.get_device_uri()
            auto_setup(__file__, logdir=True, devices=[device_uri])
            device_obj = device()
            
            if device_obj:
                # 验证设备可用性
                device_obj.get_display_info()
                yield device_obj
                return
            else:
                raise Exception("设备对象为空")
                
        except Exception as e:
            if attempt < max_retries - 1:
                sleep(retry_delay)
            else:
                print(f"❌ 设备连接失败: {e}")
                print("请检查:")
                print("  1. 设备是否连接并开启USB调试")
                print("  2. ADB是否正常工作")
                print("  3. 运行 'adb devices' 检查设备列表")
                raise


@pytest.fixture(scope="class")
def calculator_setup(global_device_setup):
    """计算器应用设置"""
    device_obj = global_device_setup
    
    calculator_pkg = "com.google.android.calculator"
    calculator_apk = "demo_apps/com.google.android.calculator.apk"
    
    try:
        # 检查并安装应用
        if calculator_pkg not in device_obj.list_app():
            apk_path = Path(calculator_apk)
            if apk_path.exists():
                device_obj.install_app(str(apk_path))
        
        # 启动应用
        stop_app(calculator_pkg)
        start_app(calculator_pkg)
        sleep(2)
        
        # 初始化Poco
        poco = AndroidUiautomationPoco()
        
        yield device_obj, poco
        
    except Exception as e:
        print(f"❌ 计算器应用设置失败: {e}")
        raise
    finally:
        try:
            stop_app(calculator_pkg)
        except:
            pass


@pytest.fixture(scope="class")
def unity_setup(global_device_setup):
    """Unity应用设置"""
    device_obj = global_device_setup
    
    unity_pkg = "com.NetEase.PocoDemo"
    
    try:
        # 启动Unity应用
        stop_app(unity_pkg)
        start_app(unity_pkg)
        sleep(5)
        
        # 初始化Unity Poco
        poco = UnityPoco()
        
        yield device_obj, poco
        
    except Exception as e:
        print(f"❌ Unity应用设置失败: {e}")
        raise
    finally:
        try:
            stop_app(unity_pkg)
        except:
            pass


@pytest.fixture(autouse=True)
def screenshot_on_failure(request):
    """测试失败时自动截图"""
    yield
    
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        if Config.SCREENSHOT_ON_FAILURE:
            test_name = request.node.name.replace("::", "_").replace("[", "_").replace("]", "_")
            timestamp = int(time.time())
            screenshot_name = f"failure_{test_name}_{timestamp}.png"
            screenshot_path = os.path.join("reports/screenshots", screenshot_name)
            
            try:
                device_obj = device()
                if device_obj:
                    snapshot(screenshot_path)
            except Exception:
                pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """生成测试报告钩子"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


def pytest_configure(config):
    """pytest配置钩子"""
    # 添加自定义标记
    config.addinivalue_line("markers", "cloud: 云平台专用测试")
    config.addinivalue_line("markers", "local: 本地设备专用测试")
    config.addinivalue_line("markers", "retry: 支持重试的测试")
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "regression: 回归测试")
    config.addinivalue_line("markers", "ui: UI测试")
    config.addinivalue_line("markers", "stress: 压力测试")
    config.addinivalue_line("markers", "performance: 性能测试")


def pytest_collection_modifyitems(config, items):
    """修改测试收集 - 根据环境跳过不适用的测试"""
    if Config.is_cloud_platform():
        # 云平台环境，跳过本地专用测试
        skip_local = pytest.mark.skip(reason="云平台环境跳过本地专用测试")
        for item in items:
            if "local" in item.keywords:
                item.add_marker(skip_local)
    else:
        # 本地环境，跳过云平台专用测试
        skip_cloud = pytest.mark.skip(reason="本地环境跳过云平台专用测试")
        for item in items:
            if "cloud" in item.keywords:
                item.add_marker(skip_cloud)