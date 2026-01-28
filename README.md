# 🔥 小红书AI爆文检测器

> 自动化检测小红书AI领域的低粉爆文，每天7点推送昨日Top 10

一个智能化的内容监测工具，专门用于发现小红书上AI相关的"异常值"内容——那些平时只有几十几百阅读，突然爆到几千几万的低粉账号爆文。

## ✨ 核心功能

- 🔍 **智能抓取**: 自动搜索小红书AI相关内容
- 📊 **异常检测**: 识别低粉账号的爆款内容（平均阅读<500，突然>3000）
- 🤖 **AI分析**: 使用Claude API分析爆点和选题
- ⏰ **定时推送**: 每天早上7点自动推送昨日Top 10
- 📧 **多种通知**: 支持邮件、企业微信、飞书、钉钉

## 📋 什么是低粉爆文？

低粉爆文是指：
- 账号平均阅读量 < 500（小账号）
- 单篇阅读量 > 3000（爆款）
- 提升倍数 > 5x（异常增长）

这类内容往往代表了：
- ✅ 精准的用户痛点
- ✅ 优质的选题方向
- ✅ 高性价比的内容策略

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- pip

### 2. 安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd sunrise-tracker

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
nano .env
```

必需配置：
- `ANTHROPIC_API_KEY`: Claude API密钥（用于AI分析）
- `EMAIL_FROM`: 发件邮箱
- `EMAIL_PASSWORD`: 邮箱密码或应用专用密码
- `EMAIL_TO`: 收件邮箱

可选配置（通知方式）：
- `WECHAT_WEBHOOK`: 企业微信webhook
- `FEISHU_WEBHOOK`: 飞书webhook
- `XHS_COOKIE`: 小红书Cookie（可选，提高抓取成功率）

### 4. 运行

#### 单次执行（测试）

```bash
cd src
python main.py
```

#### 定时执行（生产环境）

```bash
cd src
python scheduler.py
```

程序将在每天早上7点自动执行，并发送报告到你的邮箱。

## 📁 项目结构

```
sunrise-tracker/
├── src/
│   ├── scrapers/              # 爬虫模块
│   │   └── xiaohongshu_scraper.py
│   ├── analyzers/             # 分析模块
│   │   ├── viral_detector.py  # 爆文检测
│   │   └── ai_analyzer.py     # AI分析
│   ├── notifiers/             # 通知模块
│   │   ├── email_notifier.py  # 邮件通知
│   │   └── webhook_notifier.py # Webhook通知
│   ├── main.py                # 主程序
│   └── scheduler.py           # 定时调度
├── data/                      # 数据存储
│   └── viral_posts.json       # 爆文数据库
├── config/
│   └── config.yaml            # 配置文件
├── requirements.txt           # Python依赖
├── .env.example               # 环境变量模板
└── README.md
```

## ⚙️ 配置说明

### config/config.yaml

```yaml
# 搜索关键词（AI相关）
search_keywords:
  - "AI工具"
  - "ChatGPT"
  - "人工智能"
  # ... 更多关键词

# 爆文检测阈值
viral_detection:
  min_viral_views: 3000      # 最小阅读量
  max_avg_views: 500         # 账号平均阅读量上限
  viral_multiplier: 5        # 爆文倍数

# 定时任务
schedule:
  daily_time: "07:00"        # 每天执行时间
  timezone: "Asia/Shanghai"   # 时区

# 推送配置
notification:
  top_n: 10                  # 推送数量
  methods:                   # 通知方式
    - email
    - wechat
```

## 📊 报告示例

每天你会收到类似这样的报告：

```
🔥 小红书AI爆文日报 - 2024-01-28

📊 今日趋势总结
当前AI工具推荐类内容最受欢迎，特别是ChatGPT赚钱案例...

🏆 昨日Top 10 爆文

1. 🔥 用ChatGPT三天赚了5000块！保姆级教程
   📊 数据: 15,234阅读 | 1,523赞 | 12.5x提升
   👤 账号: AI爱好者小王（平均阅读: 1,218）
   🏷️ 选题: 赚钱案例
   💡 爆点: 具体收入数字 + 保姆级教程 + 低门槛复制
   🔗 查看原文

2. ...
```

## 🎯 使用场景

- 📝 **内容创作者**: 发现热门选题，学习爆款套路
- 📈 **运营人员**: 监测行业趋势，优化内容策略
- 🔬 **数据分析**: 研究内容传播规律
- 💡 **创业者**: 寻找市场机会，验证商业想法

## 🔧 高级功能

### 自定义搜索关键词

编辑 `config/config.yaml`，在 `search_keywords` 中添加你关注的关键词。

### 调整检测阈值

根据你的需求，调整 `viral_detection` 参数：
- 想看更多爆文？降低 `min_viral_views`
- 只看超小账号？降低 `max_avg_views`
- 只看超级爆款？提高 `viral_multiplier`

### 添加更多通知方式

在 `.env` 中配置webhook，在 `config.yaml` 中启用对应的通知方式。

## 🐛 常见问题

### Q: 提示"未设置 ANTHROPIC_API_KEY"？

A: 请在 `.env` 文件中配置你的Claude API密钥。可在 https://console.anthropic.com 获取。

### Q: 邮件发送失败？

A:
1. 检查邮箱配置是否正确
2. Gmail用户需要使用"应用专用密码"而非登录密码
3. 确保开启了SMTP服务

### Q: 能抓取真实的小红书数据吗？

A: 当前版本使用模拟数据（用于开发测试）。要抓取真实数据，需要：
1. 获取小红书Cookie（登录后从浏览器获取）
2. 研究小红书的API接口和反爬机制
3. 修改 `xiaohongshu_scraper.py` 中的实现

### Q: 如何部署到服务器？

A: 推荐使用 systemd 或 supervisor 管理进程：

```bash
# 使用 nohup 后台运行
nohup python scheduler.py > logs/output.log 2>&1 &

# 或使用 screen
screen -S viral-detector
python scheduler.py
# Ctrl+A, D 退出
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [Anthropic Claude](https://www.anthropic.com/) - AI分析
- [小红书](https://www.xiaohongshu.com/) - 数据来源
- [Rich](https://github.com/Textualize/rich) - 终端美化

---

Made with ❤️ by Claude Code

**⚠️ 免责声明**: 本工具仅供学习和研究使用，请遵守小红书的用户协议和Robots协议。
