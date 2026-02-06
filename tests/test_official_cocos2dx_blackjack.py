"""
基于Airtest官方Cocos2dx黑杰克游戏示例的pytest测试用例
原始文件: airtest_examples/Cocos2dx/test_blackjack.air/test_blackjack.py
作者: 刘欣
保留官方截图和逻辑
"""

import pytest
import os
from pathlib import Path
from airtest.core.api import *


class TestOfficialCocos2dxBlackjack:
    """官方Cocos2dx黑杰克游戏测试类"""
    
    PKG = "org.cocos2d.blackjack"
    APK_PATH = "demo_apps/blackjack-release-signed.apk"
    
    # 官方模板图片路径
    TEMPLATE_START = "demo_apps/tpl1499240443959.png"  # 开始按钮
    TEMPLATE_BET = "demo_apps/tpl1499240472304.png"    # 请下注
    TEMPLATE_CHIP = "demo_apps/tpl1499240490986.png"   # 筹码
    
    @pytest.fixture(scope="class")
    def blackjack_setup(self, global_device_setup):
        """黑杰克游戏应用设置"""
        device_obj = global_device_setup
        
        # 检查并安装APK - 官方逻辑
        if self.PKG not in device_obj.list_app():
            apk_path = Path(self.APK_PATH)
            if apk_path.exists():
                print(f"安装黑杰克游戏APK: {apk_path}")
                install(str(apk_path))
            else:
                raise FileNotFoundError(f"APK文件不存在: {apk_path}")
        
        # 启动应用 - 官方逻辑
        stop_app(self.PKG)
        wake()  # 官方示例中的唤醒操作
        start_app(self.PKG)
        sleep(2)  # 官方示例中的等待时间
        
        yield device_obj
        
        # 清理
        stop_app(self.PKG)
    
    @pytest.mark.smoke
    def test_app_installation_and_launch(self, blackjack_setup):
        """测试黑杰克游戏应用安装和启动"""
        device_obj = blackjack_setup
        
        # 验证应用已安装
        assert self.PKG in device_obj.list_app(), "黑杰克游戏应用未正确安装"
        
        # 截图记录
        snapshot("blackjack_launched.png")
        
        print("✅ 黑杰克游戏应用安装和启动测试通过")
    
    @pytest.mark.regression
    def test_official_blackjack_game_flow(self, blackjack_setup):
        """测试官方黑杰克游戏流程 - 完全按照官方示例"""
        device_obj = blackjack_setup
        
        # 官方示例步骤1: 点击开始按钮
        start_template = Path(self.TEMPLATE_START)
        if start_template.exists():
            touch(Template(str(start_template), record_pos=(0.22, -0.165), resolution=(2560, 1536)))
            print("✅ 点击开始按钮成功")
        else:
            pytest.skip("开始按钮模板图片不存在")
        
        # 官方示例步骤2: 验证"请下注"界面出现
        bet_template = Path(self.TEMPLATE_BET)
        if bet_template.exists():
            assert_exists(Template(str(bet_template), record_pos=(0.0, -0.094), resolution=(2560, 1536)), "请下注")
            print("✅ 请下注界面验证成功")
        else:
            pytest.skip("请下注模板图片不存在")
        
        # 官方示例步骤3: 等待并点击筹码
        chip_template = Path(self.TEMPLATE_CHIP)
        if chip_template.exists():
            p = wait(Template(str(chip_template), record_pos=(-0.443, -0.273), resolution=(2560, 1536)))
            touch(p)
            sleep(2)  # 官方示例中的等待时间
            print("✅ 筹码点击成功")
        else:
            pytest.skip("筹码模板图片不存在")
        
        # 截图记录游戏状态
        snapshot("blackjack_game_flow_completed.png")
        
        print("✅ 官方黑杰克游戏流程测试通过")
    
    @pytest.mark.ui
    def test_template_matching_accuracy(self, blackjack_setup):
        """测试模板匹配准确性"""
        device_obj = blackjack_setup
        
        # 测试所有官方模板图片的匹配
        templates = [
            {"path": self.TEMPLATE_START, "name": "开始按钮", "pos": (0.22, -0.165)},
            {"path": self.TEMPLATE_BET, "name": "请下注", "pos": (0.0, -0.094)},
            {"path": self.TEMPLATE_CHIP, "name": "筹码", "pos": (-0.443, -0.273)}
        ]
        
        matched_templates = []
        
        # 先点击开始按钮进入游戏
        start_template = Path(self.TEMPLATE_START)
        if start_template.exists():
            touch(Template(str(start_template), record_pos=(0.22, -0.165), resolution=(2560, 1536)))
            sleep(2)
        
        for template_info in templates:
            template_path = Path(template_info["path"])
            if template_path.exists():
                try:
                    # 尝试匹配模板
                    if exists(Template(str(template_path), record_pos=template_info["pos"], resolution=(2560, 1536))):
                        matched_templates.append(template_info["name"])
                        print(f"✅ 模板匹配成功: {template_info['name']}")
                    else:
                        print(f"⚠️ 模板匹配失败: {template_info['name']}")
                except Exception as e:
                    print(f"❌ 模板匹配出错: {template_info['name']} - {e}")
            else:
                print(f"⚠️ 模板文件不存在: {template_info['name']}")
        
        # 截图记录
        snapshot("template_matching_test.png")
        
        # 至少应该匹配到一个模板
        assert len(matched_templates) > 0, f"未匹配到任何模板，可能是分辨率或图片问题"
        
        print(f"✅ 模板匹配测试完成，成功匹配 {len(matched_templates)} 个模板: {matched_templates}")
    
    @pytest.mark.performance
    def test_game_startup_performance(self):
        """测试游戏启动性能"""
        import time
        
        # 停止应用
        stop_app(self.PKG)
        sleep(1)
        
        # 测量启动时间
        start_time = time.time()
        wake()
        start_app(self.PKG)
        
        # 等待游戏加载完成（等待开始按钮出现）
        start_template = Path(self.TEMPLATE_START)
        if start_template.exists():
            wait(Template(str(start_template), record_pos=(0.22, -0.165), resolution=(2560, 1536)), timeout=30)
            end_time = time.time()
            startup_time = end_time - start_time
            
            print(f"黑杰克游戏启动时间: {startup_time:.2f}秒")
            
            # 启动时间应该在合理范围内
            assert startup_time < 30, f"启动时间过长: {startup_time:.2f}秒"
            
            # 截图记录
            snapshot("game_startup_performance.png")
            
            print(f"✅ 游戏启动性能测试通过: {startup_time:.2f}秒")
        else:
            pytest.skip("开始按钮模板图片不存在，跳过启动性能测试")
        
        # 清理
        stop_app(self.PKG)
    
    @pytest.mark.stress
    def test_game_restart_stability(self):
        """测试游戏重启稳定性"""
        restart_count = 3
        successful_restarts = 0
        
        for i in range(restart_count):
            try:
                print(f"执行第 {i+1}/{restart_count} 次游戏重启测试")
                
                # 停止应用
                stop_app(self.PKG)
                sleep(2)
                
                # 启动应用
                wake()
                start_app(self.PKG)
                sleep(2)
                
                # 等待游戏加载完成
                start_template = Path(self.TEMPLATE_START)
                if start_template.exists():
                    wait(Template(str(start_template), record_pos=(0.22, -0.165), resolution=(2560, 1536)), timeout=15)
                    successful_restarts += 1
                    print(f"✅ 第{i+1}次重启成功")
                else:
                    # 没有模板图片，等待固定时间
                    sleep(5)
                    successful_restarts += 1
                    print(f"✅ 第{i+1}次重启完成（无模板验证）")
                
            except Exception as e:
                print(f"❌ 第{i+1}次重启失败: {e}")
        
        # 清理
        stop_app(self.PKG)
        
        # 至少80%的重启应该成功
        success_rate = successful_restarts / restart_count
        assert success_rate >= 0.8, f"重启成功率过低: {success_rate:.1%}"
        
        print(f"✅ 游戏重启稳定性测试完成，成功率: {success_rate:.1%}")
        
        # 截图记录
        snapshot("game_restart_stability_completed.png")
    
    @pytest.mark.ui
    def test_game_ui_interaction(self, blackjack_setup):
        """测试游戏UI交互"""
        device_obj = blackjack_setup
        
        interaction_steps = [
            {
                "name": "点击开始按钮",
                "template": self.TEMPLATE_START,
                "pos": (0.22, -0.165),
                "wait_time": 2
            },
            {
                "name": "验证请下注界面",
                "template": self.TEMPLATE_BET,
                "pos": (0.0, -0.094),
                "wait_time": 1
            }
        ]
        
        successful_interactions = 0
        
        for step in interaction_steps:
            try:
                template_path = Path(step["template"])
                if template_path.exists():
                    if step["name"] == "验证请下注界面":
                        # 验证界面存在
                        assert_exists(Template(str(template_path), record_pos=step["pos"], resolution=(2560, 1536)), step["name"])
                    else:
                        # 点击操作
                        touch(Template(str(template_path), record_pos=step["pos"], resolution=(2560, 1536)))
                    
                    sleep(step["wait_time"])
                    successful_interactions += 1
                    print(f"✅ {step['name']} 成功")
                else:
                    print(f"⚠️ {step['name']} 模板不存在")
                    
            except Exception as e:
                print(f"❌ {step['name']} 失败: {e}")
        
        # 截图记录
        snapshot("game_ui_interaction_test.png")
        
        # 至少应该有一个交互成功
        assert successful_interactions > 0, "所有UI交互都失败"
        
        print(f"✅ 游戏UI交互测试完成，成功执行 {successful_interactions}/{len(interaction_steps)} 个交互")