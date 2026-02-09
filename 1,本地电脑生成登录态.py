#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅助工具：生成 state.json
用于首次登录或更新登录状态
"""

from playwright.sync_api import sync_playwright
import os

def generate_state_json():
    """交互式生成 state.json"""
    print("=" * 60)
    print("🔐 抖音登录状态生成工具")
    print("=" * 60)
    print()
    print("📋 操作步骤:")
    print("1. 浏览器将自动打开抖音网页")
    print("2. 请手动完成登录（扫码或密码登录）")
    print("3. 登录成功后，在终端按回车键")
    print("4. 程序将自动保存登录状态到 state.json")
    print()
    input("准备好后按回车开始...")
    
    with sync_playwright() as p:
        # 启动可见浏览器
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        
        print("\n🌐 正在打开抖音...")
        page.goto("https://www.douyin.com/", wait_until="domcontentloaded")
        
        print("\n⏳ 请在浏览器中完成登录...")
        print("💡 提示: 登录成功后，你应该能看到右上角显示你的头像")
        input("\n✅ 登录完成后按回车...")
        
        # 保存状态
        output_file = "state.json"
        context.storage_state(path=output_file)
        
        browser.close()
        
        # 验证文件
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"\n✅ 成功!")
            print(f"📄 文件: {os.path.abspath(output_file)}")
            print(f"📊 大小: {file_size} 字节")
            print("\n💡 下一步: 将此文件放在脚本同一目录下，然后运行主程序")
        else:
            print("\n❌ 错误: 文件生成失败")

if __name__ == "__main__":
    try:
        generate_state_json()
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
