# -*- coding: utf-8 -*-
import time
import os
import sys
import random
import datetime
import requests
from collections import deque
from playwright.sync_api import sync_playwright

# ================= ⚙️ 配置区域 =================
TG_BOT_TOKEN = "8595558212:AAFUsCgaBqTeU2wmj9odj7Xa44GlpHYTJng"
TG_CHAT_ID = "7121245032"

TARGET_NAMES = ["Akiyo", "赵靖祥"]
SEND_TEXT = "自动火花"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")
# ===============================================

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")
    sys.stdout.flush()

def send_tg_msg(text, photo_path=None):
    try:
        if photo_path and os.path.exists(photo_path):
            requests.post(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto", 
                          files={'photo': open(photo_path, 'rb')}, data={'chat_id': TG_CHAT_ID, 'caption': text})
        else:
            requests.post(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage", 
                          data={'chat_id': TG_CHAT_ID, 'text': text})
    except: pass

def take_screenshot(page, suffix):
    filename = f"/tmp/{suffix}_{datetime.datetime.now().strftime('%H%M%S')}.png"
    page.screenshot(path=filename)
    return filename

# --- 👁️ 深度视觉逻辑 (Deep Vision) ---

def is_panel_content_visible(page):
    """
    【特征识别】扫描屏幕，寻找私信面板的“生命迹象”
    """
    # 迹象1：看到了搜索框
    if page.locator("input[placeholder*='搜索']").is_visible(): return True
    # 迹象2：看到了“消息列表”标题
    if page.locator("text=消息列表").is_visible(): return True
    # 迹象3：看到了任何一个会话列表项
    if page.locator("[data-e2e='session-list-item']").first.is_visible(): return True
    # 迹象4：看到了名单里的任何一个人
    for name in TARGET_NAMES:
        if page.locator(f"text={name}").first.is_visible(): return True
    return False

def ensure_panel_open_robust(page):
    """
    【多维校验】确保面板真正弹出
    """
    log("👁️ 开始面板视觉校验...")
    
    for attempt in range(3):  # 最多尝试 3 次打开动作
        # 1. 先检查是否已经开了
        if is_panel_content_visible(page):
            log("✅ 视觉确认：面板已处于开启状态")
            return True

        log(f"⚡ 尝试第 {attempt+1} 次开启面板...")
        
        # 2. 定位并点击入口
        entrance = page.locator("text=私信, [data-e2e='im-entrance']").first
        if not entrance.is_visible():
            # 尝试移动一下鼠标，有时候悬浮才会显示
            page.mouse.move(1800, 30)
            time.sleep(0.5)
            
        if entrance.is_visible():
            entrance.hover()
            time.sleep(0.5)
            entrance.click(force=True)
            
            # 3. 【视觉稳定器】给 5 秒时间，每秒扫视一次
            for i in range(5):
                log(f"   ⏳ 等待渲染 ({i+1}/5)...")
                time.sleep(1)
                if is_panel_content_visible(page):
                    log("✅ 视觉捕捉成功：面板内容已加载")
                    return True
        else:
            log("❌ 屏幕上完全找不到【私信】入口")
            
    shot = take_screenshot(page, "error_panel_robust_fail")
    raise Exception(f"【视觉死角】尝试3次仍无法确认面板开启 (截图: {shot})")

def find_user_tesla(page, name):
    """
    特斯拉视觉找人：锁定列表区域滚动
    """
    log(f"🔍 视觉扫描好友: {name}")
    
    # 将鼠标移动到侧边栏区域 (通常在左侧) 激活滚动
    page.mouse.move(150, 400)
    
    target = page.locator(f"text={name}").first
    
    for i in range(6): # 增加滚动深度
        # 深度扫描：每滚一下看两次
        for _ in range(2):
            if target.is_visible():
                log(f"🎯 视觉锁定: {name}")
                return True
            time.sleep(0.5)
            
        log(f"   第 {i+1} 页未见，滚轮下行...")
        page.mouse.wheel(0, 800)
        time.sleep(1.2)
        
    return False

def exit_session_vision(page):
    """视觉退出"""
    log("🔙 寻找退出/关闭路径...")
    # 依次尝试点击“关闭会话”、“消息列表”、“返回”
    for tag in ["关闭会话", "消息列表", "返回"]:
        btn = page.locator(f"text={tag}").first
        if btn.is_visible():
            log(f"   点击文字按钮: {tag}")
            btn.click(force=True)
            return
    # 强制点击列表上方空白处
    page.mouse.click(150, 150)

def find_and_send_main(page, name):
    # 1. 强力开启/校验面板
    ensure_panel_open_robust(page)
    
    # 2. 找人
    if not find_user_tesla(page, name):
        shot = take_screenshot(page, f"not_found_{name}")
        return False, "列表中未看到此人", shot

    # 3. 交互
    try:
        log(f"👇 点击好友: {name}")
        page.locator(f"text={name}").first.click(force=True)
        time.sleep(2)

        # 视觉寻找输入框 (找可编辑区域)
        box = page.locator("[contenteditable='true']").last
        if not box.is_visible():
            shot = take_screenshot(page, f"no_input_{name}")
            return False, "未见输入框", shot

        box.click(force=True)
        msg = f"{SEND_TEXT} {random.randint(100, 999)}"
        box.fill(msg)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        log(f"🚀 发送成功")
        
        # 4. 退出
        time.sleep(1)
        exit_session_vision(page)
        time.sleep(1.5)
        return True, "成功", None
    except Exception as e:
        shot = take_screenshot(page, f"error_{name}")
        return False, str(e), shot

def run_queue_task():
    if not os.path.exists(STATE_FILE): raise Exception("缺少 state.json")

    # 任务队列
    queue = deque([{"name": n, "retries": 0} for n in TARGET_NAMES])
    final_status = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context(
            storage_state=STATE_FILE,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        page.goto("https://www.douyin.com/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        while queue:
            task = queue.popleft()
            name = task["name"]
            
            log(f"🔄 处理队列任务: {name} (尝试次数: {task['retries']+1})")
            
            ok, reason, shot = find_and_send_main(page, name)
            
            if ok:
                final_status[name] = "✅ 成功"
                time.sleep(random.randint(2, 5))
            else:
                log(f"❌ {name} 失败: {reason}")
                if task["retries"] < 2: # 最多重试2次(总计3次)
                    task["retries"] += 1
                    queue.append(task) # 扔回队尾
                else:
                    final_status[name] = f"❌ 最终失败 ({reason})"
                    if shot:
                        send_tg_msg(f"⛔️ {name} 彻底挂了: {reason}", shot)
                        if os.path.exists(shot): os.remove(shot)

        browser.close()
        return final_status

# --- 守护进程入口 ---
def main_loop():
    log("🚀 特斯拉视觉 v10.0 启动成功！")
    # 这里放你的定时和TG触发逻辑
    while True:
        # 为了简洁，这里演示直接手动测试逻辑
        # 你可以加上之前的 check_tg_commands()
        time.sleep(10)

if __name__ == "__main__":
    # 调试可以直接跑一次任务
    # run_queue_task()
    main_loop()