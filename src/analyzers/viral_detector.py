"""
爆文检测模块
识别低粉账号的爆文内容
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from tinydb import TinyDB, Query
import statistics


class ViralDetector:
    """爆文检测器"""

    def __init__(
        self,
        db_path: str = './data/viral_posts.json',
        min_viral_views: int = 3000,
        max_avg_views: int = 500,
        viral_multiplier: float = 5.0
    ):
        """
        初始化检测器
        Args:
            db_path: 数据库路径
            min_viral_views: 判定为爆文的最低阅读量
            max_avg_views: 判定为小账号的平均阅读量上限
            viral_multiplier: 爆文倍数（当前阅读量/平均阅读量）
        """
        self.db = TinyDB(db_path)
        self.notes_table = self.db.table('notes')
        self.users_table = self.db.table('users')

        self.min_viral_views = min_viral_views
        self.max_avg_views = max_avg_views
        self.viral_multiplier = viral_multiplier

    def detect_viral_notes(self, notes: List[Dict]) -> List[Dict]:
        """
        检测爆文
        Args:
            notes: 笔记列表
        Returns:
            爆文列表（包含爆文分析）
        """
        viral_notes = []

        for note in notes:
            # 保存笔记到数据库
            self._save_note(note)

            # 获取用户历史数据
            user_stats = self._get_user_stats(note['user_id'])

            # 判断是否为爆文
            if self._is_viral(note, user_stats):
                # 添加分析数据
                note['viral_analysis'] = {
                    'user_avg_views': user_stats.get('avg_views', 0),
                    'viral_score': self._calculate_viral_score(note, user_stats),
                    'improvement_ratio': self._calculate_improvement_ratio(note, user_stats),
                    'is_low_follower': user_stats.get('avg_views', 0) < self.max_avg_views,
                }
                viral_notes.append(note)

        # 按爆文分数排序
        viral_notes.sort(key=lambda x: x['viral_analysis']['viral_score'], reverse=True)

        return viral_notes

    def _is_viral(self, note: Dict, user_stats: Dict) -> bool:
        """
        判断是否为爆文
        Args:
            note: 笔记数据
            user_stats: 用户统计数据
        Returns:
            是否为爆文
        """
        views = note.get('views', 0)
        avg_views = user_stats.get('avg_views', 0)

        # 条件1: 阅读量超过最低阈值
        if views < self.min_viral_views:
            return False

        # 条件2: 用户平均阅读量较低（小账号）
        if avg_views > self.max_avg_views:
            return False

        # 条件3: 当前阅读量是平均值的N倍以上
        if avg_views > 0:
            ratio = views / avg_views
            if ratio < self.viral_multiplier:
                return False
        else:
            # 新账号，第一篇爆文
            if views < self.min_viral_views * 2:
                return False

        return True

    def _get_user_stats(self, user_id: str) -> Dict:
        """
        获取用户统计数据
        Args:
            user_id: 用户ID
        Returns:
            用户统计数据
        """
        # 从数据库查询用户历史笔记
        NoteQuery = Query()
        user_notes = self.notes_table.search(NoteQuery.user_id == user_id)

        if not user_notes:
            return {
                'note_count': 0,
                'avg_views': 0,
                'median_views': 0,
                'max_views': 0,
            }

        views_list = [note.get('views', 0) for note in user_notes]

        stats = {
            'note_count': len(user_notes),
            'avg_views': int(statistics.mean(views_list)) if views_list else 0,
            'median_views': int(statistics.median(views_list)) if views_list else 0,
            'max_views': max(views_list) if views_list else 0,
        }

        # 更新用户表
        UserQuery = Query()
        self.users_table.upsert({
            'user_id': user_id,
            'stats': stats,
            'updated_at': datetime.now().isoformat(),
        }, UserQuery.user_id == user_id)

        return stats

    def _calculate_viral_score(self, note: Dict, user_stats: Dict) -> float:
        """
        计算爆文分数
        综合考虑：阅读量、增长倍数、互动率
        """
        views = note.get('views', 0)
        likes = note.get('liked_count', 0)
        avg_views = user_stats.get('avg_views', 1)

        # 增长倍数
        growth_ratio = views / max(avg_views, 1)

        # 互动率
        engagement_rate = likes / max(views, 1) * 100

        # 综合分数 = 增长倍数 * 1000 + 互动率 * 100 + 阅读量权重
        score = (
            growth_ratio * 1000 +
            engagement_rate * 100 +
            (views / 10000) * 500
        )

        return round(score, 2)

    def _calculate_improvement_ratio(self, note: Dict, user_stats: Dict) -> float:
        """计算提升倍数"""
        views = note.get('views', 0)
        avg_views = user_stats.get('avg_views', 1)

        ratio = views / max(avg_views, 1)
        return round(ratio, 2)

    def _save_note(self, note: Dict):
        """保存笔记到数据库"""
        NoteQuery = Query()
        note_data = {
            **note,
            'saved_at': datetime.now().isoformat(),
        }

        # 避免重复保存
        existing = self.notes_table.search(NoteQuery.note_id == note['note_id'])
        if not existing:
            self.notes_table.insert(note_data)
        else:
            # 更新数据（阅读量等可能变化）
            self.notes_table.update(note_data, NoteQuery.note_id == note['note_id'])

    def get_top_viral_notes(
        self,
        days: int = 1,
        limit: int = 10
    ) -> List[Dict]:
        """
        获取最近N天的Top爆文
        Args:
            days: 最近N天
            limit: 返回数量
        Returns:
            爆文列表
        """
        NoteQuery = Query()
        cutoff_time = datetime.now() - timedelta(days=days)

        # 查询最近的笔记
        recent_notes = self.notes_table.search(
            NoteQuery.saved_at >= cutoff_time.isoformat()
        )

        # 按爆文分数排序
        viral_notes = [
            note for note in recent_notes
            if 'viral_analysis' in note
        ]

        viral_notes.sort(
            key=lambda x: x['viral_analysis']['viral_score'],
            reverse=True
        )

        return viral_notes[:limit]

    def clear_old_data(self, days: int = 30):
        """
        清理旧数据
        Args:
            days: 保留最近N天的数据
        """
        NoteQuery = Query()
        cutoff_time = datetime.now() - timedelta(days=days)

        removed = self.notes_table.remove(
            NoteQuery.saved_at < cutoff_time.isoformat()
        )

        print(f"🗑️  清理了 {len(removed)} 条旧数据")
