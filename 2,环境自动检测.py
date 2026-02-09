#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证配置和基础功能
"""

import os
import sys
import requests
from playwright.sync_api import sync_playwright

# 导入主脚本配置
try:
    from douyin_automation_refactored import (
        TG_BOT_TOKEN, TG_CHAT_ID, STATE_FILE, 
        send_tg_msg, log
    )
except ImportError:
    print("❌ 无法导入主脚本，请确保 douyin_automation_refactored.py 在同一目录")
    sys.exit(1)

def test_telegram_config():
    """测试 Telegram 配置"""
    print("\n" + "=" * 60)
    print("📱 测试 Telegram 配置")
    print("=" * 60)
    
    print(f"Bot Token: {TG_BOT_TOKEN[:20]}...")
    print(f"Chat ID: {TG_CHAT_ID}")
    
    try:
        # 测试发送消息
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        response = requests.post(
            url,
            data={'chat_id': TG_CHAT_ID, 'text': '🧪 测试消息 - 如果你看到这条消息，说明配置正确！'}
        )
        
        if response.status_code == 200:
            print("✅ Telegram 配置正确，测试消息已发送")
            return True
        else:
            print(f"❌ Telegram 发送失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Telegram 测试异常: {e}")
        return False

def test_state_file():
    """测试 state.json 文件"""
    print("\n" + "=" * 60)
    print("📄 测试 state.json")
    print("=" * 60)
    
    print(f"文件路径: {STATE_FILE}")
    
    if not os.path.exists(STATE_FILE):
        print("❌ state.json 不存在")
        print("💡 请先运行 generate_state.py 生成登录状态")
        return False
    
    file_size = os.path.getsize(STATE_FILE)
    print(f"✅ 文件存在 (大小: {file_size} 字节)")
    
    # 尝试加载
    try:
        import json
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
        
        if 'cookies' in data:
            cookie_count = len(data['cookies'])
            print(f"✅ 包含 {cookie_count} 个 Cookie")
            return True
        else:
            print("⚠️ 文件格式可能不正确")
            return False
    except Exception as e:
        print(f"❌ 文件加载失败: {e}")
        return False

def test_browser_launch():
    """测试浏览器启动"""
    print("\n" + "=" * 60)
    print("🌐 测试浏览器启动")
    print("=" * 60)
    
    try:
        with sync_playwright() as p:
            print("启动浏览器...")
            browser = p.chromium.launch(headless=True)
            
            print("创建上下文...")
            context = browser.new_context(
                storage_state=STATE_FILE if os.path.exists(STATE_FILE) else None,
                viewport={"width": 1920, "height": 1080}
            )
            
            print("打开页面...")
            page = context.new_page()
            
            print("访问抖音...")
            page.goto("https://www.douyin.com/", wait_until="domcontentloaded", timeout=30000)
            
            # 截图验证
            screenshot_path = "/tmp/test_screenshot.png"
            page.screenshot(path=screenshot_path)
            print(f"✅ 截图已保存: {screenshot_path}")
            
            # 检查是否登录
            try:
                if page.locator("text=登录").is_visible(timeout=2000):
                    print("⚠️ 检测到登录按钮，可能未登录")
                else:
                    print("✅ 未检测到登录按钮，可能已登录")
            except:
                print("✅ 未检测到登录按钮，可能已登录")
            
            browser.close()
            return True
    except Exception as e:
        print(f"❌ 浏览器测试失败: {e}")
        return False

def test_visual_detection():
    """测试视觉检测功能"""
    print("\n" + "=" * 60)
    print("👁️ 测试视觉检测")
    print("=" * 60)
    
    try:
        from douyin_automation_refactored import is_panel_content_visible
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                storage_state=STATE_FILE if os.path.exists(STATE_FILE) else None,
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            page.goto("https://www.douyin.com/", wait_until="domcontentloaded", timeout=30000)
            
            print("测试面板检测函数...")
            result = is_panel_content_visible(page)
            print(f"面板可见: {result}")
            
            browser.close()
            return True
    except Exception as e:
        print(f"❌ 视觉检测测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🧪 抖音自动化脚本 - 配置测试")
    print("=" * 60)
    
    results = {
        "Telegram 配置": test_telegram_config(),
        "state.json 文件": test_state_file(),
        "浏览器启动": test_browser_launch(),
        "视觉检测": test_visual_detection()
    }
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！可以开始使用脚本了")
        print("💡 运行主程序: python douyin_automation_refactored.py")
    else:
        print("⚠️ 部分测试失败，请检查配置")
        print("💡 参考 README.md 获取帮助")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 测试已取消")
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
