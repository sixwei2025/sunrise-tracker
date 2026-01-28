"""
小红书内容爬虫模块
使用小红书搜索API获取笔记数据
"""
import time
import json
import random
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup


class XiaohongshuScraper:
    """小红书内容爬取器"""

    def __init__(self, cookie: Optional[str] = None):
        """
        初始化爬虫
        Args:
            cookie: 小红书cookie（可选，用于提高抓取成功率）
        """
        self.cookie = cookie
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.xiaohongshu.com/',
        })
        if cookie:
            self.session.headers['Cookie'] = cookie

    def search_notes(
        self,
        keyword: str,
        limit: int = 50,
        sort: str = 'time_descending'
    ) -> List[Dict]:
        """
        搜索笔记
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            sort: 排序方式 (time_descending: 最新, popularity_descending: 最热)
        Returns:
            笔记列表
        """
        notes = []
        print(f"🔍 搜索关键词: {keyword}")

        # 使用小红书Web搜索接口（无需登录）
        # 注意：这是一个模拟实现，实际使用时需要根据小红书当前的API结构调整
        search_url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"

        page = 1
        while len(notes) < limit:
            try:
                params = {
                    'keyword': keyword,
                    'page': page,
                    'page_size': 20,
                    'search_id': self._generate_search_id(),
                    'sort': sort,
                }

                # 添加随机延迟，避免被封
                time.sleep(random.uniform(1, 3))

                # 这里是简化版本，实际需要处理签名等反爬机制
                # 建议使用第三方库如 xhs 或自己抓包分析
                response = self.session.get(search_url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    items = data.get('data', {}).get('items', [])

                    for item in items:
                        note_info = self._parse_note_item(item)
                        if note_info:
                            notes.append(note_info)

                    if not items:
                        break

                    page += 1
                else:
                    print(f"⚠️  请求失败: {response.status_code}")
                    break

            except Exception as e:
                print(f"❌ 搜索出错: {e}")
                break

        return notes[:limit]

    def get_note_detail(self, note_id: str) -> Optional[Dict]:
        """
        获取笔记详情
        Args:
            note_id: 笔记ID
        Returns:
            笔记详情
        """
        try:
            url = f"https://www.xiaohongshu.com/explore/{note_id}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                # 从HTML中提取数据
                soup = BeautifulSoup(response.text, 'html.parser')

                # 查找包含笔记数据的script标签
                scripts = soup.find_all('script')
                for script in scripts:
                    if 'window.__INITIAL_STATE__' in script.text:
                        # 提取JSON数据
                        json_str = script.text.split('window.__INITIAL_STATE__=')[1].split('</script>')[0]
                        data = json.loads(json_str.strip())
                        return self._parse_note_detail(data, note_id)

        except Exception as e:
            print(f"❌ 获取笔记详情失败 {note_id}: {e}")

        return None

    def get_user_notes(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        获取用户的笔记列表
        Args:
            user_id: 用户ID
            limit: 获取数量
        Returns:
            笔记列表
        """
        notes = []
        try:
            url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 解析用户笔记数据
                # 具体实现需要根据页面结构调整
                pass

        except Exception as e:
            print(f"❌ 获取用户笔记失败 {user_id}: {e}")

        return notes[:limit]

    def _parse_note_item(self, item: Dict) -> Optional[Dict]:
        """解析笔记项目"""
        try:
            note_card = item.get('note_card', {})
            user = note_card.get('user', {})
            interact_info = note_card.get('interact_info', {})

            return {
                'note_id': note_card.get('note_id'),
                'title': note_card.get('display_title', ''),
                'description': note_card.get('desc', ''),
                'type': note_card.get('type'),  # normal: 图文, video: 视频
                'cover': note_card.get('cover', {}).get('url_default', ''),
                'user_id': user.get('user_id'),
                'user_name': user.get('nickname', ''),
                'user_avatar': user.get('avatar', ''),
                'liked_count': interact_info.get('liked_count', 0),
                'collected_count': interact_info.get('collected_count', 0),
                'comment_count': interact_info.get('comment_count', 0),
                'share_count': interact_info.get('share_count', 0),
                'views': self._estimate_views(interact_info),
                'create_time': note_card.get('time'),
                'url': f"https://www.xiaohongshu.com/explore/{note_card.get('note_id')}",
            }
        except Exception as e:
            print(f"⚠️  解析笔记失败: {e}")
            return None

    def _parse_note_detail(self, data: Dict, note_id: str) -> Optional[Dict]:
        """解析笔记详情"""
        # 根据实际数据结构解析
        # 这里需要根据小红书实际返回的数据结构来实现
        return None

    def _estimate_views(self, interact_info: Dict) -> int:
        """
        估算阅读量（小红书不直接显示阅读量）
        根据点赞、收藏、评论等互动数据估算
        经验公式：阅读量 ≈ (点赞数 + 收藏数 * 2 + 评论数 * 3) * 10
        """
        liked = interact_info.get('liked_count', 0)
        collected = interact_info.get('collected_count', 0)
        comment = interact_info.get('comment_count', 0)

        # 估算公式
        estimated_views = (liked + collected * 2 + comment * 3) * 10

        return max(estimated_views, liked * 10)  # 至少是点赞数的10倍

    def _generate_search_id(self) -> str:
        """生成搜索ID"""
        return f"{int(time.time() * 1000)}{random.randint(1000, 9999)}"


# 模拟数据生成器（用于测试，实际部署时删除）
class MockXiaohongshuScraper(XiaohongshuScraper):
    """模拟数据生成器（用于开发测试）"""

    def search_notes(self, keyword: str, limit: int = 50, sort: str = 'time_descending') -> List[Dict]:
        """生成模拟数据"""
        print(f"🔍 [模拟模式] 搜索关键词: {keyword}")

        notes = []
        for i in range(min(limit, 20)):
            # 模拟不同的阅读量分布
            is_viral = random.random() < 0.15  # 15%的概率是爆文

            if is_viral:
                views = random.randint(5000, 50000)
                likes = int(views * random.uniform(0.05, 0.15))
            else:
                views = random.randint(50, 800)
                likes = int(views * random.uniform(0.02, 0.08))

            note = {
                'note_id': f'mock_{int(time.time())}_{i}',
                'title': self._generate_mock_title(keyword, is_viral),
                'description': f'这是一篇关于{keyword}的笔记内容...',
                'type': random.choice(['normal', 'video']),
                'cover': 'https://placeholder.com/300x400',
                'user_id': f'user_{random.randint(1000, 9999)}',
                'user_name': f'AI爱好者{random.randint(1, 999)}',
                'user_avatar': 'https://placeholder.com/100x100',
                'liked_count': likes,
                'collected_count': int(likes * 0.3),
                'comment_count': int(likes * 0.1),
                'share_count': int(likes * 0.05),
                'views': views,
                'create_time': int((datetime.now() - timedelta(hours=random.randint(1, 24))).timestamp() * 1000),
                'url': f'https://www.xiaohongshu.com/explore/mock_{i}',
            }
            notes.append(note)

            time.sleep(0.1)  # 模拟延迟

        return notes

    def _generate_mock_title(self, keyword: str, is_viral: bool) -> str:
        """生成模拟标题"""
        viral_templates = [
            f"🔥 {keyword}居然可以这样用！一天涨粉1000+",
            f"💰 用{keyword}三天赚了5000块！保姆级教程",
            f"⚡ {keyword}最强玩法！99%的人都不知道",
            f"🎯 {keyword}变现实录：从0到月入过万",
            f"🚀 {keyword}神器！效率提升10倍的秘密",
        ]

        normal_templates = [
            f"{keyword}使用体验分享",
            f"我的{keyword}学习笔记",
            f"{keyword}入门指南",
            f"关于{keyword}的一些思考",
            f"{keyword}日常使用技巧",
        ]

        if is_viral:
            return random.choice(viral_templates)
        else:
            return random.choice(normal_templates)
