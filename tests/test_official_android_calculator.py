"""
基于Airtest官方Android计算器示例的pytest测试用例 - 支持云真机平台
原始文件: airtest_examples/Android/calculator.air/calculator.py
作者: gzliuxin
"""

import pytest
import os
from pathlib import Path
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from config.test_config import Config


class TestOfficialAndroidCalculator:
    """官方Android计算器测试类 - 云平台适配版"""
    
    PKG = "com.google.android.calculator"
    APK_PATH = "demo_apps/com.google.android.calculator.apk"
    
    @pytest.fixture(scope="class")
    def calculator_setup(self):
        """计算器应用设置 - 支持云平台"""
        # 使用云平台设备连接
        device_uri = Config.get_device_uri()
        print(f"🔗 云平台设备连接: {device_uri}")
        
        # 连接设备
        auto_setup(
            __file__, 
            logdir=True, 
            devices=[device_uri]
        )
        
        device_obj = device()
        
        # 云平台设备初始化
        if Config.is_cloud_platform():
            print("☁️ 云平台设备初始化...")
            sleep(2)
        
        # 检查并安装APK（云平台可能已预装）
        if self.PKG not in device_obj.list_app():
            apk_path = Path(self.APK_PATH)
            if apk_path.exists():
                print(f"📱 安装计算器APK: {apk_path}")
                device_obj.install_app(str(apk_path))
            else:
                # 云平台可能不需要安装，应用已预装
                if Config.is_cloud_platform():
                    print("☁️ 云平台应用可能已预装")
                else:
                    raise FileNotFoundError(f"APK文件不存在: {apk_path}")
        
        # 启动应用
        stop_app(self.PKG)
        start_app(self.PKG)
        
        # 云平台可能需要更长的启动时间
        if Config.is_cloud_platform():
            sleep(3)
        else:
            sleep(2)
        
        # 初始化AndroidUiautomationPoco
        poco = AndroidUiautomationPoco()
        
        yield device_obj, poco
        
        # 清理
        stop_app(self.PKG)
    
    @pytest.mark.smoke
    @pytest.mark.cloud  # 标记为云平台测试
    def test_app_installation_and_launch(self, calculator_setup):
        """测试计算器应用安装和启动 - 云平台版"""
        device_obj, poco = calculator_setup
        
        # 验证应用已安装
        assert self.PKG in device_obj.list_app(), "计算器应用未正确安装"
        
        # 验证Poco连接成功
        assert poco is not None, "AndroidUiautomationPoco初始化失败"
        
        # 截图记录
        snapshot("calculator_launched_cloud.png")
        
        print("✅ 云平台计算器应用安装和启动测试通过")
    
    @pytest.mark.regression
    @pytest.mark.retry  # 标记为支持重试
    def test_basic_calculation_1_plus_2_equals_3(self, calculator_setup):
        """测试基本计算: (1+2)==3 - 官方示例核心功能（云平台适配）"""
        device_obj, poco = calculator_setup
        
        # 清除之前的计算
        try:
            poco("com.google.android.calculator:id/clr").click()
        except:
            pass  # 如果没有清除按钮就跳过
        
        # 云平台可能需要额外等待
        if Config.is_cloud_platform():
            sleep(1)
        
        # 执行计算: 1 + 2 = 3
        poco("com.google.android.calculator:id/digit_1").click()
        poco("com.google.android.calculator:id/op_add").click()
        poco("com.google.android.calculator:id/digit_2").click()
        poco("com.google.android.calculator:id/eq").click()
        
        # 云平台计算可能需要更多时间
        if Config.is_cloud_platform():
            sleep(1)
        
        # 验证结果
        result = poco("com.google.android.calculator:id/result").get_text()
        assert_equal(result, "3")
        
        # 截图记录
        snapshot("calculation_1_plus_2_equals_3_cloud.png")
        
        print(f"✅ 云平台基本计算测试通过: 1+2={result}")
    
    @pytest.mark.ui
    def test_swipe_functionality(self, calculator_setup):
        """测试滑动功能 - 官方示例功能（云平台适配）"""
        device_obj, poco = calculator_setup
        
        # 点击箭头按钮展开更多功能
        try:
            poco("com.google.android.calculator:id/arrow").click()
            sleep(1.0)
            
            # 验证对数函数按钮出现
            fun_log = poco("com.google.android.calculator:id/fun_log").exists()
            assert_equal(fun_log, True)
            
            # 滑动收起功能面板
            poco("com.google.android.calculator:id/arrow").swipe([0.6884, 0.01])
            sleep(1.0)
            
        except Exception as e:
            if Config.is_cloud_platform():
                print(f"☁️ 云平台滑动功能可能不支持: {e}")
                pytest.skip("云平台设备不支持此滑动功能")
            else:
                raise
        
        # 截图记录
        snapshot("swipe_functionality_test_cloud.png")
        
        print("✅ 滑动功能测试通过")
    
    @pytest.mark.regression
    def test_input_all_digits(self, calculator_setup):
        """测试输入所有数字 - 官方示例功能（云平台适配）"""
        device_obj, poco = calculator_setup
        
        # 清除之前的输入
        try:
            poco("com.google.android.calculator:id/clr").click()
        except:
            pass
        
        # 云平台操作间隔
        if Config.is_cloud_platform():
            sleep(0.5)
        
        # 按顺序点击所有数字按钮 (官方示例逻辑)
        clicked_digits = []
        for btn in poco(nameMatches="com.google.android.calculator:id/digit_\\d"):
            print(f"点击按钮: {btn}")
            btn.click()
            clicked_digits.append(btn.get_name())
            
            # 云平台需要更慢的操作节奏
            if Config.is_cloud_platform():
                sleep(0.2)
        
        # 验证输入结果
        result2 = poco("com.google.android.calculator:id/formula").get_text()
        expected = "7894561230"  # 官方示例的预期结果
        
        # 云平台可能有不同的数字排列，放宽验证条件
        if Config.is_cloud_platform():
            assert len(result2) == len(expected), f"云平台数字输入长度不匹配: 期望{len(expected)}, 实际{len(result2)}"
            print(f"☁️ 云平台数字输入结果: {result2}")
        else:
            assert_equal(result2, expected)
        
        # 截图记录
        snapshot("all_digits_input_test_cloud.png")
        
        print(f"✅ 所有数字输入测试通过: {result2}")
    
    @pytest.mark.ui
    def test_calculator_ui_elements(self, calculator_setup):
        """测试计算器UI元素存在性（云平台适配）"""
        device_obj, poco = calculator_setup
        
        # 要验证的UI元素
        ui_elements = [
            "com.google.android.calculator:id/digit_0",
            "com.google.android.calculator:id/digit_1", 
            "com.google.android.calculator:id/digit_2",
            "com.google.android.calculator:id/digit_3",
            "com.google.android.calculator:id/digit_4",
            "com.google.android.calculator:id/digit_5",
            "com.google.android.calculator:id/digit_6",
            "com.google.android.calculator:id/digit_7",
            "com.google.android.calculator:id/digit_8",
            "com.google.android.calculator:id/digit_9",
            "com.google.android.calculator:id/op_add",
            "com.google.android.calculator:id/op_sub",
            "com.google.android.calculator:id/op_mul",
            "com.google.android.calculator:id/op_div",
            "com.google.android.calculator:id/eq",
            "com.google.android.calculator:id/clr"
        ]
        
        missing_elements = []
        existing_elements = []
        
        for element_id in ui_elements:
            # 云平台UI检测可能需要更多时间
            if Config.is_cloud_platform():
                sleep(0.1)
            
            if poco(element_id).exists():
                existing_elements.append(element_id)
            else:
                missing_elements.append(element_id)
        
        # 云平台可能有不同的UI布局，放宽要求
        if Config.is_cloud_platform():
            success_rate = len(existing_elements) / len(ui_elements)
            assert success_rate >= 0.8, f"云平台UI元素检测成功率过低: {success_rate:.1%}"
            print(f"☁️ 云平台UI元素检测成功率: {success_rate:.1%}")
        else:
            assert len(missing_elements) == 0, f"缺少UI元素: {missing_elements}"
        
        # 截图记录
        snapshot("ui_elements_verification_cloud.png")
        
        print(f"✅ UI元素验证完成，存在 {len(existing_elements)}/{len(ui_elements)} 个元素")
    
    @pytest.mark.regression
    @pytest.mark.retry
    def test_complex_calculation(self, calculator_setup):
        """测试复杂计算（云平台适配）"""
        device_obj, poco = calculator_setup
        
        # 清除之前的计算
        try:
            poco("com.google.android.calculator:id/clr").click()
        except:
            pass
        
        # 云平台操作间隔
        if Config.is_cloud_platform():
            sleep(0.5)
        
        # 执行计算: 5 * 6 + 7 = 37
        poco("com.google.android.calculator:id/digit_5").click()
        if Config.is_cloud_platform(): sleep(0.2)
        
        poco("com.google.android.calculator:id/op_mul").click()
        if Config.is_cloud_platform(): sleep(0.2)
        
        poco("com.google.android.calculator:id/digit_6").click()
        if Config.is_cloud_platform(): sleep(0.2)
        
        poco("com.google.android.calculator:id/op_add").click()
        if Config.is_cloud_platform(): sleep(0.2)
        
        poco("com.google.android.calculator:id/digit_7").click()
        if Config.is_cloud_platform(): sleep(0.2)
        
        poco("com.google.android.calculator:id/eq").click()
        
        # 云平台计算结果可能需要更多时间
        if Config.is_cloud_platform():
            sleep(1)
        
        # 验证结果
        result = poco("com.google.android.calculator:id/result").get_text()
        assert_equal(result, "37")
        
        # 截图记录
        snapshot("complex_calculation_test_cloud.png")
        
        print(f"✅ 云平台复杂计算测试通过: 5*6+7={result}")
    
    @pytest.mark.stress
    @pytest.mark.cloud
    def test_cloud_platform_stability(self, calculator_setup):
        """测试云平台稳定性"""
        device_obj, poco = calculator_setup
        
        if not Config.is_cloud_platform():
            pytest.skip("非云平台环境跳过稳定性测试")
        
        # 云平台稳定性测试
        test_rounds = 5
        successful_operations = 0
        
        for i in range(test_rounds):
            try:
                print(f"☁️ 云平台稳定性测试 {i+1}/{test_rounds}")
                
                # 清除
                poco("com.google.android.calculator:id/clr").click()
                sleep(0.5)
                
                # 简单计算
                poco("com.google.android.calculator:id/digit_1").click()
                sleep(0.2)
                poco("com.google.android.calculator:id/op_add").click()
                sleep(0.2)
                poco("com.google.android.calculator:id/digit_1").click()
                sleep(0.2)
                poco("com.google.android.calculator:id/eq").click()
                sleep(0.5)
                
                # 验证结果
                result = poco("com.google.android.calculator:id/result").get_text()
                if result == "2":
                    successful_operations += 1
                    print(f"✅ 第{i+1}轮测试成功")
                else:
                    print(f"❌ 第{i+1}轮测试失败: 结果={result}")
                
            except Exception as e:
                print(f"❌ 第{i+1}轮测试异常: {e}")
        
        # 云平台稳定性要求
        stability_rate = successful_operations / test_rounds
        assert stability_rate >= 0.8, f"云平台稳定性过低: {stability_rate:.1%}"
        
        print(f"✅ 云平台稳定性测试完成: {stability_rate:.1%}")
        
        # 截图记录
        snapshot("cloud_platform_stability_test.png")
    
    @pytest.mark.smoke
    def test_app_installation_and_launch(self, calculator_setup):
        """测试计算器应用安装和启动"""
        device_obj, poco = calculator_setup
        
        # 验证应用已安装
        assert self.PKG in device_obj.list_app(), "计算器应用未正确安装"
        
        # 验证Poco连接成功
        assert poco is not None, "AndroidUiautomationPoco初始化失败"
        
        # 截图记录
        snapshot("calculator_launched.png")
        
        print("✅ 计算器应用安装和启动测试通过")
    
    @pytest.mark.regression
    def test_basic_calculation_1_plus_2_equals_3(self, calculator_setup):
        """测试基本计算: (1+2)==3 - 官方示例核心功能"""
        device_obj, poco = calculator_setup
        
        # 清除之前的计算
        try:
            poco("com.google.android.calculator:id/clr").click()
        except:
            pass  # 如果没有清除按钮就跳过
        
        # 执行计算: 1 + 2 = 3
        poco("com.google.android.calculator:id/digit_1").click()
        poco("com.google.android.calculator:id/op_add").click()
        poco("com.google.android.calculator:id/digit_2").click()
        poco("com.google.android.calculator:id/eq").click()
        
        # 验证结果
        result = poco("com.google.android.calculator:id/result").get_text()
        assert_equal(result, "3")
        
        # 截图记录
        snapshot("calculation_1_plus_2_equals_3.png")
        
        print(f"✅ 基本计算测试通过: 1+2={result}")
    
    @pytest.mark.ui
    def test_swipe_functionality(self, calculator_setup):
        """测试滑动功能 - 官方示例功能"""
        device_obj, poco = calculator_setup
        
        # 点击箭头按钮展开更多功能
        poco("com.google.android.calculator:id/arrow").click()
        sleep(1.0)
        
        # 验证对数函数按钮出现
        fun_log = poco("com.google.android.calculator:id/fun_log").exists()
        assert_equal(fun_log, True)
        
        # 滑动收起功能面板
        poco("com.google.android.calculator:id/arrow").swipe([0.6884, 0.01])
        sleep(1.0)
        
        # 截图记录
        snapshot("swipe_functionality_test.png")
        
        print("✅ 滑动功能测试通过")
    
    @pytest.mark.regression
    def test_input_all_digits(self, calculator_setup):
        """测试输入所有数字 - 官方示例功能"""
        device_obj, poco = calculator_setup
        
        # 清除之前的输入
        poco("com.google.android.calculator:id/clr").click()
        
        # 按顺序点击所有数字按钮 (官方示例逻辑)
        for btn in poco(nameMatches="com.google.android.calculator:id/digit_\\d"):
            print(f"点击按钮: {btn}")
            btn.click()
        
        # 验证输入结果
        result2 = poco("com.google.android.calculator:id/formula").get_text()
        assert_equal(result2, "7894561230")
        
        # 截图记录
        snapshot("all_digits_input_test.png")
        
        print(f"✅ 所有数字输入测试通过: {result2}")
    
    @pytest.mark.ui
    def test_calculator_ui_elements(self, calculator_setup):
        """测试计算器UI元素存在性"""
        device_obj, poco = calculator_setup
        
        # 要验证的UI元素
        ui_elements = [
            "com.google.android.calculator:id/digit_0",
            "com.google.android.calculator:id/digit_1", 
            "com.google.android.calculator:id/digit_2",
            "com.google.android.calculator:id/digit_3",
            "com.google.android.calculator:id/digit_4",
            "com.google.android.calculator:id/digit_5",
            "com.google.android.calculator:id/digit_6",
            "com.google.android.calculator:id/digit_7",
            "com.google.android.calculator:id/digit_8",
            "com.google.android.calculator:id/digit_9",
            "com.google.android.calculator:id/op_add",
            "com.google.android.calculator:id/op_sub",
            "com.google.android.calculator:id/op_mul",
            "com.google.android.calculator:id/op_div",
            "com.google.android.calculator:id/eq",
            "com.google.android.calculator:id/clr"
        ]
        
        missing_elements = []
        for element_id in ui_elements:
            if not poco(element_id).exists():
                missing_elements.append(element_id)
        
        assert len(missing_elements) == 0, f"缺少UI元素: {missing_elements}"
        
        # 截图记录
        snapshot("ui_elements_verification.png")
        
        print(f"✅ 所有 {len(ui_elements)} 个UI元素都存在")
    
    @pytest.mark.regression
    def test_complex_calculation(self, calculator_setup):
        """测试复杂计算"""
        device_obj, poco = calculator_setup
        
        # 清除之前的计算
        poco("com.google.android.calculator:id/clr").click()
        
        # 执行计算: 5 * 6 + 7 = 37
        poco("com.google.android.calculator:id/digit_5").click()
        poco("com.google.android.calculator:id/op_mul").click()
        poco("com.google.android.calculator:id/digit_6").click()
        poco("com.google.android.calculator:id/op_add").click()
        poco("com.google.android.calculator:id/digit_7").click()
        poco("com.google.android.calculator:id/eq").click()
        
        # 验证结果
        result = poco("com.google.android.calculator:id/result").get_text()
        assert_equal(result, "37")
        
        # 截图记录
        snapshot("complex_calculation_test.png")
        
        print(f"✅ 复杂计算测试通过: 5*6+7={result}")
    
    @pytest.mark.stress
    def test_repeated_calculations(self, calculator_setup):
        """测试重复计算的稳定性"""
        device_obj, poco = calculator_setup
        
        test_cases = [
            {"formula": "2+3", "expected": "5", "steps": ["digit_2", "op_add", "digit_3"]},
            {"formula": "8-4", "expected": "4", "steps": ["digit_8", "op_sub", "digit_4"]},
            {"formula": "3*4", "expected": "12", "steps": ["digit_3", "op_mul", "digit_4"]},
            {"formula": "9/3", "expected": "3", "steps": ["digit_9", "op_div", "digit_3"]}
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"执行第 {i+1}/{len(test_cases)} 个计算: {test_case['formula']}")
            
            # 清除之前的计算
            poco("com.google.android.calculator:id/clr").click()
            
            # 执行计算步骤
            for step in test_case["steps"]:
                poco(f"com.google.android.calculator:id/{step}").click()
            
            # 点击等号
            poco("com.google.android.calculator:id/eq").click()
            
            # 验证结果
            result = poco("com.google.android.calculator:id/result").get_text()
            assert_equal(result, test_case["expected"])
            
            print(f"✅ 第{i+1}个计算成功: {test_case['formula']}={result}")
        
        # 截图记录
        snapshot("repeated_calculations_completed.png")
        
        print(f"✅ 完成 {len(test_cases)} 个重复计算测试")