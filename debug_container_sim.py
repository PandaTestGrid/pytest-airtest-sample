"""
模拟容器环境下 Airtest 连接设备的完整流程
重点测试: ADB server 地址解析 + adb forward 端口转发问题
"""
import subprocess
import os

def test_adb_forward_issue():
    """
    核心问题诊断：
    Airtest 使用 minicap/javacap 截图时需要 adb forward 端口转发。
    在容器中，adb forward 创建的是容器本地端口到设备的映射。
    但如果 ADB server 在宿主机上，forward 的端口也在宿主机上，
    容器内无法直接访问这些 forward 的端口。
    """
    print("=" * 60)
    print("容器环境 Airtest 连接问题诊断")
    print("=" * 60)
    
    host = "host.docker.internal"
    port = "5037"
    device_id = "62f57575"
    
    # 1. 测试 adb -H host.docker.internal 是否能工作
    print(f"\n[1] 测试 adb -H {host} -P {port} devices")
    try:
        result = subprocess.run(
            ["adb", "-H", host, "-P", port, "devices"],
            capture_output=True, text=True, timeout=10
        )
        print(f"    stdout: {result.stdout.strip()}")
        if result.stderr:
            print(f"    stderr: {result.stderr.strip()}")
        if result.returncode != 0:
            print(f"    ❌ 返回码: {result.returncode}")
        else:
            print(f"    ✅ ADB 命令成功")
    except Exception as e:
        print(f"    ❌ 失败: {e}")
    
    # 2. 测试 adb forward（这是关键！）
    print(f"\n[2] 测试 adb -H {host} forward 端口转发")
    try:
        # 创建一个 forward
        result = subprocess.run(
            ["adb", "-H", host, "-P", port, "-s", device_id, 
             "forward", "--no-rebind", "tcp:19876", "localabstract:test_forward"],
            capture_output=True, text=True, timeout=10
        )
        print(f"    forward 创建: returncode={result.returncode}")
        if result.stderr:
            print(f"    stderr: {result.stderr.strip()}")
        
        if result.returncode == 0:
            # 检查 forward 列表
            result2 = subprocess.run(
                ["adb", "-H", host, "-P", port, "-s", device_id, "forward", "--list"],
                capture_output=True, text=True, timeout=10
            )
            print(f"    forward 列表: {result2.stdout.strip()}")
            
            # 关键问题：forward 的端口 19876 在哪里监听？
            # 如果 ADB server 在宿主机，端口 19876 监听在宿主机上
            # 容器内连 localhost:19876 是连不到的！
            import socket
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                # 尝试连接本地 forward 端口
                sock.connect(("127.0.0.1", 19876))
                print(f"    ✅ 本地 127.0.0.1:19876 可连接")
                sock.close()
            except Exception as e:
                print(f"    ⚠️ 本地 127.0.0.1:19876 不可连接: {e}")
                print(f"    这在容器中意味着: forward 端口在宿主机上，容器内无法访问!")
            
            # 尝试连接 host.docker.internal:19876
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((host, 19876))
                print(f"    ✅ {host}:19876 可连接")
                sock.close()
            except Exception as e:
                print(f"    ⚠️ {host}:19876 不可连接: {e}")
            
            # 清理 forward
            subprocess.run(
                ["adb", "-H", host, "-P", port, "-s", device_id, 
                 "forward", "--remove", "tcp:19876"],
                capture_output=True, text=True, timeout=10
            )
    except Exception as e:
        print(f"    ❌ 失败: {e}")
    
    # 3. 分析 Airtest 的 ADB 类行为
    print(f"\n[3] Airtest ADB 类行为分析")
    from airtest.core.android.adb import ADB
    
    # 模拟容器环境: host=host.docker.internal
    print(f"    当 host={host} 时:")
    print(f"    ADB 命令前缀: adb -H {host} -P {port}")
    print(f"    adb forward 创建的端口监听在: 宿主机 (ADB server 所在机器)")
    print(f"    Airtest 连接 forward 端口时连的是: 127.0.0.1 (容器本地)")
    print(f"    ❌ 这就是问题所在！forward 端口在宿主机，但 Airtest 连的是容器本地")
    
    # 4. 看看 Airtest 怎么连接 forward 端口的
    print(f"\n[4] Airtest forward 端口连接方式")
    import inspect
    
    # 查看 javacap 的连接方式
    try:
        from airtest.core.android.cap_methods.javacap import Javacap
        src = inspect.getsource(Javacap.get_stream)
        # 找到 socket 连接的部分
        for line in src.split('\n'):
            if 'connect' in line.lower() or 'socket' in line.lower() or 'localhost' in line.lower() or '127.0.0.1' in line.lower():
                print(f"    {line.strip()}")
    except Exception as e:
        print(f"    查看 Javacap 源码失败: {e}")
    
    # 查看 minicap 的连接方式
    try:
        from airtest.core.android.cap_methods.minicap import Minicap
        src = inspect.getsource(Minicap)
        for line in src.split('\n'):
            if 'connect' in line.lower() and ('socket' in line.lower() or 'localhost' in line.lower() or '127.0.0.1' in line.lower()):
                print(f"    {line.strip()}")
    except Exception as e:
        print(f"    查看 Minicap 源码失败: {e}")
    
    # 5. 结论
    print(f"\n{'=' * 60}")
    print("诊断结论:")
    print("=" * 60)
    print("""
Airtest 在容器中找不到设备的根本原因:

1. Airtest 通过 URI 解析出 host=host.docker.internal, port=5037
2. ADB 命令使用 -H host.docker.internal -P 5037，可以正常执行 adb shell 等命令
3. 但 Airtest 的 minicap/javacap/maxtouch 等组件需要 adb forward 端口转发
4. adb forward 创建的端口监听在 ADB server 所在的机器（宿主机）
5. Airtest 内部连接 forward 端口时，连的是 localhost/127.0.0.1
6. 在容器中，localhost 是容器自己，不是宿主机
7. 所以 Airtest 无法连接到 forward 的端口，导致截图/触控失败

这就是为什么 uiautomator2 可以工作但 Airtest 不行:
- uiautomator2 通过 HTTP 协议直接与设备上的 atx-agent 通信
- Airtest 依赖 adb forward 端口转发 + 本地 socket 连接
""")

if __name__ == "__main__":
    test_adb_forward_issue()
