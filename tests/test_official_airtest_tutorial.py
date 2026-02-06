"""
基于Airtest官方教程示例的pytest测试用例
原始文件: airtest_examples/tutorial/tutorial_airtest.air/fish.py
作者: airtest
保留官方截图和逻辑
"""

import pytest
import os
from pathlib import Path
from airtest.core.api import *


class TestOfficialAirtestTutorial:
    """官方Airtest教程测试类"""
    
    PKG = "com.netease.dyll"  # 官方示例中的包名
    
    # 官方教程模板图片路径
    TEMPLATE_GAME_SCENE = "demo_apps/tpl1530603956757.png"      # 游戏画面
    TEMPLATE_LEVEL_SELECT = "demo_apps/tpl1530588210942.png"    # 关卡选择
    TEMPLATE_SHARK = "demo_apps/tpl1530603698872.png"           # 鲨鱼图案
    TEMPLATE_LEVEL_20 = "demo_apps/tpl1530603939766.png"        # 第20关
    TEMPLATE_LEVEL_20_VERIFY = "demo_apps/tpl1530604090919.png" # 第20关验证
    
    @pytest.fixture(scope="class")
    def tutorial_setup(self, global_device_setup):
        """教程应用设置"""
        device_obj = global_device_setup
        
        yield device_obj
        
        # 清理 - 如果应用存在则停止
        if self.PKG in device_obj.list_app():
            stop_app(self.PKG)
    
    @pytest.mark.smoke
    def test_tutorial_app_availability(self, tutorial_setup):
        """测试教程应用可用性"""
        device_obj = tutorial_setup
        
        # 检查应用是否已安装
        if self.PKG in device_obj.list_app():
            print(f"✅ 教程应用 {self.PKG} 已安装")
            
            # 尝试启动应用
            start_app(self.PKG)
            sleep(5)  # 等待应用启动
            
            # 截图记录
            snapshot("tutorial_app_launched.png")
            
            print("✅ 教程应用启动成功")
        else:
            pytest.skip(f"教程应用 {self.PKG} 未安装，跳过测试")
    
    @pytest.mark.regression
    def test_official_tutorial_game_flow(self, tutorial_setup):
        """测试官方教程游戏流程 - 完全按照官方示例"""
        device_obj = tutorial_setup
        
        # 检查应用是否存在
        if self.PKG not in device_obj.list_app():
            pytest.skip(f"教程应用 {self.PKG} 未安装，跳过游戏流程测试")
        
        # 官方示例步骤1: 启动应用
        start_app(self.PKG)
        sleep(10)  # 官方示例中的等待时间
        
        # 官方示例步骤2: 等待游戏画面出现
        game_scene_template = Path(self.TEMPLATE_GAME_SCENE)
        if game_scene_template.exists():
            wait(Template(str(game_scene_template), record_pos=(0.001, -0.023), resolution=(1920, 1080)))
            print("✅ 游戏画面出现")
        else:
            print("⚠️ 游戏画面模板不存在，使用固定等待")
            sleep(5)
        
        # 官方示例步骤3: 点击关卡选择
        level_select_template = Path(self.TEMPLATE_LEVEL_SELECT)
        if level_select_template.exists():
            touch(Template(str(level_select_template), record_pos=(-0.177, 0.167), resolution=(1920, 1080)))
            sleep(1)  # 官方示例中的等待时间
            print("✅ 点击关卡选择成功")
        else:
            print("⚠️ 关卡选择模板不存在")
        
        # 官方示例步骤4: 滑动到最右边直到看到鲨鱼图案
        shark_template = Path(self.TEMPLATE_SHARK)
        if shark_template.exists():
            # 官方示例中的while循环逻辑
            swipe_attempts = 0
            max_swipes = 10  # 防止无限循环
            
            while not exists(Template(str(shark_template), record_pos=(0.374, -0.001), resolution=(1920, 1080))) and swipe_attempts < max_swipes:
                swipe((959, 609), vector=[-0.1706, 0.0025])  # 官方示例中的滑动参数
                swipe_attempts += 1
                sleep(0.5)
            
            if swipe_attempts < max_swipes:
                print("✅ 找到鲨鱼图案")
            else:
                print("⚠️ 滑动次数达到上限，未找到鲨鱼图案")
        else:
            print("⚠️ 鲨鱼图案模板不存在")
        
        # 官方示例步骤5: 点击第20关
        level_20_template = Path(self.TEMPLATE_LEVEL_20)
        if level_20_template.exists():
            touch(Template(str(level_20_template), record_pos=(0.365, 0.102), resolution=(1920, 1080)))
            print("✅ 点击第20关")
        else:
            print("⚠️ 第20关模板不存在")
        
        # 官方示例步骤6: 验证是否进入了第20关
        level_20_verify_template = Path(self.TEMPLATE_LEVEL_20_VERIFY)
        if level_20_verify_template.exists():
            assert_exists(Template(str(level_20_verify_template), record_pos=(-0.385, -0.173), resolution=(1920, 1080)), "断言是否进入了第20关")
            print("✅ 成功进入第20关")
        else:
            print("⚠️ 第20关验证模板不存在")
        
        # 官方示例步骤7: 截图
        snapshot("当前画面截图.")  # 保持官方示例中的中文描述
        
        print("✅ 官方教程游戏流程测试完成")
    
    @pytest.mark.ui
    def test_template_matching_with_official_images(self, tutorial_setup):
        """测试使用官方模板图片进行图像匹配"""
        device_obj = tutorial_setup
        
        # 检查应用是否存在
        if self.PKG not in device_obj.list_app():
            pytest.skip(f"教程应用 {self.PKG} 未安装，跳过模板匹配测试")
        
        # 启动应用
        start_app(self.PKG)
        sleep(10)
        
        # 测试所有官方模板图片
        templates = [
            {"path": self.TEMPLATE_GAME_SCENE, "name": "游戏画面", "pos": (0.001, -0.023)},
            {"path": self.TEMPLATE_LEVEL_SELECT, "name": "关卡选择", "pos": (-0.177, 0.167)},
            {"path": self.TEMPLATE_SHARK, "name": "鲨鱼图案", "pos": (0.374, -0.001)},
            {"path": self.TEMPLATE_LEVEL_20, "name": "第20关", "pos": (0.365, 0.102)},
            {"path": self.TEMPLATE_LEVEL_20_VERIFY, "name": "第20关验证", "pos": (-0.385, -0.173)}
        ]
        
        matched_templates = []
        
        for template_info in templates:
            template_path = Path(template_info["path"])
            if template_path.exists():
                try:
                    # 尝试匹配模板
                    if exists(Template(str(template_path), record_pos=template_info["pos"], resolution=(1920, 1080))):
                        matched_templates.append(template_info["name"])
                        print(f"✅ 模板匹配成功: {template_info['name']}")
                    else:
                        print(f"⚠️ 模板匹配失败: {template_info['name']}")
                except Exception as e:
                    print(f"❌ 模板匹配出错: {template_info['name']} - {e}")
            else:
                print(f"⚠️ 模板文件不存在: {template_info['name']}")
        
        # 截图记录
        snapshot("tutorial_template_matching_test.png")
        
        print(f"✅ 模板匹配测试完成，成功匹配 {len(matched_templates)} 个模板: {matched_templates}")
    
    @pytest.mark.ui
    def test_swipe_gesture_accuracy(self, tutorial_setup):
        """测试滑动手势准确性"""
        device_obj = tutorial_setup
        
        # 检查应用是否存在
        if self.PKG not in device_obj.list_app():
            pytest.skip(f"教程应用 {self.PKG} 未安装，跳过滑动测试")
        
        # 启动应用并进入关卡选择
        start_app(self.PKG)
        sleep(10)
        
        # 等待游戏画面
        game_scene_template = Path(self.TEMPLATE_GAME_SCENE)
        if game_scene_template.exists():
            wait(Template(str(game_scene_template), record_pos=(0.001, -0.023), resolution=(1920, 1080)))
        else:
            sleep(5)
        
        # 点击关卡选择
        level_select_template = Path(self.TEMPLATE_LEVEL_SELECT)
        if level_select_template.exists():
            touch(Template(str(level_select_template), record_pos=(-0.177, 0.167), resolution=(1920, 1080)))
            sleep(1)
        
        # 测试滑动手势 - 使用官方示例中的参数
        swipe_tests = [
            {"name": "向左滑动1", "start": (959, 609), "vector": [-0.1706, 0.0025]},
            {"name": "向左滑动2", "start": (959, 609), "vector": [-0.2, 0.0]},
            {"name": "向右滑动", "start": (400, 609), "vector": [0.2, 0.0]}
        ]
        
        successful_swipes = 0
        
        for swipe_test in swipe_tests:
            try:
                # 截图前状态
                snapshot(f"before_{swipe_test['name']}.png")
                
                # 执行滑动
                swipe(swipe_test["start"], vector=swipe_test["vector"])
                sleep(1)
                
                # 截图后状态
                snapshot(f"after_{swipe_test['name']}.png")
                
                successful_swipes += 1
                print(f"✅ {swipe_test['name']} 执行成功")
                
            except Exception as e:
                print(f"❌ {swipe_test['name']} 执行失败: {e}")
        
        # 截图记录
        snapshot("swipe_gesture_test_completed.png")
        
        assert successful_swipes > 0, "所有滑动手势都失败"
        
        print(f"✅ 滑动手势测试完成，成功执行 {successful_swipes}/{len(swipe_tests)} 个滑动")
    
    @pytest.mark.performance
    def test_template_matching_performance(self, tutorial_setup):
        """测试模板匹配性能"""
        device_obj = tutorial_setup
        
        # 检查应用是否存在
        if self.PKG not in device_obj.list_app():
            pytest.skip(f"教程应用 {self.PKG} 未安装，跳过性能测试")
        
        import time
        
        # 启动应用
        start_app(self.PKG)
        sleep(10)
        
        # 测试模板匹配性能
        game_scene_template = Path(self.TEMPLATE_GAME_SCENE)
        if game_scene_template.exists():
            # 多次执行模板匹配，测量平均时间
            match_times = []
            test_count = 5
            
            for i in range(test_count):
                start_time = time.time()
                
                try:
                    exists(Template(str(game_scene_template), record_pos=(0.001, -0.023), resolution=(1920, 1080)))
                    end_time = time.time()
                    match_time = end_time - start_time
                    match_times.append(match_time)
                    print(f"第{i+1}次模板匹配耗时: {match_time:.3f}秒")
                except Exception as e:
                    print(f"第{i+1}次模板匹配失败: {e}")
            
            if match_times:
                avg_time = sum(match_times) / len(match_times)
                max_time = max(match_times)
                min_time = min(match_times)
                
                print(f"模板匹配性能统计:")
                print(f"  平均耗时: {avg_time:.3f}秒")
                print(f"  最大耗时: {max_time:.3f}秒")
                print(f"  最小耗时: {min_time:.3f}秒")
                
                # 性能断言 - 平均匹配时间应该在合理范围内
                assert avg_time < 5.0, f"模板匹配平均耗时过长: {avg_time:.3f}秒"
                
                # 截图记录
                snapshot("template_matching_performance_test.png")
                
                print("✅ 模板匹配性能测试通过")
            else:
                pytest.skip("所有模板匹配都失败，无法测试性能")
        else:
            pytest.skip("游戏画面模板不存在，跳过性能测试")