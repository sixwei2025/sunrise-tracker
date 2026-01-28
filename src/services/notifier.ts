import axios from 'axios';
import { DailyReport, Config } from '../types';

export interface Notifier {
  send(report: DailyReport): Promise<void>;
}

/**
 * 控制台输出
 */
export class ConsoleNotifier implements Notifier {
  async send(report: DailyReport): Promise<void> {
    console.log('\n==============================================');
    console.log(`📊 小红书AI爆文日报 - ${report.date}`);
    console.log('==============================================\n');

    console.log(`📈 数据概览：`);
    console.log(`   扫描文章：${report.summary.totalScanned} 篇`);
    console.log(`   发现爆文：${report.summary.viralFound} 篇`);
    console.log(`   热门话题：${report.summary.topTopics.join(', ')}\n`);

    if (report.posts.length === 0) {
      console.log('❌ 今日暂无符合条件的爆文\n');
      return;
    }

    console.log(`🔥 Top ${report.posts.length} 爆文：\n`);

    report.posts.forEach((post, index) => {
      console.log(`${index + 1}. 【${post.topic}】${post.title}`);
      console.log(`   作者：${post.authorName} | 阅读：${post.views.toLocaleString()}`);
      console.log(`   平均阅读：${Math.round(post.authorAverageViews)} | 爆文倍数：${post.viralMultiplier.toFixed(1)}x`);
      if (post.viralAnalysis) {
        console.log(`   💡 爆点分析：${post.viralAnalysis}`);
      }
      console.log(`   🔗 链接：${post.url}\n`);
    });

    console.log('==============================================\n');
  }
}

/**
 * Webhook通知（企业微信、飞书、钉钉等）
 */
export class WebhookNotifier implements Notifier {
  private webhookUrl: string;

  constructor(webhookUrl: string) {
    this.webhookUrl = webhookUrl;
  }

  async send(report: DailyReport): Promise<void> {
    try {
      const content = this.formatMarkdown(report);

      let payload: any;

      // 判断是否为Server酱
      if (this.webhookUrl.includes('sctapi.ftqq.com')) {
        // Server酱格式
        payload = {
          title: `📊 小红书AI爆文日报 - ${report.date}`,
          desp: content,
        };
      } else {
        // 企业微信/飞书/钉钉格式
        payload = {
          msgtype: 'markdown',
          markdown: {
            content,
          },
        };
      }

      await axios.post(this.webhookUrl, payload);
      console.log('✅ Webhook通知发送成功');
    } catch (error) {
      console.error('❌ Webhook通知发送失败:', error);
      throw error;
    }
  }

  private formatMarkdown(report: DailyReport): string {
    let md = `# 📊 小红书AI爆文日报\n`;
    md += `> ${report.date}\n\n`;

    md += `## 数据概览\n`;
    md += `- 扫描文章：${report.summary.totalScanned} 篇\n`;
    md += `- 发现爆文：${report.summary.viralFound} 篇\n`;
    md += `- 热门话题：${report.summary.topTopics.join(', ')}\n\n`;

    if (report.posts.length === 0) {
      md += `> 今日暂无符合条件的爆文\n`;
      return md;
    }

    md += `## 🔥 Top ${report.posts.length} 爆文\n\n`;

    report.posts.forEach((post, index) => {
      md += `### ${index + 1}. ${post.title}\n`;
      md += `- **选题**：${post.topic}\n`;
      md += `- **账号**：${post.authorName}\n`;
      md += `- **阅读量**：${post.views.toLocaleString()} （平均：${Math.round(post.authorAverageViews)}）\n`;
      md += `- **爆文倍数**：${post.viralMultiplier.toFixed(1)}x\n`;
      if (post.viralAnalysis) {
        md += `- **爆点分析**：${post.viralAnalysis}\n`;
      }
      md += `- [查看原文](${post.url})\n\n`;
    });

    return md;
  }
}

/**
 * 邮件通知
 */
export class EmailNotifier implements Notifier {
  private config: Config['emailConfig'];

  constructor(config: Config['emailConfig']) {
    this.config = config;
  }

  async send(report: DailyReport): Promise<void> {
    // 这里需要使用nodemailer等库来发送邮件
    // 为了简化，这里只是示例代码
    console.log('📧 邮件通知功能需要配置SMTP服务');
    console.log(`   收件人：${this.config?.to}`);

    // 实际实现可以使用 nodemailer:
    // const nodemailer = require('nodemailer');
    // const transporter = nodemailer.createTransporter({...});
    // await transporter.sendMail({...});
  }
}

/**
 * 通知器工厂
 */
export function createNotifier(config: Config): Notifier {
  switch (config.notificationType) {
    case 'webhook':
      if (!config.webhookUrl) {
        console.warn('⚠️  未配置Webhook URL，使用控制台输出');
        return new ConsoleNotifier();
      }
      return new WebhookNotifier(config.webhookUrl);

    case 'email':
      if (!config.emailConfig) {
        console.warn('⚠️  未配置邮件信息，使用控制台输出');
        return new ConsoleNotifier();
      }
      return new EmailNotifier(config.emailConfig);

    case 'console':
    default:
      return new ConsoleNotifier();
  }
}
