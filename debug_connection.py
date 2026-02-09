"""
诊断脚本：模拟容器环境下 Airtest 连接设备的过程
"""
import subprocess
import sys
import os

def diagnose():
    print("=" * 50)
    print("Airtest 设备连接诊断")
    print("=" * 50)
    
    # 1. 检查环境变量
    host = os.getenv("DEVICE_HOST", "127.0.0.1")
    port = os.getenv("DEVICE_PORT", "5037")
    device_id = os.getenv("DEVICE_ID", "62f57575")
    container_mode = os.getenv("CONTAINER_MODE", "false")
    
    print(f"\n[环境变量]")
    print(f"  DEVICE_HOST: {host}")
    print(f"  DEVICE_PORT: {port}")
    print(f"  DEVICE_ID: {device_id}")
    print(f"  CONTAINER_MODE: {container_mode}")
    print(f"  AIRTEST_CAP_METHOD: {os.getenv('AIRTEST_CAP_METHOD', '未设置')}")
    print(f"  AIRTEST_TOUCH_METHOD: {os.getenv('AIRTEST_TOUCH_METHOD', '未设置')}")
    print(f"  AIRTEST_NO_MINICAP: {os.getenv('AIRTEST_NO_MINICAP', '未设置')}")
    print(f"  AIRTEST_NO_MINITOUCH: {os.getenv('AIRTEST_NO_MINITOUCH', '未设置')}")
    
    # 2. 检查 adb 连接
    print(f"\n[ADB 连接测试]")
    try:
        result = subprocess.run(
            ["adb", "-H", host, "-P", port, "devices"],
            capture_output=True, text=True, timeout=10
        )
        print(f"  adb -H {host} -P {port} devices:")
        print(f"  {result.stdout.strip()}")
        if result.stderr:
            print(f"  stderr: {result.stderr.strip()}")
    except Exception as e:
        print(f"  ADB命令失败: {e}")
    
    # 3. 测试 Airtest 连接
    print(f"\n[Airtest 连接测试]")
    
    # 测试不同的 URI 格式
    uris_to_test = [
        f"Android://{host}:{port}/{device_id}?cap_method=JAVACAP&touch_method=ADBTOUCH&ori_method=ADBORI",
        f"Android://{host}:{port}/{device_id}",
        f"Android:///{device_id}",
    ]
    
    from airtest.core.api import connect_device, device as get_device
    from airtest.core.helper import G
    
    for uri in uris_to_test:
        print(f"\n  尝试URI: {uri}")
        try:
            # 清除之前的设备连接
            G.DEVICE_LIST = []
            G.DEVICE = None
            
            dev = connect_device(uri)
            if dev:
                info = dev.get_display_info()
                print(f"  ✅ 连接成功! 屏幕信息: {info}")
                
                # 测试截图能力
                try:
                    screen = dev.snapshot()
                    if screen is not None:
                        print(f"  ✅ 截图成功! 尺寸: {screen.shape if hasattr(screen, 'shape') else '未知'}")
                    else:
                        print(f"  ❌ 截图返回None")
                except Exception as e:
                    print(f"  ❌ 截图失败: {type(e).__name__}: {e}")
                
                # 断开连接
                try:
                    dev.disconnect()
                except:
                    pass
            else:
                print(f"  ❌ connect_device 返回 None")
        except Exception as e:
            print(f"  ❌ 连接失败: {type(e).__name__}: {e}")
    
    print(f"\n{'=' * 50}")
    print("诊断完成")

if __name__ == "__main__":
    diagnose()
