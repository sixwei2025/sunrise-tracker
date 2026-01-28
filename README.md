# 小红书AI爆文检测器

自动化检测小红书AI领域的低粉爆文（异常流量内容），每天定时推送分析报告。

## 功能特点

✨ **智能检测**：自动识别平时阅读量低，但突然爆火的内容（低粉爆文）

📊 **数据分析**：追踪账号历史数据，计算爆文倍数（阅读量/平均阅读量）

🤖 **AI爆点分析**：支持OpenAI、Claude等AI服务分析爆文原因

⏰ **定时推送**：每天早上7点自动推送昨日Top 10爆文

📤 **多种通知方式**：控制台、Webhook（企业微信/飞书/钉钉）、邮件

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

复制配置文件模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的参数：

```env
# 通知方式（必填）
NOTIFICATION_TYPE=console  # console, webhook, email

# Webhook通知（可选）
# WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx

# AI分析（可选，不配置则使用规则分析）
# AI_PROVIDER=openai
# AI_API_KEY=sk-xxxxx
# AI_MODEL=gpt-4

# 检测参数（可选，使用默认值）
# MIN_VIRAL_MULTIPLIER=10  # 爆文倍数阈值
# MIN_VIEWS_THRESHOLD=1000  # 最低阅读量
# TOP_N_POSTS=10  # 每天推送条数
```

### 3. 运行程序

**开发模式（立即执行一次）：**

```bash
npm run dev -- --now
```

**执行一次后退出：**

```bash
npm run dev -- --once
```

**后台运行（定时任务）：**

```bash
# 编译
npm run build

# 启动
npm start
```

**使用 PM2 持久化运行：**

```bash
npm install -g pm2
pm2 start dist/index.js --name xhs-viral-detector
pm2 save
pm2 startup
```

## 工作原理

### 1. 数据采集

- 每天抓取小红书AI相关内容（ChatGPT、AI绘画、Midjourney等话题）
- 记录每篇文章的：标题、话题、作者、阅读量、点赞数等

### 2. 爆文识别算法

```
爆文倍数 = 当前阅读量 / 作者平均阅读量

判定条件：
- 爆文倍数 >= 10倍（可配置）
- 阅读量 >= 1000（可配置）
```

**示例：**
- 作者A平时文章阅读量：50-200
- 某篇文章阅读量：8000
- 爆文倍数：8000 / 125 = 64倍 ✅ 符合条件

### 3. 爆点分析

使用AI或规则引擎分析爆文原因：
- 标题吸引力（痛点、好奇心、利益点）
- 话题热度
- 可能的传播点

### 4. 报告推送

每天早上7点推送包含：
- 选题
- 标题
- 账号名字
- 阅读量
- 爆点分析

## 报告示例

```
📊 小红书AI爆文日报 - 2024-01-28
==============================================

📈 数据概览：
   扫描文章：150 篇
   发现爆文：8 篇
   热门话题：AI绘画教程, ChatGPT使用技巧, Midjourney提示词

🔥 Top 8 爆文：

1. 【AI绘画教程】震惊！免费分享，效果惊人！
   作者：AI创作者23 | 阅读：15,234
   平均阅读：156 | 爆文倍数：97.7x
   💡 爆点分析：标题强调免费分享；标题有强烈情感词汇；实用教程型内容
   🔗 链接：https://www.xiaohongshu.com/explore/...

2. 【ChatGPT使用技巧】保姆级教程！千万不要错过！
   ...
```

## 配置说明

### 通知方式配置

**1. 控制台输出（默认）**

```env
NOTIFICATION_TYPE=console
```

**2. 企业微信/飞书/钉钉 Webhook**

```env
NOTIFICATION_TYPE=webhook
WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx
```

获取Webhook URL：
- 企业微信：群聊 → 群机器人 → 添加机器人 → 复制Webhook地址
- 飞书：群聊 → 设置 → 群机器人 → 添加机器人 → 复制Webhook地址
- 钉钉：群聊 → 群设置 → 智能群助手 → 添加机器人 → 复制Webhook地址

**3. 邮件通知**

```env
NOTIFICATION_TYPE=email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient@example.com
```

### AI分析配置

**使用OpenAI：**

```env
AI_PROVIDER=openai
AI_API_KEY=sk-xxxxx
AI_MODEL=gpt-4
```

**使用Claude：**

```env
AI_PROVIDER=anthropic
AI_API_KEY=sk-ant-xxxxx
AI_MODEL=claude-3-5-sonnet-20241022
```

**不使用AI（规则分析）：**

```env
AI_PROVIDER=none
```

### 定时任务配置

```env
# Cron表达式：分 时 日 月 周
CRON_SCHEDULE=0 7 * * *  # 每天7点

# 其他示例：
# 0 */6 * * *   # 每6小时
# 0 9,18 * * *  # 每天9点和18点
# 0 8 * * 1-5   # 工作日早上8点
```

## 接入真实数据

当前版本使用模拟数据进行演示。要接入真实的小红书数据，需要：

### 方案1：实现XHSFetcher接口

编辑 `src/services/xhs-fetcher.ts`：

```typescript
export class RealXHSFetcher implements XHSFetcher {
  async fetchAIPosts(days: number = 1): Promise<XHSPost[]> {
    // 实现你的数据抓取逻辑
    // 可以使用：
    // 1. Puppeteer/Playwright 浏览器自动化
    // 2. 小红书私有API（需要逆向）
    // 3. 第三方数据服务
  }
}
```

然后修改 `src/app.ts` 中的 `useMock` 参数为 `false`。

### 方案2：使用第三方数据服务

如果有第三方数据服务API，可以直接在 `RealXHSFetcher` 中调用。

### 方案3：手动导入数据

在 `data/` 目录下创建 `posts.json` 文件，然后修改fetcher读取本地文件。

## 项目结构

```
xiaohongshu-viral-detector/
├── src/
│   ├── types/          # TypeScript类型定义
│   ├── services/       # 核心服务
│   │   ├── xhs-fetcher.ts      # 数据抓取
│   │   ├── viral-detector.ts   # 爆文检测
│   │   ├── ai-analyzer.ts      # AI分析
│   │   └── notifier.ts         # 通知推送
│   ├── utils/          # 工具函数
│   │   ├── config.ts   # 配置加载
│   │   └── storage.ts  # 数据存储
│   ├── app.ts          # 应用主逻辑
│   └── index.ts        # 程序入口
├── data/               # 数据存储目录
├── .env.example        # 配置模板
├── package.json
└── README.md
```

## 常见问题

**Q: 为什么检测不到爆文？**

A: 可能原因：
1. 首次运行，还没有足够的历史数据来计算平均值
2. `MIN_VIRAL_MULTIPLIER` 阈值设置太高，尝试调低到5或更低
3. 抓取的数据量太少，增加数据源

**Q: 如何调整爆文标准？**

A: 修改 `.env` 文件中的参数：
```env
MIN_VIRAL_MULTIPLIER=5   # 降低爆文倍数阈值
MIN_VIEWS_THRESHOLD=500  # 降低最低阅读量
```

**Q: 可以监控其他领域吗？**

A: 可以。修改 `src/services/xhs-fetcher.ts` 中的搜索关键词即可。

**Q: 数据存储在哪里？**

A: 存储在 `data/` 目录下的JSON文件中，保留最近30天的数据。

## 免责声明

本工具仅供学习和研究使用。使用时请遵守小红书的服务条款和robots.txt规则。不要进行高频请求或其他可能对平台造成负担的行为。

## 开源协议

MIT License

## 贡献

欢迎提交Issue和Pull Request！
