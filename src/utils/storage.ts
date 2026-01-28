import fs from 'fs';
import path from 'path';
import { AuthorStats, XHSPost } from '../types';

const DATA_DIR = path.join(__dirname, '../../data');
const AUTHOR_STATS_FILE = path.join(DATA_DIR, 'author_stats.json');
const POSTS_HISTORY_FILE = path.join(DATA_DIR, 'posts_history.json');

export class Storage {
  private authorStats: Map<string, AuthorStats> = new Map();
  private postsHistory: XHSPost[] = [];

  constructor() {
    this.loadData();
  }

  private loadData() {
    try {
      if (fs.existsSync(AUTHOR_STATS_FILE)) {
        const data = JSON.parse(fs.readFileSync(AUTHOR_STATS_FILE, 'utf-8'));
        this.authorStats = new Map(
          data.map((stat: AuthorStats) => [stat.authorId, stat])
        );
      }

      if (fs.existsSync(POSTS_HISTORY_FILE)) {
        this.postsHistory = JSON.parse(
          fs.readFileSync(POSTS_HISTORY_FILE, 'utf-8')
        );
      }
    } catch (error) {
      console.error('加载数据失败:', error);
    }
  }

  private saveData() {
    try {
      if (!fs.existsSync(DATA_DIR)) {
        fs.mkdirSync(DATA_DIR, { recursive: true });
      }

      fs.writeFileSync(
        AUTHOR_STATS_FILE,
        JSON.stringify(Array.from(this.authorStats.values()), null, 2)
      );

      fs.writeFileSync(
        POSTS_HISTORY_FILE,
        JSON.stringify(this.postsHistory, null, 2)
      );
    } catch (error) {
      console.error('保存数据失败:', error);
    }
  }

  getAuthorStats(authorId: string): AuthorStats | undefined {
    return this.authorStats.get(authorId);
  }

  updateAuthorStats(posts: XHSPost[]) {
    const authorPosts = new Map<string, XHSPost[]>();

    // 合并历史数据和新数据
    const allPosts = [...this.postsHistory, ...posts];

    // 按作者分组
    for (const post of allPosts) {
      if (!authorPosts.has(post.authorId)) {
        authorPosts.set(post.authorId, []);
      }
      authorPosts.get(post.authorId)!.push(post);
    }

    // 计算每个作者的平均阅读量
    for (const [authorId, posts] of authorPosts.entries()) {
      const totalViews = posts.reduce((sum, post) => sum + post.views, 0);
      const averageViews = totalViews / posts.length;

      this.authorStats.set(authorId, {
        authorId,
        authorName: posts[0].authorName,
        averageViews,
        totalPosts: posts.length,
        lastUpdated: new Date(),
      });
    }

    // 更新历史记录（保留最近30天的数据）
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    this.postsHistory = allPosts.filter(
      (post) => new Date(post.publishTime) > thirtyDaysAgo
    );

    this.saveData();
  }

  getAllAuthorStats(): AuthorStats[] {
    return Array.from(this.authorStats.values());
  }
}
