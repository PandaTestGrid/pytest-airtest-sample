"""
基于Airtest官方Calculator Demo的测试用例
使用pytest框架重构官方示例
"""

import pytest
import os
from pathlib import Path
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


class TestOfficialCalculator:
    """官方计算器Demo测试类
    
    使用 conftest.py 中的 calculator_setup fixture 连接设备，
    通过 Config.get_device_uri() 动态获取设备地址，兼容本地和云平台环境。
    """
    
    PKG = "com.google.android.calculator"
    APK_PATH = "demo_apps/com.google.android.calculator.apk"
    
    @pytest.mark.smoke
    def test_app_installation_and_launch(self, calculator_setup):
        """测试应用安装和启动"""
        device_obj, poco = calculator_setup
        
        # 验证应用已安装
        assert self.PKG in device_obj.list_app(), "计算器应用未正确安装"
        
        # 验证应用界面已显示
        assert poco(packageName=self.PKG).exists(), "计算器应用界面未显示"
        
        # 截图记录
        snapshot("calculator_launched.png")
    
    @pytest.mark.smoke
    def test_basic_calculation_1_plus_2(self, calculator_setup):
        """测试基本计算: 1+2=3 (官方示例)"""
        device_obj, poco = calculator_setup
        
        # 清除之前的计算
        if poco("com.google.android.calculator:id/clr").exists():
            poco("com.google.android.calculator:id/clr").click()
        
        # 执行计算: 1+2
        poco("com.google.android.calculator:id/digit_1").click()
        poco("com.google.android.calculator:id/op_add").click()
        poco("com.google.android.calculator:id/digit_2").click()
        poco("com.google.android.calculator:id/eq").click()
        
        # 验证结果
        result = poco("com.google.android.calculator:id/result").get_text()
        assert_equal(result, "3", "1+2的计算结果应该是3")
        
        # 截图记录
        snapshot("calculation_1_plus_2.png")
    
    @pytest.mark.ui
    def test_swipe_functionality(self, calculator_setup):
        """测试滑动功能 (官方示例)"""
        device_obj, poco = calculator_setup
        
        # 点击箭头按钮展开更多功能
        if poco("com.google.android.calculator:id/arrow").exists():
            poco("com.google.android.calculator:id/arrow").click()
            sleep(1.0)
            
            # 验证对数函数按钮出现
            fun_log = poco("com.google.android.calculator:id/fun_log").exists()
            assert_equal(fun_log, True, "对数函数按钮应该出现")
            
            # 滑动收起
            poco("com.google.android.calculator:id/arrow").swipe([0.6884, 0.01])
            sleep(1.0)
            
            # 截图记录
            snapshot("swipe_functionality.png")
    
    @pytest.mark.regression
    def test_input_all_digits(self, calculator_setup):
        """测试输入所有数字 (官方示例)"""
        device_obj, poco = calculator_setup
        
        # 清除显示
        if poco("com.google.android.calculator:id/clr").exists():
            poco("com.google.android.calculator:id/clr").click()
        
        # 点击所有数字按钮
        digits_clicked = []
        for btn in poco(nameMatches="com.google.android.calculator:id/digit_\\d"):
            digit_id = btn.get_name()
            digit_num = digit_id.split('_')[-1]
            print(f"点击数字按钮: {digit_num}")
            btn.click()
            digits_clicked.append(digit_num)
        
        # 验证输入结果
        result = poco("com.google.android.calculator:id/formula").get_text()
        expected = "7894561230"  # 官方示例的预期结果
        assert_equal(result, expected, f"输入所有数字的结果应该是{expected}")
        
        # 截图记录
        snapshot("all_digits_input.png")
        
        print(f"成功点击了 {len(digits_clicked)} 个数字按钮")
    
    @pytest.mark.ui
    def test_clear_functionality(self, calculator_setup):
        """测试清除功能"""
        device_obj, poco = calculator_setup
        
        # 输入一些数字
        poco("com.google.android.calculator:id/digit_1").click()
        poco("com.google.android.calculator:id/digit_2").click()
        poco("com.google.android.calculator:id/digit_3").click()
        
        # 验证有输入
        formula = poco("com.google.android.calculator:id/formula").get_text()
        assert formula == "123", "输入的数字应该显示为123"
        
        # 点击清除按钮
        poco("com.google.android.calculator:id/clr").click()
        
        # 验证已清除
        formula_after_clear = poco("com.google.android.calculator:id/formula").get_text()
        assert formula_after_clear == "" or formula_after_clear == "0", "清除后显示应该为空或0"
        
        # 截图记录
        snapshot("clear_functionality.png")
    
    @pytest.mark.regression
    def test_multiple_operations(self, calculator_setup):
        """测试多种运算操作"""
        device_obj, poco = calculator_setup
        
        test_cases = [
            {"operation": "5+3", "expected": "8", "desc": "加法"},
            {"operation": "9-4", "expected": "5", "desc": "减法"},
            {"operation": "6×7", "expected": "42", "desc": "乘法"},
            {"operation": "8÷2", "expected": "4", "desc": "除法"}
        ]
        
        for case in test_cases:
            # 清除之前的计算
            if poco("com.google.android.calculator:id/clr").exists():
                poco("com.google.android.calculator:id/clr").click()
            
            # 根据操作类型执行计算
            if case["operation"] == "5+3":
                poco("com.google.android.calculator:id/digit_5").click()
                poco("com.google.android.calculator:id/op_add").click()
                poco("com.google.android.calculator:id/digit_3").click()
            elif case["operation"] == "9-4":
                poco("com.google.android.calculator:id/digit_9").click()
                poco("com.google.android.calculator:id/op_sub").click()
                poco("com.google.android.calculator:id/digit_4").click()
            # 可以继续添加其他操作...
            
            # 点击等号
            poco("com.google.android.calculator:id/eq").click()
            
            # 验证结果
            result = poco("com.google.android.calculator:id/result").get_text()
            assert result == case["expected"], f"{case['desc']}计算错误: 期望{case['expected']}, 实际{result}"
            
            # 截图记录
            snapshot(f"operation_{case['desc']}.png")
            
            print(f"✅ {case['desc']}测试通过: {case['operation']} = {result}")
    
    @pytest.mark.ui
    def test_ui_elements_existence(self, calculator_setup):
        """测试UI元素存在性"""
        device_obj, poco = calculator_setup
        
        # 检查主要UI元素
        essential_elements = [
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
            "com.google.android.calculator:id/eq",
            "com.google.android.calculator:id/clr"
        ]
        
        missing_elements = []
        for element_id in essential_elements:
            if not poco(element_id).exists():
                missing_elements.append(element_id)
        
        assert len(missing_elements) == 0, f"缺少UI元素: {missing_elements}"
        
        print(f"✅ 所有 {len(essential_elements)} 个主要UI元素都存在")
        
        # 截图记录
        snapshot("ui_elements_check.png")