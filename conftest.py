"""
pytest配置文件和全局fixture - 支持云真机测试平台
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
    
    print("✅ 测试环境设置完成")
    yield
    print("✅ 测试环境清理完成")


@pytest.fixture(scope="session")
def global_device_setup():
    """全局设备连接设置 - 整个测试会话只连接一次"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # 获取设备连接URI
            device_uri = Config.get_device_uri()
            print(f"🔗 全局设备连接 (尝试 {attempt + 1}/{max_retries}): {device_uri}")
            
            # 使用auto_setup进行全局设备连接
            auto_setup(__file__, logdir=True, devices=[device_uri])
            device_obj = device()
            
            if device_obj:
                print(f"✅ 全局设备连接成功")
                # 验证设备是否可用
                try:
                    # 简单的设备验证
                    device_obj.get_display_info()
                    print(f"✅ 设备验证通过")
                    yield device_obj
                    return
                except Exception as e:
                    print(f"⚠️ 设备验证失败: {e}")
                    if attempt < max_retries - 1:
                        print(f"🔄 {retry_delay}秒后重试...")
                        sleep(retry_delay)
                        continue
                    else:
                        raise
            else:
                raise Exception("设备对象为空")
                
        except Exception as e:
            print(f"❌ 设备连接失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"🔄 {retry_delay}秒后重试...")
                sleep(retry_delay)
            else:
                # 最后一次尝试失败，提供更详细的错误信息
                if Config.is_cloud_platform():
                    print("☁️ 云平台连接失败，请检查:")
                    print("  1. DEVICE_ID 是否正确")
                    print("  2. CLOUD_TOKEN 是否有效")
                    print("  3. 云平台设备是否在线")
                else:
                    print("🏠 本地设备连接失败，请检查:")
                    print("  1. 设备是否连接并开启USB调试")
                    print("  2. ADB是否正常工作")
                    print("  3. 运行 'adb devices' 检查设备列表")
                raise
    
    print("🔌 全局设备连接清理完成")


@pytest.fixture(scope="class")
def calculator_setup(global_device_setup):
    """计算器应用设置fixture"""
    device_obj = global_device_setup
    
    # 计算器应用配置
    calculator_pkg = "com.google.android.calculator"
    calculator_apk = "demo_apps/com.google.android.calculator.apk"
    
    try:
        # 检查应用是否已安装
        if calculator_pkg not in device_obj.list_app():
            apk_path = Path(calculator_apk)
            if apk_path.exists():
                print(f"📱 安装计算器APK: {apk_path}")
                device_obj.install_app(str(apk_path))
            else:
                print(f"⚠️ APK文件不存在: {apk_path}")
        
        # 启动计算器应用
        stop_app(calculator_pkg)
        print(f"🧮 启动计算器应用: {calculator_pkg}")
        start_app(calculator_pkg)
        sleep(2)
        
        # 初始化AndroidUiautomationPoco
        poco = AndroidUiautomationPoco()
        
        yield device_obj, poco
        
    except Exception as e:
        print(f"❌ 计算器应用设置失败: {e}")
        raise
    finally:
        # 清理
        try:
            stop_app(calculator_pkg)
            print("🛑 计算器应用已停止")
        except:
            pass


@pytest.fixture(scope="class")
def unity_setup(global_device_setup):
    """Unity应用设置fixture"""
    device_obj = global_device_setup
    
    # Unity应用包名
    unity_pkg = "com.NetEase.PocoDemo"
    
    try:
        # 启动Unity应用
        print(f"🎮 启动Unity应用: {unity_pkg}")
        stop_app(unity_pkg)
        start_app(unity_pkg)
        sleep(5)  # Unity应用需要更长的启动时间
        
        # 初始化Unity Poco
        poco = UnityPoco()
        
        yield device_obj, poco
        
    except Exception as e:
        print(f"❌ Unity应用设置失败: {e}")
        raise
    finally:
        # 清理Unity应用
        try:
            stop_app(unity_pkg)
            print("🛑 Unity应用已停止")
        except:
            pass


@pytest.fixture(autouse=True)
def screenshot_on_failure(request):
    """测试失败时自动截图"""
    yield
    
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        if Config.SCREENSHOT_ON_FAILURE:
            # 生成截图文件名
            test_name = request.node.name.replace("::", "_").replace("[", "_").replace("]", "_")
            timestamp = int(time.time())
            screenshot_name = f"failure_{test_name}_{timestamp}.png"
            screenshot_path = os.path.join("reports/screenshots", screenshot_name)
            
            try:
                # 确保设备连接存在
                device_obj = device()
                if device_obj:
                    # 截图
                    snapshot(screenshot_path)
                    print(f"📸 失败截图已保存: {screenshot_path}")
                else:
                    print("⚠️ 设备未连接，无法截图")
            except Exception as e:
                print(f"❌ 截图失败: {e}")


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