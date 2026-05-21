# DouYin-lottery

抖音评论区幸运用户抽取工具 —— 从抖音视频评论区中随机抽取幸运用户。

## 功能特点

- 自动拦截抖音评论区 API 请求，获取完整签名参数
- 自动分页获取全部评论数据
- 按用户去重，确保公平抽奖
- 抽奖时带有滚动动画效果，增强仪式感
- 首次运行自动下载 Chromium 浏览器
- 支持打包为独立可执行文件（exe）

## 环境要求

- Python 3.10+
- Chromium 浏览器（首次运行自动下载）

## 安装

```bash
# 克隆仓库
git clone https://github.com/alexander12581/DouYin-lottery.git
cd DouYin-lottery

# 创建虚拟环境
python -m venv env
env\Scripts\activate        # Windows
# source env/bin/activate   # macOS / Linux

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器（首次使用时程序也会自动下载）
playwright install chromium
```

## 使用方法

```bash
python main.py
```

按提示操作：

1. 输入抖音视频链接
2. 输入抽取人数
3. 在弹出的浏览器中登录抖音账号
4. 登录成功后工具自动获取评论
5. 按回车开始抽奖，查看滚动动画和中奖结果

## 打包为 exe

```bash
python build.py
```

生成的 `dist/douyin_lottery.exe` 可独立运行，无需 Python 环境。

## 项目结构

```
├── main.py          # 程序入口，交互流程控制
├── browser.py       # 浏览器管理，拦截评论 API 请求
├── api.py           # 抖音评论 API 客户端，分页获取评论
├── lottery.py       # 抽奖逻辑，去重 + 随机抽取
├── models.py        # 数据模型（CommentUser, RequestContext）
├── url_parser.py    # 抖音视频链接解析
├── build.py         # PyInstaller 打包脚本
├── requirements.txt # 依赖列表
└── tests/           # 单元测试
```

## 依赖说明

| 依赖 | 用途 |
|------|------|
| playwright | 浏览器自动化，拦截网络请求 |
| httpx | 发送 HTTP 请求获取评论 |
| colorama | 终端彩色输出 |
| pyinstaller | 打包为可执行文件 |
| pytest | 单元测试 |

## 开源许可

本项目基于 [MIT 许可证](LICENSE) 开源。

## 免责声明

本工具仅供学习和研究使用。使用本工具时请遵守抖音平台的服务条款和相关法律法规。用户需自行承担使用本工具所产生的一切风险和责任，作者不对因使用本工具而产生的任何损失负责。
