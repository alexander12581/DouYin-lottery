# 抖音评论区幸运用户抽取工具 - 设计文档

## 概述

一个 Python CLI 工具，通过 Playwright 自动化浏览器拦截抖音评论 API 的签名参数，然后批量获取视频评论用户，随机抽取幸运用户。

## 架构

```
用户输入视频URL
      │
      ▼
┌─────────────────┐
│  Playwright      │
│  打开浏览器       │
│  等待用户登录     │
│  拦截comment/list │
│  提取签名参数     │
└────────┬────────┘
         │ headers, cookies, a_bogus, msToken
         ▼
┌─────────────────┐
│  httpx API调用   │
│  翻页获取所有评论 │
│  提取用户信息     │
└────────┬────────┘
         │ List[UserInfo]
         ▼
┌─────────────────┐
│  随机抽取        │
│  去重            │
│  输出结果        │
└─────────────────┘
```

## 模块设计

### 1. browser.py - 浏览器控制

**职责：** 打开浏览器，拦截请求，提取签名参数

**核心流程：**
1. 启动 Playwright Chromium（非 headless，用户需要看到浏览器）
2. 导航到抖音视频页面
3. 检测登录状态（判断是否出现登录弹窗）
4. 等待用户手动登录（如果需要）
5. 监听网络请求，拦截 `comment/list` 响应
6. 从拦截到的请求中提取完整的 headers 和 cookies
7. 返回 `RequestContext` 对象

**关键实现：**
- 使用 `page.on("request", handler)` 拦截请求
- 提取 `a_bogus`, `msToken`, `cookie`, 所有自定义 headers
- 设置超时机制，避免无限等待

### 2. api.py - API 调用

**职责：** 使用提取的签名参数批量获取评论

**核心流程：**
1. 使用 `RequestContext` 构建请求 headers
2. 调用 `GET /aweme/v1/web/comment/list/` 获取第一页
3. 解析响应，提取评论列表和 `cursor`
4. 用更新后的 `cursor` 继续翻页
5. 签名过期时通知 browser 重新获取
6. 返回所有评论用户列表

**关键参数：**
- `aweme_id`: 视频ID（从URL提取）
- `cursor`: 分页游标
- `count`: 每页数量（建议20）

**错误处理：**
- 签名过期（HTTP 403/状态码异常）→ 自动刷新签名
- 请求频率限制 → 自动加延迟
- 网络异常 → 重试机制

### 3. lottery.py - 抽奖逻辑

**职责：** 从用户列表中随机抽取幸运用户

**功能：**
- 用户去重（同一用户ID只保留一条）
- 随机抽取 N 个用户
- 结果格式化输出（用户名、评论内容、用户主页链接）

### 4. main.py - 主入口

**职责：** CLI 参数解析，流程编排

**命令行接口：**
```
python main.py <视频URL> --count <抽取人数>
```

**示例：**
```
python main.py "https://www.douyin.com/video/7640797086758263921" --count 5
```

**URL 解析：**
- 从 URL 路径中提取 `aweme_id`（如 `/video/7640797086758263921`）
- 支持格式：`https://www.douyin.com/video/<id>`、`https://www.douyin.com/jingxuan?modal_id=<id>`

## 数据结构

```python
@dataclass
class CommentUser:
    user_id: str          # 用户ID
    nickname: str         # 昵称
    avatar_url: str       # 头像URL
    comment_text: str     # 评论内容
    comment_time: int     # 评论时间戳
    homepage_url: str      # 用户主页链接

@dataclass
class RequestContext:
    headers: dict         # 完整请求头
    cookies: dict         # Cookie
    aweme_id: str         # 视频ID
```

## 依赖

- `playwright` - 浏览器自动化
- `httpx` - HTTP 客户端（支持 HTTP/2）
- `random` - 随机抽取（标准库）

## 使用流程

1. 运行命令：`python main.py <视频URL> --count 5`
2. 工具自动打开 Chromium 浏览器
3. 如果未登录，浏览器会显示抖音登录页面
4. 用户扫码/手动登录
5. 登录后工具自动拦截评论请求，提取签名
6. 自动翻页获取所有评论
7. 随机抽取并输出结果
8. 关闭浏览器

## 限制与注意事项

- **Cookie 有效期：** 登录态会过期，长时间运行可能需要重新登录
- **频率限制：** 请求过快可能被限流，工具会自动加延迟
- **评论数量上限：** 抖音API可能限制最大返回数量，超过上限时会提前停止
- **仅支持公开视频：** 私密视频无法获取评论
