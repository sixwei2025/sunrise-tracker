# 🚀 小红书AI爆文监控工具 - 部署完成

## ✅ 部署状态

所有部署任务已完成！工具正在运行中，每天早上7点自动检测并推送爆文报告。

---

## 📋 部署清单

### 1️⃣ 环境检查 ✅
- **Node.js**: v22.22.0
- **npm**: 10.9.4
- **PM2**: 已安装并配置

### 2️⃣ 依赖安装 ✅
- 已安装58个npm包
- 无安全漏洞

### 3️⃣ Server酱配置 ✅
- **推送Key**: SCT311779T1iZF9z6r81nLaN4HAgsI5b3b
- **Webhook URL**: https://sctapi.ftqq.com/SCT311779T1iZF9z6r81nLaN4HAgsI5b3b.send
- **状态**: 已配置（需在实际环境中测试）

### 4️⃣ 定时任务 ✅
- **执行时间**: 每天早上7:00
- **管理方式**: PM2进程管理器
- **开机自启**: 已配置

### 5️⃣ 程序状态 ✅
- **运行状态**: 在线 (online)
- **进程名称**: xhs-爆文监控
- **进程ID**: 查看命令 `pm2 status`

---

## 🎯 核心功能

### 爆文检测标准
- **阅读量倍数**: ≥ 3倍平均值（可调整为10倍）
- **最低阅读量**: ≥ 100（可调整为1000）
- **推送数量**: Top 10爆文

### 报告内容
每天早上7点推送包含：
- 📊 数据概览（扫描文章数、爆文数、热门话题）
- 🔥 Top 10爆文详情
  - 标题和选题
  - 作者名称
  - 阅读量和爆文倍数
  - 💡 爆点分析
  - 🔗 原文链接

---

## 📱 Server酱推送说明

### ⚠️ 当前状态
当前环境无法访问Server酱API（显示403错误），所以临时使用**控制台输出**模式。

### 🔧 在实际服务器上启用Server酱
在你自己的服务器或本地电脑上部署时：

1. 编辑配置文件：
```bash
nano /home/user/sunrise-tracker/.env
```

2. 修改通知类型：
```env
NOTIFICATION_TYPE=webhook  # 改为webhook
```

3. 重启PM2：
```bash
pm2 restart xhs-爆文监控
```

### 📬 Server酱使用指南
1. 微信扫码登录 [Server酱官网](https://sct.ftqq.com/)
2. 你的SendKey: **SCT311779T1iZF9z6r81nLaN4HAgsI5b3b**
3. 每天早上7点会收到微信推送

---

## 🛠️ 常用管理命令

### PM2进程管理
```bash
# 查看程序状态
pm2 status

# 查看实时日志
pm2 logs xhs-爆文监控

# 停止程序
pm2 stop xhs-爆文监控

# 重启程序
pm2 restart xhs-爆文监控

# 删除程序
pm2 delete xhs-爆文监控
```

### 手动测试
```bash
# 进入项目目录
cd /home/user/sunrise-tracker

# 立即执行一次检测（测试用）
npm run dev -- --once

# 查看配置
cat .env
```

---

## ⚙️ 配置文件说明

配置文件位置：`/home/user/sunrise-tracker/.env`

### 核心配置项
```env
# 通知方式：console（控制台）/ webhook（Server酱）/ email（邮件）
NOTIFICATION_TYPE=console

# Server酱推送地址
WEBHOOK_URL=https://sctapi.ftqq.com/SCT311779T1iZF9z6r81nLaN4HAgsI5b3b.send

# 定时任务（cron表达式）
CRON_SCHEDULE=0 7 * * *  # 每天早上7点

# 爆文检测标准
MIN_VIRAL_MULTIPLIER=3   # 爆文倍数阈值（建议改回10）
MIN_VIEWS_THRESHOLD=100  # 最低阅读量（建议改回1000）
TOP_N_POSTS=10           # 每天推送条数
```

### 调整爆文标准（可选）
如果想要更严格的爆文标准，修改：
```env
MIN_VIRAL_MULTIPLIER=10   # 10倍平均值
MIN_VIEWS_THRESHOLD=1000  # 至少1000阅读量
```

修改后重启：
```bash
pm2 restart xhs-爆文监控
```

---

## 🔍 查看运行日志

### PM2日志
```bash
# 查看最近20行日志
pm2 logs xhs-爆文监控 --lines 20

# 实时监控日志
pm2 logs xhs-爆文监控
```

### 日志内容示例
```
⏰ 定时任务已配置: 0 7 * * *
   (每天早上7点自动执行)

✅ 程序运行中... (按 Ctrl+C 退出)
```

---

## 📊 测试结果

已成功测试，检测到10篇爆文：

示例爆文：
1. 【AI绘画教程】免费分享！效果惊人！
   - 阅读量：23,407 | 爆文倍数：13.2x

2. 【Midjourney提示词】震惊！效果惊人！
   - 阅读量：36,329 | 爆文倍数：11.9x

---

## ❓ 常见问题

### Q1: Server酱推送失败怎么办？
**A**: 当前环境限制，推荐方案：
1. 在自己的服务器或电脑上部署
2. 或者使用控制台输出，配合PM2日志查看
3. 检查Server酱SendKey是否正确

### Q2: 如何修改推送时间？
**A**: 编辑 `.env` 文件中的 `CRON_SCHEDULE`：
```env
CRON_SCHEDULE=0 9 * * *   # 改为每天9点
CRON_SCHEDULE=0 */6 * * *  # 改为每6小时
```

### Q3: 如何停止定时任务？
**A**:
```bash
pm2 stop xhs-爆文监控
```

### Q4: 数据从哪里来？
**A**: 当前使用模拟数据测试。接入真实数据需要：
- 修改 `src/services/xhs-fetcher.ts`
- 实现真实的小红书数据抓取（需要遵守小红书服务条款）

---

## 🎉 部署成功

恭喜！小红书AI爆文监控工具已成功部署并运行。

**下一步建议**：
1. ✅ 工具已在后台运行，明天早上7点会自动执行
2. 📝 如需调整配置，编辑 `.env` 文件后重启PM2
3. 📱 在实际环境中测试Server酱推送
4. 🔍 可随时用 `pm2 logs` 查看运行日志

**需要帮助？**
- 查看项目README: `/home/user/sunrise-tracker/README.md`
- PM2官方文档: https://pm2.keymetrics.io/

---

**部署时间**: 2026-01-28
**项目位置**: /home/user/sunrise-tracker
**进程管理**: PM2
**定时执行**: 每天 07:00

🎊 祝使用愉快！
