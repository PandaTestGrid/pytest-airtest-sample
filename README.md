# Airtest + Pytest 自动化测试框架

基于Airtest和Pytest的移动应用自动化测试框架，专为容器环境优化，使用JAVACAP+ADBTOUCH配置确保稳定性。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 连接设备

确保Android设备已连接并开启USB调试：

```bash
adb devices
```

### 3. 运行测试

```bash
# 运行所有测试
./test.sh

# 运行特定测试
./test.sh tests/test_official_android_calculator.py -v

# 运行特定测试方法
./test.sh tests/test_official_android_calculator.py::TestOfficialAndroidCalculator::test_app_installation_and_launch -v
```

## 环境变量配置

### 必需配置

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `DEVICE_ID` | 设备序列号 | `62f57575` | `adb devices`获取 |

### 可选配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEVICE_HOST` | ADB服务器地址 | `127.0.0.1` |
| `DEVICE_PORT` | ADB端口 | `5037` |
| `APP_PACKAGE` | 默认应用包名 | `com.google.android.calculator` |
| `TEST_TIMEOUT` | 测试超时时间(秒) | `30.0` |
| `SCREENSHOT_ON_FAILURE` | 失败时截图 | `true` |

### 容器环境变量

框架默认使用容器优化配置，以下变量已预设：

| 变量名 | 值 | 说明 |
|--------|---|------|
| `AIRTEST_CAP_METHOD` | `JAVACAP` | 截图方法 |
| `AIRTEST_TOUCH_METHOD` | `ADBTOUCH` | 触摸方法 |
| `AIRTEST_NO_MINICAP` | `1` | 禁用minicap |
| `AIRTEST_NO_MINITOUCH` | `1` | 禁用minitouch |

## 设备连接配置

框架使用以下设备连接格式（已优化）：

```
Android://127.0.0.1:5037/device_id?cap_method=JAVACAP&touch_method=ADBTOUCH
```

## 项目结构

```
pytest-airtest-sample/
├── config/
│   └── test_config.py          # 测试配置
├── tests/                      # 测试用例
│   ├── test_official_android_calculator.py
│   ├── test_unity_game.py
│   ├── test_official_cocos2dx_blackjack.py
│   └── test_official_airtest_tutorial.py
├── demo_apps/                  # 测试应用和资源
│   ├── com.google.android.calculator.apk
│   ├── poco-demo.apk
│   └── *.png                   # 模板图片
├── utils/                      # 工具类
├── reports/                    # 测试报告
├── conftest.py                 # pytest配置
├── pytest.ini                 # pytest设置
├── requirements.txt            # 依赖包
└── test.sh                     # 测试执行脚本
```

## 测试用例

### 计算器测试
- 应用安装和启动
- 基本计算功能
- UI元素验证
- 复杂计算测试

### Unity游戏测试
- 游戏启动测试
- UI交互测试
- 模板匹配测试

### 其他测试
- Cocos2dx黑杰克游戏
- Airtest官方教程示例

## Docker支持

### 构建镜像

```bash
docker build -t airtest-runner .
```

### 运行容器

```bash
# 使用宿主机网络（推荐）
docker run --rm \
  --network host \
  -e DEVICE_ID=your_device_id \
  -v $(pwd)/reports:/app/reports \
  airtest-runner \
  ./test.sh tests/ -v

# 或使用端口映射
docker run --rm \
  -p 5037:5037 \
  -e DEVICE_ID=your_device_id \
  -e DEVICE_HOST=host.docker.internal \
  -v $(pwd)/reports:/app/reports \
  airtest-runner \
  ./test.sh tests/ -v
```

### Docker Compose

```bash
# 编辑 docker-compose.example.yml 中的设备ID
# 然后运行
docker-compose -f docker-compose.example.yml up
```

## 报告

测试完成后会生成以下报告：

- **HTML报告**: `reports/report.html` - 详细的测试结果和截图
- **JSON报告**: `reports/report.json` - 机器可读的测试数据
- **失败截图**: `reports/screenshots/` - 测试失败时的自动截图

## 常见问题

### 设备连接失败

```bash
# 检查设备连接
adb devices

# 重启ADB服务
adb kill-server
adb start-server

# 检查设备授权
adb shell
```

### 应用安装失败

```bash
# 手动安装APK
adb install demo_apps/com.google.android.calculator.apk

# 检查应用是否已安装
adb shell pm list packages | grep calculator
```

### 容器环境问题

确保容器可以访问宿主机ADB服务：

```bash
# 检查网络连接
docker exec -it container_name ping 127.0.0.1

# 检查ADB连接
docker exec -it container_name adb devices
```

## 开发指南

### 添加新测试

1. 在 `tests/` 目录创建新的测试文件
2. 继承相应的测试基类
3. 使用提供的fixture进行设备和应用设置
4. 编写测试方法，使用 `@pytest.mark.*` 标记

### 自定义配置

修改 `config/test_config.py` 中的配置类来调整框架行为。

### 扩展工具

在 `utils/` 目录添加新的工具类和辅助函数。

## 技术特性

- ✅ **容器优化**: 使用JAVACAP+ADBTOUCH确保容器环境稳定性
- ✅ **零配置**: 开箱即用的设备连接和测试配置
- ✅ **多应用支持**: 支持原生Android、Unity、Cocos2dx应用
- ✅ **丰富报告**: HTML和JSON格式的详细测试报告
- ✅ **失败截图**: 自动捕获测试失败时的屏幕状态
- ✅ **Docker支持**: 完整的容器化部署方案
- ✅ **CI/CD友好**: 适合集成到持续集成流水线

## 许可证

MIT License