import { loadConfig } from './utils/config';
import { Storage } from './utils/storage';
import { createXHSFetcher } from './services/xhs-fetcher';
import { ViralDetector } from './services/viral-detector';
import { createAIAnalyzer } from './services/ai-analyzer';
import { createNotifier } from './services/notifier';
import { DailyReport } from './types';

export class ViralDetectorApp {
  private config = loadConfig();
  private storage = new Storage();
  private fetcher = createXHSFetcher(this.config.xhsCookie, true); // true表示使用模拟数据
  private detector = new ViralDetector(this.storage, this.config);
  private analyzer = createAIAnalyzer(this.config);
  private notifier = createNotifier(this.config);

  /**
   * 运行每日检测任务
   */
  async runDailyCheck(): Promise<void> {
    console.log('🚀 开始执行每日爆文检测...\n');

    try {
      // 1. 抓取昨日的AI相关帖子
      console.log('📥 正在抓取小红书AI相关内容...');
      const posts = await this.fetcher.fetchAIPosts(1);
      console.log(`   ✓ 共抓取 ${posts.length} 篇文章\n`);

      // 2. 检测爆文
      console.log('🔍 正在分析爆文...');
      const viralPosts = this.detector.detectViralPosts(posts);
      console.log(`   ✓ 发现 ${viralPosts.length} 篇爆文\n`);

      if (viralPosts.length === 0) {
        console.log('ℹ️  今日无符合条件的爆文\n');
        return;
      }

      // 3. AI分析爆点
      console.log('🤖 正在进行AI爆点分析...');
      for (const post of viralPosts) {
        post.viralAnalysis = await this.analyzer.analyzeViralReason(post);
      }
      console.log(`   ✓ 分析完成\n`);

      // 4. 生成报告
      const patterns = this.detector.analyzeViralPatterns(viralPosts);
      const report: DailyReport = {
        date: new Date().toLocaleDateString('zh-CN'),
        posts: viralPosts,
        summary: {
          totalScanned: posts.length,
          viralFound: viralPosts.length,
          topTopics: patterns.topTopics,
        },
      };

      // 5. 发送通知
      console.log('📤 正在发送通知...');
      await this.notifier.send(report);
      console.log('   ✓ 通知发送完成\n');

      console.log('✅ 每日检测任务完成！');
    } catch (error) {
      console.error('❌ 执行失败:', error);
      throw error;
    }
  }

  /**
   * 获取配置信息
   */
  getConfig() {
    return this.config;
  }
}
