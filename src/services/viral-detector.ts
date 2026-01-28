import { XHSPost, ViralPost, Config } from '../types';
import { Storage } from '../utils/storage';

export class ViralDetector {
  private storage: Storage;
  private config: Config;

  constructor(storage: Storage, config: Config) {
    this.storage = storage;
    this.config = config;
  }

  /**
   * 检测爆文
   */
  detectViralPosts(posts: XHSPost[]): ViralPost[] {
    const viralPosts: ViralPost[] = [];

    // 先更新作者统计数据
    this.storage.updateAuthorStats(posts);

    for (const post of posts) {
      const authorStats = this.storage.getAuthorStats(post.authorId);

      if (!authorStats) {
        // 如果没有历史数据，跳过这个作者的第一批帖子
        continue;
      }

      // 计算爆文倍数
      const viralMultiplier = post.views / authorStats.averageViews;

      // 判断是否为爆文
      const isViral =
        viralMultiplier >= this.config.minViralMultiplier &&
        post.views >= this.config.minViewsThreshold;

      if (isViral) {
        viralPosts.push({
          ...post,
          authorAverageViews: authorStats.averageViews,
          viralMultiplier,
        });
      }
    }

    // 按爆文倍数排序
    viralPosts.sort((a, b) => b.viralMultiplier - a.viralMultiplier);

    return viralPosts.slice(0, this.config.topNPosts);
  }

  /**
   * 分析爆文特征
   */
  analyzeViralPatterns(viralPosts: ViralPost[]): {
    topTopics: string[];
    avgViralMultiplier: number;
    topAuthors: string[];
  } {
    if (viralPosts.length === 0) {
      return {
        topTopics: [],
        avgViralMultiplier: 0,
        topAuthors: [],
      };
    }

    // 统计话题
    const topicCount = new Map<string, number>();
    for (const post of viralPosts) {
      topicCount.set(post.topic, (topicCount.get(post.topic) || 0) + 1);
    }

    const topTopics = Array.from(topicCount.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([topic]) => topic);

    // 计算平均爆文倍数
    const avgViralMultiplier =
      viralPosts.reduce((sum, post) => sum + post.viralMultiplier, 0) /
      viralPosts.length;

    // 统计爆文作者
    const authorCount = new Map<string, number>();
    for (const post of viralPosts) {
      authorCount.set(
        post.authorName,
        (authorCount.get(post.authorName) || 0) + 1
      );
    }

    const topAuthors = Array.from(authorCount.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([author]) => author);

    return {
      topTopics,
      avgViralMultiplier,
      topAuthors,
    };
  }
}
