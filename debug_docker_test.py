"""
Docker 容器内 Airtest 设备连接诊断
使用 ADB_SERVER_SOCKET 环境变量连接宿主机 ADB server
"""
import subprocess
import socket
import os
import sys

def run_cmd(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def main():
    adb_socket = os.getenv("ADB_SERVER_SOCKET", "")
    device_id = os.getenv("DEVICE_ID", "62f57575")
    
    print("=" * 60)
    print("Docker 容器内 Airtest 连接诊断")
    print(f"ADB_SERVER_SOCKET={adb_socket}")
    print("=" * 60)
    
    # Step 1: adb devices (直接用，靠 ADB_SERVER_SOCKET)
    print(f"\n[1] adb devices")
    code, out, err = run_cmd(["adb", "devices"])
    print(f"    returncode: {code}")
    print(f"    stdout: {out}")
    if err:
        print(f"    stderr: {err}")
    
    if "device" not in out:
        print(f"    ❌ 没有找到设备")
        return
    else:
        print(f"    ✅ 设备列表获取成功")
    
    # Step 2: adb shell 测试
    print(f"\n[2] adb shell getprop")
    code, out, err = run_cmd(["adb", "-s", device_id, "shell", "getprop", "ro.build.version.sdk"])
    print(f"    SDK version: {out}")
    
    # Step 3: adb forward 测试
    print(f"\n[3] adb forward 端口转发测试")
    test_port = "19876"
    code, out, err = run_cmd([
        "adb", "-s", device_id,
        "forward", "--no-rebind", f"tcp:{test_port}", "localabstract:test_airtest_diag"
    ])
    print(f"    forward 创建: returncode={code}")
    if err:
        print(f"    stderr: {err}")
    
    if code == 0:
        # 测试 forward 端口可达性
        for target in ["host.docker.internal", "127.0.0.1"]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((target, int(test_port)))
                print(f"    ✅ {target}:{test_port} 可连接")
                s.close()
            except Exception as e:
                print(f"    ❌ {target}:{test_port} 不可连接: {e}")
        
        run_cmd(["adb", "-s", device_id, "forward", "--remove", f"tcp:{test_port}"])
    
    # Step 4: Airtest 连接测试
    print(f"\n[4] Airtest connect_device 测试")
    
    # 必须在URI中指定 host.docker.internal，这样 Airtest 的 forward 端口连接才能通
    # ADB_SERVER_SOCKET 让 adb 命令知道 server 在哪
    # URI 中的 host 让 Airtest 知道 forward 端口在哪
    uris = [
        f"Android://host.docker.internal:5037/{device_id}?cap_method=JAVACAP&touch_method=ADBTOUCH&ori_method=ADBORI",
        f"Android://host.docker.internal:5037/{device_id}",
    ]
    
    from airtest.core.api import connect_device, device as get_device
    from airtest.core.helper import G
    
    for uri in uris:
        print(f"\n    URI: {uri}")
        try:
            G.DEVICE_LIST = []
            G.DEVICE = None
            
            dev = connect_device(uri)
            if dev:
                info = dev.get_display_info()
                print(f"    ✅ 连接成功! 屏幕: {info.get('width')}x{info.get('height')}")
                
                try:
                    screen = dev.snapshot()
                    if screen is not None:
                        print(f"    ✅ 截图成功! shape={screen.shape}")
                    else:
                        print(f"    ❌ 截图返回 None")
                except Exception as e:
                    print(f"    ❌ 截图失败: {type(e).__name__}: {e}")
                
                try:
                    dev.disconnect()
                except:
                    pass
                break  # 成功就不再试其他URI
            else:
                print(f"    ❌ connect_device 返回 None")
        except Exception as e:
            print(f"    ❌ 连接失败: {type(e).__name__}: {e}")
    
    print(f"\n{'=' * 60}")
    print("诊断完成")

if __name__ == "__main__":
    main()
