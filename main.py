import logging
import random
import subprocess
import sys
import time
from pathlib import Path

import colorama
from playwright.sync_api import sync_playwright

from url_parser import extract_aweme_id
from browser import BrowserManager
from api import DouyinCommentClient
from lottery import draw_lucky_users

colorama.init()
GREEN = colorama.Fore.GREEN
RESET = colorama.Style.RESET_ALL

logging.basicConfig(level=logging.WARNING)


def check_chromium():
    """Check if Playwright Chromium is installed, auto-download if not."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        return True
    except Exception:
        return False


def install_chromium():
    """Download Playwright Chromium browser."""
    print("首次运行，需要下载 Chromium 浏览器（约100MB）...")
    print("正在下载，请稍候...")
    try:
        from playwright._impl._driver import compute_driver_executable
        driver_executable = compute_driver_executable()
        result = subprocess.run(
            [str(driver_executable), "install", "chromium"],
            capture_output=False,
        )
        if result.returncode == 0:
            print("Chromium 下载完成！")
            return True
        else:
            print("下载失败，请手动执行: playwright install chromium")
            return False
    except Exception as e:
        print(f"下载失败: {e}")
        print("请手动执行: playwright install chromium")
        return False


def print_banner():
    print("=" * 50)
    print("      抖音评论区幸运用户抽取工具")
    print("=" * 50)
    print()


def scroll_animation(all_nicknames, final_nickname, rounds=12):
    """Scrolling effect: rapidly display random names, slow down, land on final."""
    for i in range(rounds):
        name = random.choice(all_nicknames)
        delay = 0.05 + (i / rounds) * 0.25
        sys.stdout.write(f"\r    {name}  ")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(f"\r    {GREEN}★ {final_nickname} ★{RESET}  \n")
    sys.stdout.flush()


def main():
    print_banner()

    # Check Chromium
    if not check_chromium():
        if not install_chromium():
            print("无法运行，请手动执行: playwright install chromium")
            sys.exit(1)
        print()

    # Step 1: Get user input
    url = input("请输入抖音视频链接: ").strip()
    if not url:
        print("链接不能为空！")
        sys.exit(1)

    try:
        extract_aweme_id(url)
    except ValueError:
        print("无法识别的抖音链接，请检查后重试。")
        sys.exit(1)

    count_input = input("请输入抽取人数: ").strip()
    try:
        count = int(count_input)
        if count <= 0:
            raise ValueError
    except ValueError:
        print("请输入有效的正整数！")
        sys.exit(1)

    # Step 2: Open browser and intercept signatures
    print()
    print("正在打开浏览器，请登录抖音...")
    browser = BrowserManager(url)
    try:
        ctx = browser.capture_request_context()
    except RuntimeError as e:
        print(f"错误: {e}")
        sys.exit(1)

    # Step 3: Fetch all comments
    print()
    print("正在获取全部评论...")
    try:
        with DouyinCommentClient(
            headers=ctx.headers,
            cookies=ctx.cookies,
            params=ctx.params,
            aweme_id=ctx.aweme_id,
        ) as client:
            all_comments = client.fetch_all_comments()
    except Exception as e:
        print(f"获取评论失败: {e}")
        sys.exit(1)

    if not all_comments:
        print("没有找到任何评论。")
        sys.exit(1)

    print()
    print(f"评论已获取完毕，共 {len(all_comments)} 条评论。")
    input("请按下回车开始抽奖...")

    # Step 4: Draw and display winners one by one
    winners = draw_lucky_users(all_comments, count=count)
    all_nicknames = list({u.nickname for u in all_comments})

    print()
    print("=" * 50)
    for i, winner in enumerate(winners, 1):
        print(f"\n--- 第 {i} 位幸运用户 ---")
        time.sleep(0.3)
        scroll_animation(all_nicknames, winner.nickname)
        print(f"    评论: {winner.comment_text}")
        print(f"    主页: {winner.homepage_url}")
        time.sleep(0.5)

    print()
    print("=" * 50)
    print(f"  抽奖完成！共抽取 {len(winners)} 位幸运用户")
    print("=" * 50)
    print()
    input("按回车退出...")


if __name__ == "__main__":
    main()
