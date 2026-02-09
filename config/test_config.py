"""测试配置 - 通过环境变量动态配置"""

import os


class Config:
    # 设备连接
    DEVICE_ID = os.getenv("DEVICE_ID", "62f57575")
    DEVICE_HOST = os.getenv("DEVICE_HOST", "127.0.0.1")
    DEVICE_PORT = int(os.getenv("DEVICE_PORT", "5037"))

    # 运行环境
    CONTAINER_MODE = os.getenv("CONTAINER_MODE", "false").lower() == "true"
    CLOUD_PLATFORM = os.getenv("CLOUD_PLATFORM", "local")

    # 应用
    APP_PACKAGE = os.getenv("APP_PACKAGE", "com.google.android.calculator")

    # 测试行为
    SCREENSHOT_ON_FAILURE = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"

    @classmethod
    def get_device_uri(cls) -> str:
        """构建 Airtest 设备 URI

        容器环境中 DEVICE_HOST 须指向宿主机:
          macOS Docker Desktop → host.docker.internal
          Linux bridge         → 172.17.0.1 或宿主机 IP
          Linux host network   → 127.0.0.1
        """
        h, p = cls.DEVICE_HOST, cls.DEVICE_PORT
        if cls.DEVICE_ID:
            return f"Android://{h}:{p}/{cls.DEVICE_ID}"
        return f"Android://{h}:{p}"

    @classmethod
    def is_cloud_platform(cls) -> bool:
        return cls.CLOUD_PLATFORM != "local"
