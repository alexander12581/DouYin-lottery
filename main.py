import logging
import os
import random
import subprocess
import sys
import time
import traceback
from pathlib import Path

# Fix browser path for PyInstaller exe - must be before playwright import
if getattr(sys, 'frozen', False):
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.join(
        os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
        'ms-playwright'
    )

import colorama
from playwright.sync_api import sync_playwright

from url_parser import extract_aweme_id
from browser import BrowserManager
from api import DouyinCommentClient
from lottery import draw_lucky_users

colorama.init()
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
RESET = colorama.Style.RESET_ALL

logging.basicConfig(level=logging.WARNING)


def pause():
    input("\n按回车退出...")


def check_chromium():
    """Check if Playwright Chromium is installed."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        return True
    except Exception as e:
        print(f"Chromium 检测失败: {e}")
        return False


def _find_driver():
    """Find Playwright node.exe and cli.js paths."""
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
        node = base / "playwright" / "driver" / "node.exe"
        cli = base / "playwright" / "driver" / "package" / "cli.js"
        if node.exists() and cli.exists():
            return str(node), str(cli)

    from playwright._impl._driver import compute_driver_executable
    node, cli = compute_driver_executable()
    return str(node), str(cli)


def install_chromium():
    """Download Playwright Chromium browser."""
    print("首次运行，需要下载 Chromium 浏览器（约100MB）...")
    print("正在下载，请稍候...")
    try:
        node_exe, cli_js = _find_driver()
        print(f"Driver: {node_exe}")
        result = subprocess.run(
            [node_exe, cli_js, "install", "chromium"],
            capture_output=False,
        )
        if result.returncode == 0:
            print("Chromium 下载完成！")
            return True
        else:
            print(f"下载失败 (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"下载失败: {e}")
        traceback.print_exc()
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
    try:
        print_banner()

        # Check Chromium
        if not check_chromium():
            print("\n正在自动安装 Chromium 浏览器...")
            if not install_chromium():
                print(f"\n{RED}错误: Chromium 安装失败，请手动执行: playwright install chromium{RESET}")
                pause()
                sys.exit(1)
            print()

        # Step 1: Get user input
        url = input("请输入抖音视频链接: ").strip()
        if not url:
            print("链接不能为空！")
            pause()
            sys.exit(1)

        try:
            extract_aweme_id(url)
        except ValueError:
            print("无法识别的抖音链接，请检查后重试。")
            pause()
            sys.exit(1)

        count_input = input("请输入抽取人数: ").strip()
        try:
            count = int(count_input)
            if count <= 0:
                raise ValueError
        except ValueError:
            print("请输入有效的正整数！")
            pause()
            sys.exit(1)

        # Step 2: Open browser and intercept signatures
        print()
        print("正在打开浏览器，请登录抖音...")
        browser = BrowserManager(url)
        try:
            ctx = browser.capture_request_context()
        except RuntimeError as e:
            print(f"错误: {e}")
            pause()
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
            pause()
            sys.exit(1)

        if not all_comments:
            print("没有找到任何评论。")
            pause()
            sys.exit(1)

        print()
        print(f"评论已获取完毕，共 {len(all_comments)} 条评论。")
        all_nicknames = list({u.nickname for u in all_comments})

        # Step 4: Draw loop — can re-draw without re-fetching comments
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print_banner()
            input("请按下回车开始抽奖...")

            winners = draw_lucky_users(all_comments, count=count)

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
            choice = input("按回车重新抽奖，输入 q 退出: ").strip().lower()
            if choice == 'q':
                break
            print()

        pause()

    except Exception as e:
        print(f"\n{RED}发生错误: {e}{RESET}")
        traceback.print_exc()
        pause()


if __name__ == "__main__":
    main()
