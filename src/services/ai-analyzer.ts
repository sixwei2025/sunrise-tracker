import axios from 'axios';
import { ViralPost, Config } from '../types';

export interface AIAnalyzer {
  analyzeViralReason(post: ViralPost): Promise<string>;
}

/**
 * OpenAI分析器
 */
export class OpenAIAnalyzer implements AIAnalyzer {
  private apiKey: string;
  private model: string;

  constructor(apiKey: string, model: string = 'gpt-4') {
    this.apiKey = apiKey;
    this.model = model;
  }

  async analyzeViralReason(post: ViralPost): Promise<string> {
    try {
      const prompt = `分析以下小红书帖子为什么会成为爆文：

标题：${post.title}
话题：${post.topic}
作者平均阅读量：${Math.round(post.authorAverageViews)}
本文阅读量：${post.views}
爆文倍数：${post.viralMultiplier.toFixed(1)}x

请从以下角度简要分析（50字以内）：
1. 标题吸引力（痛点、好奇心、利益点）
2. 话题热度
3. 可能的传播点

直接给出分析结论，不要啰嗦。`;

      const response = await axios.post(
        'https://api.openai.com/v1/chat/completions',
        {
          model: this.model,
          messages: [
            {
              role: 'system',
              content: '你是一个小红书内容分析专家，擅长分析爆文原因。',
            },
            {
              role: 'user',
              content: prompt,
            },
          ],
          max_tokens: 200,
          temperature: 0.7,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      return response.data.choices[0].message.content.trim();
    } catch (error) {
      console.error('AI分析失败:', error);
      return '分析失败';
    }
  }
}

/**
 * Claude分析器
 */
export class ClaudeAnalyzer implements AIAnalyzer {
  private apiKey: string;
  private model: string;

  constructor(apiKey: string, model: string = 'claude-3-5-sonnet-20241022') {
    this.apiKey = apiKey;
    this.model = model;
  }

  async analyzeViralReason(post: ViralPost): Promise<string> {
    try {
      const prompt = `分析以下小红书帖子为什么会成为爆文：

标题：${post.title}
话题：${post.topic}
作者平均阅读量：${Math.round(post.authorAverageViews)}
本文阅读量：${post.views}
爆文倍数：${post.viralMultiplier.toFixed(1)}x

请从以下角度简要分析（50字以内）：
1. 标题吸引力（痛点、好奇心、利益点）
2. 话题热度
3. 可能的传播点

直接给出分析结论，不要啰嗦。`;

      const response = await axios.post(
        'https://api.anthropic.com/v1/messages',
        {
          model: this.model,
          max_tokens: 200,
          messages: [
            {
              role: 'user',
              content: prompt,
            },
          ],
        },
        {
          headers: {
            'x-api-key': this.apiKey,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json',
          },
        }
      );

      return response.data.content[0].text.trim();
    } catch (error) {
      console.error('AI分析失败:', error);
      return '分析失败';
    }
  }
}

/**
 * 规则分析器（不使用AI）
 */
export class RuleBasedAnalyzer implements AIAnalyzer {
  async analyzeViralReason(post: ViralPost): Promise<string> {
    const reasons: string[] = [];

    // 分析标题
    const title = post.title;
    if (title.includes('免费') || title.includes('分享')) {
      reasons.push('标题强调免费分享');
    }
    if (title.includes('！') || title.includes('震惊') || title.includes('千万')) {
      reasons.push('标题有强烈情感词汇');
    }
    if (title.includes('教程') || title.includes('攻略') || title.includes('保姆级')) {
      reasons.push('实用教程型内容');
    }
    if (title.includes('推荐') || title.includes('必备') || title.includes('神器')) {
      reasons.push('工具推荐类');
    }

    // 分析爆文倍数
    if (post.viralMultiplier > 50) {
      reasons.push('超高流量倍数');
    } else if (post.viralMultiplier > 20) {
      reasons.push('高流量倍数');
    }

    // 分析话题
    const hotTopics = ['ChatGPT', 'AI绘画', 'Midjourney', '免费'];
    if (hotTopics.some((topic) => post.topic.includes(topic))) {
      reasons.push('热门话题领域');
    }

    return reasons.length > 0
      ? reasons.join('；')
      : '普通爆文，可能受平台推荐影响';
  }
}

/**
 * AI分析器工厂
 */
export function createAIAnalyzer(config: Config): AIAnalyzer {
  if (config.aiProvider === 'openai' && config.aiApiKey) {
    console.log('使用OpenAI进行爆点分析');
    return new OpenAIAnalyzer(config.aiApiKey, config.aiModel);
  } else if (config.aiProvider === 'anthropic' && config.aiApiKey) {
    console.log('使用Claude进行爆点分析');
    return new ClaudeAnalyzer(config.aiApiKey, config.aiModel);
  } else {
    console.log('使用规则引擎进行爆点分析');
    return new RuleBasedAnalyzer();
  }
}
