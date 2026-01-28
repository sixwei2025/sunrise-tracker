export interface XHSPost {
  id: string;
  title: string;
  topic: string;
  authorName: string;
  authorId: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  publishTime: Date;
  url: string;
  coverImage?: string;
}

export interface AuthorStats {
  authorId: string;
  authorName: string;
  averageViews: number;
  totalPosts: number;
  lastUpdated: Date;
}

export interface ViralPost extends XHSPost {
  authorAverageViews: number;
  viralMultiplier: number; // 阅读量是平均值的多少倍
  viralAnalysis?: string; // AI分析的爆点原因
}

export interface DailyReport {
  date: string;
  posts: ViralPost[];
  summary: {
    totalScanned: number;
    viralFound: number;
    topTopics: string[];
  };
}

export interface Config {
  xhsCookie?: string;
  aiProvider?: 'openai' | 'anthropic' | 'none';
  aiApiKey?: string;
  aiModel?: string;
  notificationType: 'console' | 'email' | 'webhook';
  emailConfig?: {
    host: string;
    port: number;
    user: string;
    password: string;
    to: string;
  };
  webhookUrl?: string;
  cronSchedule: string;
  minViralMultiplier: number;
  minViewsThreshold: number;
  topNPosts: number;
}
