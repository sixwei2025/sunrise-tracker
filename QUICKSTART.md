# 快速开始指南

## 5分钟快速上手

### 1. 安装依赖

```bash
npm install
```

### 2. 立即运行测试

```bash
npm run dev -- --once
```

第一次运行不会检测到爆文（需要建立历史数据基线），再运行一次：

```bash
npm run dev -- --once
```

你会看到类似这样的输出：

```
📊 小红书AI爆文日报 - 2026/1/28
==============================================

📈 数据概览：
   扫描文章：268 篇
   发现爆文：4 篇
   热门话题：ChatGPT使用技巧, Midjourney提示词

🔥 Top 4 爆文：

1. 【ChatGPT使用技巧】免费分享！ChatGPT使用技巧，效果惊人！
   作者：AI创作者15 | 阅读：39,471
   平均阅读：3330 | 爆文倍数：11.9x
   💡 爆点分析：标题强调免费分享；标题有强烈情感词汇；热门话题领域
   🔗 链接：https://www.xiaohongshu.com/explore/152
```

### 3. 配置通知（可选）

#### 企业微信/飞书/钉钉通知

1. 在群聊中添加机器人，获取Webhook URL
2. 创建 `.env` 文件：

```bash
cp .env.example .env
```

3. 编辑 `.env` 文件：

```env
NOTIFICATION_TYPE=webhook
WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key
```

4. 测试通知：

```bash
npm run dev -- --once
```

### 4. 配置AI分析（可选）

如果你有OpenAI或Claude的API密钥，可以启用AI爆点分析：

```env
AI_PROVIDER=openai
AI_API_KEY=sk-你的密钥
AI_MODEL=gpt-4
```

### 5. 启动定时任务

**方式1: 直接运行（前台）**

```bash
npm run build
npm start
```

**方式2: 使用PM2（后台）**

```bash
# 安装PM2
npm install -g pm2

# 启动
pm2 start dist/index.js --name xhs-viral-detector

# 查看日志
pm2 logs xhs-viral-detector

# 停止
pm2 stop xhs-viral-detector
```

## 常用命令

```bash
# 立即执行一次检测
npm run dev -- --once

# 启动定时任务（前台）
npm run dev

# 编译TypeScript
npm run build

# 运行编译后的代码
npm start
```

## 配置参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| NOTIFICATION_TYPE | 通知方式：console, webhook, email | console |
| WEBHOOK_URL | Webhook地址 | - |
| AI_PROVIDER | AI提供商：openai, anthropic, none | none |
| AI_API_KEY | AI API密钥 | - |
| MIN_VIRAL_MULTIPLIER | 爆文倍数阈值 | 10 |
| MIN_VIEWS_THRESHOLD | 最低阅读量 | 1000 |
| TOP_N_POSTS | 每天推送条数 | 10 |
| CRON_SCHEDULE | 定时任务时间 | 0 7 * * * (每天7点) |

## 调整检测灵敏度

如果检测到的爆文太少，可以降低阈值：

```env
MIN_VIRAL_MULTIPLIER=5   # 降低到5倍
MIN_VIEWS_THRESHOLD=500  # 降低到500阅读
```

如果检测到的爆文太多，可以提高阈值：

```env
MIN_VIRAL_MULTIPLIER=20   # 提高到20倍
MIN_VIEWS_THRESHOLD=5000  # 提高到5000阅读
```

## 接入真实数据

当前使用模拟数据。要接入真实的小红书数据，请参考 `README.md` 的"接入真实数据"章节。

## 问题排查

**问题1: 检测不到爆文**
- 第一次运行不会检测到爆文，需要运行2-3次建立历史数据
- 降低 `MIN_VIRAL_MULTIPLIER` 阈值

**问题2: Webhook通知没收到**
- 检查 `WEBHOOK_URL` 是否正确
- 查看控制台是否有错误信息
- 确认机器人已添加到群聊

**问题3: 定时任务没有执行**
- 检查 `CRON_SCHEDULE` 配置是否正确
- 确认程序正在运行（`pm2 list`）
- 查看日志（`pm2 logs`）

## 下一步

✅ 已完成基础配置
⏰ 启动定时任务
🔔 配置通知方式
🤖 启用AI分析（可选）
📊 接入真实数据源（可选）

祝你使用愉快！🎉
