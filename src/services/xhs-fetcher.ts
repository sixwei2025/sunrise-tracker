import axios from 'axios';
import { XHSPost } from '../types';

export interface XHSFetcher {
  fetchAIPosts(days?: number): Promise<XHSPost[]>;
}

/**
 * 真实的小红书数据抓取器
 * 注意：小红书没有公开API，此实现需要根据实际情况调整
 * 可能需要：
 * 1. 使用浏览器自动化工具（Puppeteer/Playwright）
 * 2. 逆向小红书的私有API
 * 3. 使用第三方数据服务
 */
export class RealXHSFetcher implements XHSFetcher {
  private cookie: string;

  constructor(cookie?: string) {
    this.cookie = cookie || '';
  }

  async fetchAIPosts(days: number = 1): Promise<XHSPost[]> {
    // 这里是一个示例实现框架
    // 实际使用时需要根据小红书的API或网页结构来实现

    try {
      // 示例：使用小红书的搜索API
      // 注意：这只是示例代码，实际的API端点和参数可能不同
      const response = await axios.get('https://www.xiaohongshu.com/api/sns/web/v1/search/notes', {
        params: {
          keyword: 'AI 人工智能',
          page: 1,
          page_size: 50,
        },
        headers: {
          'Cookie': this.cookie,
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
      });

      // 解析响应并转换为XHSPost格式
      // 这部分需要根据实际的响应结构来实现
      return [];
    } catch (error) {
      console.error('抓取小红书数据失败:', error);
      throw error;
    }
  }
}

/**
 * 模拟数据抓取器（用于测试和演示）
 */
export class MockXHSFetcher implements XHSFetcher {
  async fetchAIPosts(days: number = 1): Promise<XHSPost[]> {
    // 生成模拟数据
    const topics = [
      'AI绘画教程',
      'ChatGPT使用技巧',
      'AI写作工具推荐',
      'Midjourney提示词',
      'AI视频生成',
      'AI配音工具',
      'AIGC商业应用',
      'Stable Diffusion教程',
    ];

    const posts: XHSPost[] = [];
    const now = new Date();

    // 生成50个模拟账号
    for (let i = 0; i < 50; i++) {
      const authorId = `author_${i}`;
      const authorName = `AI创作者${i}`;

      // 每个账号生成3-8个帖子
      const postCount = Math.floor(Math.random() * 6) + 3;

      for (let j = 0; j < postCount; j++) {
        const topic = topics[Math.floor(Math.random() * topics.length)];
        const isViral = Math.random() < 0.15; // 15%的概率是爆文

        // 正常阅读量：50-500
        // 爆文阅读量：5000-50000
        const baseViews = isViral
          ? Math.floor(Math.random() * 45000) + 5000
          : Math.floor(Math.random() * 450) + 50;

        const publishTime = new Date(now);
        publishTime.setHours(publishTime.getHours() - Math.floor(Math.random() * 24 * days));

        posts.push({
          id: `post_${i}_${j}`,
          title: this.generateTitle(topic, isViral),
          topic,
          authorName,
          authorId,
          views: baseViews,
          likes: Math.floor(baseViews * (Math.random() * 0.15 + 0.05)),
          comments: Math.floor(baseViews * (Math.random() * 0.08 + 0.02)),
          shares: Math.floor(baseViews * (Math.random() * 0.05 + 0.01)),
          publishTime,
          url: `https://www.xiaohongshu.com/explore/${i}${j}`,
        });
      }
    }

    return posts;
  }

  private generateTitle(topic: string, isViral: boolean): string {
    const viralPrefixes = [
      '震惊！',
      '实测有效！',
      '免费分享！',
      '保姆级教程！',
      '千万不要错过！',
      '强烈推荐！',
    ];

    const normalPrefixes = [
      '分享一下',
      '简单记录',
      '今天试了',
      '关于',
    ];

    const prefix = isViral
      ? viralPrefixes[Math.floor(Math.random() * viralPrefixes.length)]
      : normalPrefixes[Math.floor(Math.random() * normalPrefixes.length)];

    return `${prefix}${topic}，${isViral ? '效果惊人！' : '还不错'}`;
  }
}

// 工厂函数
export function createXHSFetcher(cookie?: string, useMock: boolean = true): XHSFetcher {
  if (useMock || !cookie) {
    console.log('使用模拟数据模式（开发测试）');
    return new MockXHSFetcher();
  }
  return new RealXHSFetcher(cookie);
}
