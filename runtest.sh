#!/bin/bash

# pytest + airtest 云真机测试运行脚本

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  pytest + airtest 云真机测试框架${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "常用选项:"
    echo "  -h, --help              显示帮助信息"
    echo "  -v                      详细输出"
    echo "  -s                      显示print输出"
    echo "  -k EXPRESSION           运行匹配表达式的测试"
    echo "  -m MARKEXPR             运行指定标记的测试"
    echo "  --clean                 清理之前的测试结果"
    echo "  --config                显示云平台配置"
    echo ""
    echo "测试标记:"
    echo "  -m smoke                冒烟测试"
    echo "  -m regression           回归测试"
    echo "  -m ui                   UI测试"
    echo "  -m cloud                云平台测试"
    echo ""
    echo "云平台环境变量:"
    echo "  CLOUD_PLATFORM         云平台类型 (local/tencent/alibaba/aws)"
    echo "  DEVICE_ID               设备ID"
    echo "  APP_PACKAGE             应用包名"
    echo ""
    echo "示例:"
    echo "  $0                      # 运行所有测试"
    echo "  $0 -m smoke             # 运行冒烟测试"
    echo "  $0 -v                   # 详细输出"
    echo "  $0 tests/test_*.py      # 运行指定文件"
}

# 显示云平台配置
show_config() {
    echo -e "${BLUE}=== 云平台配置 ===${NC}"
    echo "云平台: ${CLOUD_PLATFORM:-local}"
    echo "设备ID: ${DEVICE_ID:-自动检测}"
    echo "应用包名: ${APP_PACKAGE:-com.google.android.calculator}"
    echo "测试超时: ${TEST_TIMEOUT:-30.0}秒"
    echo -e "${BLUE}==================${NC}"
}

# 清理测试结果
clean_results() {
    echo -e "${YELLOW}清理测试结果...${NC}"
    rm -rf reports/*.html reports/*.json reports/screenshots/* logs/* .pytest_cache
    echo -e "${GREEN}清理完成${NC}"
}

# 检查参数
for arg in "$@"; do
    case $arg in
        -h|--help)
            show_help
            exit 0
            ;;
        --config)
            show_config
            exit 0
            ;;
        --clean)
            clean_results
            exit 0
            ;;
    esac
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  pytest + airtest 云真机测试框架${NC}"
echo -e "${GREEN}========================================${NC}"

# 显示云平台配置
if [ "$CLOUD_PLATFORM" != "" ] && [ "$CLOUD_PLATFORM" != "local" ]; then
    echo -e "${BLUE}云平台: $CLOUD_PLATFORM${NC}"
    echo -e "${BLUE}设备ID: ${DEVICE_ID:-自动检测}${NC}"
    echo -e "${BLUE}应用包名: ${APP_PACKAGE:-com.google.android.calculator}${NC}"
    echo ""
fi

# 创建报告目录
mkdir -p reports/screenshots

# 检查设备连接
if [ "$CLOUD_PLATFORM" == "" ] || [ "$CLOUD_PLATFORM" == "local" ]; then
    if command -v adb >/dev/null 2>&1; then
        devices=$(adb devices | grep -v "List of devices" | grep -v "^$" | wc -l)
        if [ $devices -gt 0 ]; then
            echo -e "${GREEN}发现 $devices 个Android设备${NC}"
        else
            echo -e "${YELLOW}未发现Android设备${NC}"
        fi
    fi
fi

# 运行测试
echo -e "${GREEN}开始运行测试...${NC}"
pytest "$@"

# 显示结果
echo -e "${GREEN}测试完成！${NC}"
echo -e "${YELLOW}HTML 报告: reports/report.html${NC}"
echo -e "${YELLOW}JSON 报告: reports/report.json${NC}"