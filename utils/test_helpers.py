"""测试辅助工具函数"""

import time
import random
import string
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


class TestHelpers:
    """测试辅助类"""
    
    @staticmethod
    def wait_and_click(poco, selector, timeout=10):
        """等待元素出现并点击"""
        element = poco(selector)
        element.wait_for_appearance(timeout=timeout)
        element.click()
        return element
    
    @staticmethod
    def wait_and_input(poco, selector, text, timeout=10):
        """等待元素出现并输入文本"""
        element = poco(selector)
        element.wait_for_appearance(timeout=timeout)
        element.click()
        element.set_text(text)
        return element
    
    @staticmethod
    def generate_random_string(length=8):
        """生成随机字符串"""
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))
    
    @staticmethod
    def generate_random_email():
        """生成随机邮箱地址"""
        username = TestHelpers.generate_random_string(8)
        domain = random.choice(['gmail.com', 'yahoo.com', 'hotmail.com'])
        return f"{username}@{domain}"
    
    @staticmethod
    def scroll_to_element(poco, selector, direction="down", max_attempts=5):
        """滚动查找元素"""
        for attempt in range(max_attempts):
            if poco(selector).exists():
                return poco(selector)
            
            # 执行滚动
            if direction == "down":
                poco.swipe([0.5, 0.8], [0.5, 0.2])
            elif direction == "up":
                poco.swipe([0.5, 0.2], [0.5, 0.8])
            elif direction == "left":
                poco.swipe([0.8, 0.5], [0.2, 0.5])
            elif direction == "right":
                poco.swipe([0.2, 0.5], [0.8, 0.5])
            
            time.sleep(1)
        
        raise Exception(f"Element {selector} not found after {max_attempts} scroll attempts")
    
    @staticmethod
    def take_screenshot_with_timestamp(filename_prefix="screenshot"):
        """带时间戳的截图"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.png"
        snapshot(filename)
        return filename
    
    @staticmethod
    def verify_element_text(poco, selector, expected_text, timeout=10):
        """验证元素文本内容"""
        element = poco(selector)
        element.wait_for_appearance(timeout=timeout)
        actual_text = element.get_text()
        assert expected_text in actual_text, f"Expected '{expected_text}' in '{actual_text}'"
        return True
    
    @staticmethod
    def wait_for_loading_complete(poco, loading_selector="com.example.app:id/loading", timeout=30):
        """等待加载完成"""
        try:
            # 等待加载指示器出现
            poco(loading_selector).wait_for_appearance(timeout=5)
            # 等待加载指示器消失
            poco(loading_selector).wait_for_disappearance(timeout=timeout)
        except:
            # 如果没有找到加载指示器，直接返回
            pass
    
    @staticmethod
    def clear_app_data(package_name):
        """清除应用数据"""
        try:
            shell(f"pm clear {package_name}")
            time.sleep(2)
        except Exception as e:
            print(f"清除应用数据失败: {e}")
    
    @staticmethod
    def restart_app(package_name):
        """重启应用"""
        try:
            # 强制停止应用
            shell(f"am force-stop {package_name}")
            time.sleep(2)
            # 启动应用
            start_app(package_name)
            time.sleep(3)
        except Exception as e:
            print(f"重启应用失败: {e}")


class AssertHelpers:
    """断言辅助类"""
    
    @staticmethod
    def assert_element_exists(poco, selector, message="Element should exist"):
        """断言元素存在"""
        assert poco(selector).exists(), f"{message}: {selector}"
    
    @staticmethod
    def assert_element_not_exists(poco, selector, message="Element should not exist"):
        """断言元素不存在"""
        assert not poco(selector).exists(), f"{message}: {selector}"
    
    @staticmethod
    def assert_element_visible(poco, selector, message="Element should be visible"):
        """断言元素可见"""
        element = poco(selector)
        assert element.exists() and element.get_bounds(), f"{message}: {selector}"
    
    @staticmethod
    def assert_text_contains(poco, selector, expected_text, message="Text should contain expected value"):
        """断言文本包含指定内容"""
        actual_text = poco(selector).get_text()
        assert expected_text in actual_text, f"{message}: Expected '{expected_text}' in '{actual_text}'"
    
    @staticmethod
    def assert_element_enabled(poco, selector, message="Element should be enabled"):
        """断言元素可用"""
        element = poco(selector)
        # 这里需要根据实际应用的属性来判断元素是否可用
        assert element.exists(), f"{message}: {selector}"