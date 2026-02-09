# Douyin-Spark
基于 Playwright 的抖音自动化交互工具，采用纯视觉逻辑
🛠️ 技术底座
架构: Python + Playwright (Synchronous)

运行环境: X99 平台 / Debian (远程 SSH 环境部署)

通知系统: Telegram Bot API 全程联动

👁️ 核心方案：Tesla Vision v10.0
本项目放弃了传统的 wait_for_selector 逻辑，转而采用“多维视觉校验”：

生命迹象扫描: 通过检索搜索框、消息标题等多个特征点，确认面板是否真正渲染。

视觉稳定器: 采用循环采样机制，对抗动态加载的延迟。

鲁棒性重试: 结合 deque 队列，实现任务失败后的阶梯式重试。

在 2026 年 2 月 8 日凌晨，本项目经历了从 v22 到 v32 的高频迭代。虽然 Web 端的 headless 模式最终触发了工业级的滑块校验，但整个开发过程沉淀了大量的 UI 自动化对抗经验。

结论: 面对顶级风控，环境伪装比逻辑更重要。本项目目前作为“视觉识别方案”存档，未来计划转向物理层面的轨迹模拟。



# 抖音自动化脚本 - Tesla Vision v2.0

## 📋 功能特性

### ✨ 核心功能
- **纯视觉定位**: 不依赖不稳定的 CSS Class/ID，使用 `text=` 方式定位元素
- **非阻塞命令监听**: 实时响应 Telegram 命令，不会卡死
- **智能队列重试**: 失败后自动跳过并重试，最多 3 次尝试
- **完善错误处理**: 每个故障点自动截图并发送到 Telegram
- **真人模拟**: 随机延迟、hover 预热、区域激活

### 🔍 Tesla Vision 技术
- **象限定位系统 (v2.1 新增)**: 使用平面直角坐标系，在第一象限（右上）精确定位"私信"按钮，避免全屏搜索
- **悬停触发机制 (⭐ 关键改进)**: 移动到目标坐标后先悬停 1.5 秒触发面板显示，再点击（很多元素需要 hover 才显示）
- **真人轨迹移动**: 分 5 步从起点移动到终点，每步 50ms，模拟人类鼠标轨迹
- **多维视觉校验**: 点击后循环扫描屏幕，直到看到"消息列表"、"搜索框"或好友名字
- **滚动扫描机制**: 在会话列表中自动翻页查找目标用户（最多 6 页）
- **视觉退出**: 识别"关闭会话"、"消息列表"等文字按钮，确保回到初始状态

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install playwright requests

# 安装 Chromium 浏览器
playwright install chromium
```

### 2. 获取登录状态 (state.json)

**重要**: 脚本需要已登录的 Cookie 才能运行。

#### 方法 A: 使用 Playwright 代码生成器（推荐）

```bash
# 打开浏览器并手动登录
playwright codegen https://www.douyin.com/

# 登录后，在终端执行：
# 1. 点击右下角 "Persist storage state"
# 2. 保存为 state.json
```

#### 方法 B: 手动提取

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # 访问抖音并手动登录
    page.goto("https://www.douyin.com/")
    input("登录完成后按回车...")
    
    # 保存状态
    context.storage_state(path="state.json")
    browser.close()
    print("✅ state.json 已保存")
```

### 3. 配置脚本

编辑 `douyin_automation_refactored.py`:

```python
# Telegram Bot 配置
TG_BOT_TOKEN = "YOUR_BOT_TOKEN"  # 从 @BotFather 获取
TG_CHAT_ID = "YOUR_CHAT_ID"      # 你的 Telegram Chat ID

# 目标用户列表
TARGET_NAMES = ["用户A", "用户B", "用户C"]

# 发送的消息模板
SEND_TEXT = "自动烟花"  # 实际发送: "自动烟花 123"（带随机数）
```

### 4. 运行脚本

```bash
# 方式1: 守护进程模式（推荐）
python douyin_automation_refactored.py

# 方式2: 单次测试
python -c "from douyin_automation_refactored import run_task_queue, TARGET_NAMES; print(run_task_queue(TARGET_NAMES))"
```

---

## 💬 Telegram 命令

脚本启动后，可通过 Telegram 发送以下命令：

| 命令 | 功能 | 示例 |
|------|------|------|
| `/test` | 立即执行发送任务 | 直接发送 `/test` |
| `/status` | 查看当前状态和上次结果 | 直接发送 `/status` |
| `/help` | 显示帮助信息 | 直接发送 `/help` |

---

## 🔧 技术细节

### 队列重试机制

```
初始队列: [A, B, C]

第1轮:
  A 成功 ✅
  B 失败 ❌ → 加入队尾
  C 成功 ✅
  
队列变为: [B]

第2轮:
  B 成功 ✅
  
完成！
```

每个用户最多尝试 3 次，失败后自动截图并推送到 Telegram。

### 视觉校验流程

```python
1. 点击"私信"入口
2. 循环扫描 5 秒:
   - 是否看到"搜索框"? ✓
   - 是否看到"消息列表"? ✓
   - 是否看到"会话列表项"? ✓
   - 是否看到目标好友? ✓
3. 任一条件满足 → 面板开启成功
4. 5 秒内无匹配 → 重试（最多 3 次）
```

### 错误处理策略

| 故障点 | 行为 |
|--------|------|
| 面板未打开 | 截图 + TG 通知 + 重试 |
| 用户未找到 | 截图 + TG 通知 + 跳过 |
| 输入框未找到 | 截图 + TG 通知 + 跳过 |
| 发送失败 | 截图 + TG 通知 + 重试 |

所有截图保存在 `/tmp/douyin_screenshots/` 目录。

---

## 📊 日志示例

```
[2024-02-09 14:30:15] 🚀 Tesla Vision 任务启动
============================================================
[2024-02-09 14:30:20] 🌐 正在访问 douyin.com...
[2024-02-09 14:30:25] 👁️ 开始面板视觉校验流程...
[2024-02-09 14:30:26]    ✓ 检测到消息列表标题
[2024-02-09 14:30:26] ✅ 面板已处于开启状态，跳过点击
[2024-02-09 14:30:26] 🔍 视觉搜索好友: Akiyo
[2024-02-09 14:30:27] 🎯 视觉锁定: Akiyo (第 1 页)
[2024-02-09 14:30:27] 👆 点击进入会话: Akiyo
[2024-02-09 14:30:29] ✍️ 输入消息: 自动烟花 456
[2024-02-09 14:30:30] 🚀 消息已发送给 Akiyo
[2024-02-09 14:30:31] ✅ Akiyo 完成
[2024-02-09 14:30:31] ⏱️ 休息 3 秒...
```

---

## ⚠️ 注意事项

### 1. 登录状态维护
- `state.json` 会过期，需要定期更新（建议每周一次）
- 如果收到"请登录"相关错误，重新生成 state.json

### 2. 反爬虫应对
- 脚本已内置随机延迟（2-5 秒）
- 建议不要短时间内发送过多消息
- 可以调整 `time.sleep()` 参数增加延迟

### 3. 页面布局变更
- 如果抖音更新界面，可能需要调整定位逻辑
- 优先检查 `ensure_panel_open_robust()` 和 `find_user_in_list()` 函数

### 4. 资源占用
- 无头模式占用约 200-300MB 内存
- 截图文件会累积，建议定期清理 `/tmp/douyin_screenshots/`

---

## 🐛 故障排查

### Q1: "面板开启失败"
**原因**: 页面布局变更或网络延迟  
**解决**: 
1. 检查 Telegram 收到的截图
2. 尝试增加等待时间: `time.sleep(5)` → `time.sleep(10)`
3. 手动访问 douyin.com 确认页面正常

### Q2: "列表中未找到用户"
**原因**: 用户名不完全匹配或不在好友列表  
**解决**:
1. 确认 `TARGET_NAMES` 中的名字与实际完全一致（区分大小写）
2. 检查该用户是否真的在会话列表中
3. 增加滚动次数: `range(6)` → `range(10)`

### Q3: Telegram 命令无响应
**原因**: Bot Token 或 Chat ID 错误  
**解决**:
1. 验证 `TG_BOT_TOKEN` 是否正确
2. 获取 Chat ID: 给 Bot 发消息后访问  
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. 检查网络连接是否正常

### Q4: "未找到输入框"
**原因**: 会话窗口加载延迟  
**解决**:
1. 增加等待时间: `time.sleep(2)` → `time.sleep(5)`
2. 检查是否有弹窗干扰（如新手引导）

---

## 🔄 高级用法

### 1. 自定义消息内容

```python
# 动态消息
import datetime
message = f"早安！今天是 {datetime.datetime.now().strftime('%Y-%m-%d')}"

# 多行消息
message = """
你好！
这是第一行
这是第二行
"""
```

### 2. 定时任务（Cron）

```bash
# 编辑 crontab
crontab -e

# 每天 9:00 执行
0 9 * * * cd /path/to/script && python douyin_automation_refactored.py
```

### 3. 后台运行（nohup）

```bash
nohup python douyin_automation_refactored.py > output.log 2>&1 &

# 查看日志
tail -f output.log
```

### 4. Docker 部署

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install playwright requests
RUN playwright install --with-deps chromium

COPY douyin_automation_refactored.py /app/
COPY state.json /app/

WORKDIR /app
CMD ["python", "douyin_automation_refactored.py"]
```

---

## 📝 更新日志

### v2.1 (2024-02-09) - 象限定位系统
- ✅ **引入平面直角坐标系象限定位**（第一象限精确搜索，速度提升 4 倍）
- ✅ **悬停触发机制**（移动后悬停 1.5 秒再点击，支持隐藏元素）
- ✅ **真人轨迹移动**（分 5 步移动，每步 50ms，避免机器人特征）
- ✅ **5 重备用定位方案**（文字/属性/固定坐标多重保险）

### v2.0 (2024-02-09) - 非阻塞架构重构
- ✅ 重构为非阻塞架构，支持实时 Telegram 命令
- ✅ 实现 Tesla Vision 纯视觉定位系统
- ✅ 增强队列重试机制（失败自动跳过并重试）
- ✅ 完善错误处理（所有故障点自动截图）
- ✅ 优化视觉校验逻辑（多维度检测）

### v1.0 (原始版本)
- 基础自动化功能
- 简单的 Telegram 通知

---

## 📄 许可证

本脚本仅供学习交流使用，请勿用于商业目的或违反平台规则的行为。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**作者**: Tesla Vision Team  
**最后更新**: 2024-02-09
