"""
AI内容分析模块
使用Claude API分析爆文的选题和爆点
"""
from typing import Dict, List, Optional
import os
from anthropic import Anthropic


class AIContentAnalyzer:
    """AI内容分析器"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化分析器
        Args:
            api_key: Anthropic API Key
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("未设置 ANTHROPIC_API_KEY")

        self.client = Anthropic(api_key=self.api_key)

    def analyze_viral_note(self, note: Dict) -> Dict:
        """
        分析单篇爆文
        Args:
            note: 笔记数据
        Returns:
            分析结果
        """
        title = note.get('title', '')
        description = note.get('description', '')
        views = note.get('views', 0)
        likes = note.get('liked_count', 0)
        viral_analysis = note.get('viral_analysis', {})

        prompt = f"""请分析这篇小红书爆文，它是一个低粉账号的异常爆款内容：

标题：{title}
内容简介：{description}
数据表现：
- 阅读量：{views:,}
- 点赞数：{likes:,}
- 账号平均阅读量：{viral_analysis.get('user_avg_views', 0):,}
- 提升倍数：{viral_analysis.get('improvement_ratio', 0)}x

请从以下角度分析：
1. **选题分类**：这篇内容属于什么类型的选题？（如：工具推荐、赚钱案例、教程分享、经验总结等）
2. **爆点分析**：为什么这篇内容能成为爆款？列出3-5个核心爆点
3. **用户痛点**：解决了用户什么痛点或需求？
4. **可复制性**：这个选题和内容形式的可复制性如何？（高/中/低）

请用简洁的中文回答，每个部分2-3句话即可。"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            analysis_text = message.content[0].text

            # 解析分析结果
            return self._parse_analysis(analysis_text, note)

        except Exception as e:
            print(f"❌ AI分析失败: {e}")
            return self._get_fallback_analysis(note)

    def analyze_batch(self, notes: List[Dict]) -> List[Dict]:
        """
        批量分析爆文
        Args:
            notes: 笔记列表
        Returns:
            带分析结果的笔记列表
        """
        analyzed_notes = []

        for i, note in enumerate(notes, 1):
            print(f"🤖 分析第 {i}/{len(notes)} 篇...")
            try:
                analysis = self.analyze_viral_note(note)
                note['ai_analysis'] = analysis
                analyzed_notes.append(note)
            except Exception as e:
                print(f"⚠️  分析失败: {e}")
                note['ai_analysis'] = self._get_fallback_analysis(note)
                analyzed_notes.append(note)

        return analyzed_notes

    def generate_summary(self, notes: List[Dict]) -> str:
        """
        生成爆文总结报告
        Args:
            notes: 已分析的笔记列表
        Returns:
            总结报告
        """
        if not notes:
            return "暂无爆文数据"

        # 准备数据
        notes_summary = []
        for i, note in enumerate(notes[:10], 1):
            ai_analysis = note.get('ai_analysis', {})
            viral_analysis = note.get('viral_analysis', {})

            notes_summary.append(f"""
{i}. {note.get('title', '无标题')}
   📊 数据：{note.get('views', 0):,}阅读 | {note.get('liked_count', 0):,}赞 | {viral_analysis.get('improvement_ratio', 0)}x提升
   👤 账号：{note.get('user_name', '未知')}（平均阅读：{viral_analysis.get('user_avg_views', 0):,}）
   🏷️ 选题：{ai_analysis.get('topic_category', '未知')}
   💡 爆点：{ai_analysis.get('key_points', '未分析')}
""")

        prompt = f"""基于以下10篇AI领域的小红书爆文数据，请生成一份精简的趋势分析报告：

{chr(10).join(notes_summary)}

请从以下角度总结：
1. **热门选题趋势**：当前最受欢迎的AI内容方向是什么？
2. **共同爆点特征**：这些爆文有哪些共同的成功特征？
3. **内容建议**：给创作者的3条实用建议

回答要简洁有力，每部分3-5句话。"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            print(f"❌ 生成总结失败: {e}")
            return "生成总结时出错，请检查API配置"

    def _parse_analysis(self, analysis_text: str, note: Dict) -> Dict:
        """解析AI分析结果"""
        # 简单的解析逻辑
        lines = analysis_text.strip().split('\n')

        result = {
            'full_analysis': analysis_text,
            'topic_category': '未分类',
            'key_points': '',
            'user_pain_points': '',
            'replicability': '中',
        }

        # 提取关键信息（简化版）
        for line in lines:
            line = line.strip()
            if '选题' in line or '类型' in line:
                result['topic_category'] = line.split('：')[-1].strip()[:50]
            elif '爆点' in line and '：' in line:
                result['key_points'] = line.split('：', 1)[-1].strip()[:200]
            elif '痛点' in line and '：' in line:
                result['user_pain_points'] = line.split('：', 1)[-1].strip()[:200]
            elif '可复制' in line:
                if '高' in line:
                    result['replicability'] = '高'
                elif '低' in line:
                    result['replicability'] = '低'

        return result

    def _get_fallback_analysis(self, note: Dict) -> Dict:
        """获取降级分析（当AI分析失败时）"""
        title = note.get('title', '')

        # 基于标题关键词的简单分类
        topic = '其他'
        if any(kw in title for kw in ['工具', '软件', 'AI', 'ChatGPT']):
            topic = '工具推荐'
        elif any(kw in title for kw in ['赚钱', '收入', '副业', '变现']):
            topic = '赚钱案例'
        elif any(kw in title for kw in ['教程', '指南', '教学', '学习']):
            topic = '教程分享'
        elif any(kw in title for kw in ['经验', '心得', '分享', '总结']):
            topic = '经验总结'

        return {
            'full_analysis': '（AI分析失败，使用简单分类）',
            'topic_category': topic,
            'key_points': '数据异常突出，选题吸引眼球',
            'user_pain_points': '解决了用户的实际需求',
            'replicability': '中',
        }
