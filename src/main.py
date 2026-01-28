"""
小红书AI爆文检测器 - 主程序
"""
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from scrapers import MockXiaohongshuScraper
from analyzers import ViralDetector, AIContentAnalyzer
from notifiers import EmailNotifier, WebhookNotifier


# 加载环境变量
load_dotenv()

# 初始化控制台
console = Console()


class ViralPostsDetector:
    """爆文检测器主类"""

    def __init__(self, config_path: str = './config/config.yaml'):
        """
        初始化检测器
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # 初始化各个模块
        self.scraper = self._init_scraper()
        self.detector = self._init_detector()
        self.analyzer = self._init_analyzer()
        self.notifiers = self._init_notifiers()

    def _init_scraper(self):
        """初始化爬虫"""
        cookie = os.getenv('XHS_COOKIE')

        # 使用模拟数据（用于开发测试）
        # 实际部署时，请使用真实的 XiaohongshuScraper
        console.print("🔧 [yellow]使用模拟数据模式（开发测试）[/yellow]")
        return MockXiaohongshuScraper(cookie=cookie)

    def _init_detector(self):
        """初始化检测器"""
        detection_config = self.config.get('viral_detection', {})
        db_path = os.getenv('DB_PATH', './data/viral_posts.json')

        # 确保数据目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        return ViralDetector(
            db_path=db_path,
            min_viral_views=detection_config.get('min_viral_views', 3000),
            max_avg_views=detection_config.get('max_avg_views', 500),
            viral_multiplier=detection_config.get('viral_multiplier', 5.0)
        )

    def _init_analyzer(self):
        """初始化AI分析器"""
        try:
            return AIContentAnalyzer()
        except ValueError as e:
            console.print(f"⚠️  [yellow]{e}，AI分析功能将不可用[/yellow]")
            return None

    def _init_notifiers(self):
        """初始化通知器"""
        notifiers = []
        notification_methods = self.config.get('notification', {}).get('methods', [])

        # 邮件通知
        if 'email' in notification_methods:
            try:
                email_notifier = EmailNotifier()
                notifiers.append(('email', email_notifier))
                console.print("✅ 邮件通知已启用")
            except ValueError as e:
                console.print(f"⚠️  [yellow]邮件通知未配置: {e}[/yellow]")

        # Webhook通知
        webhook_notifier = WebhookNotifier()

        if 'wechat' in notification_methods and webhook_notifier.wechat_webhook:
            notifiers.append(('wechat', webhook_notifier))
            console.print("✅ 企业微信通知已启用")

        if 'feishu' in notification_methods and webhook_notifier.feishu_webhook:
            notifiers.append(('feishu', webhook_notifier))
            console.print("✅ 飞书通知已启用")

        if 'dingtalk' in notification_methods and webhook_notifier.dingtalk_webhook:
            notifiers.append(('dingtalk', webhook_notifier))
            console.print("✅ 钉钉通知已启用")

        return notifiers

    def run(self):
        """执行检测任务"""
        console.print("\n" + "="*60)
        console.print("🔥 [bold cyan]小红书AI爆文检测器[/bold cyan]")
        console.print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        console.print("="*60 + "\n")

        try:
            # 1. 抓取数据
            all_notes = self._fetch_notes()

            if not all_notes:
                console.print("❌ [red]未抓取到任何数据[/red]")
                return

            # 2. 检测爆文
            viral_notes = self._detect_viral(all_notes)

            if not viral_notes:
                console.print("ℹ️  [yellow]未发现符合条件的爆文[/yellow]")
                return

            # 3. AI分析
            analyzed_notes = self._analyze_notes(viral_notes)

            # 4. 生成报告
            summary = self._generate_summary(analyzed_notes)

            # 5. 发送通知
            self._send_notifications(analyzed_notes, summary)

            console.print("\n✅ [bold green]任务执行完成！[/bold green]\n")

        except Exception as e:
            console.print(f"\n❌ [bold red]执行出错: {e}[/bold red]\n")
            import traceback
            traceback.print_exc()

    def _fetch_notes(self):
        """抓取笔记数据"""
        console.print("📥 [bold]1. 抓取小红书数据[/bold]")

        keywords = self.config.get('search_keywords', [])
        notes_per_keyword = self.config.get('scraping', {}).get('notes_per_keyword', 50)

        all_notes = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            for keyword in keywords:
                task = progress.add_task(f"🔍 搜索: {keyword}", total=None)

                try:
                    notes = self.scraper.search_notes(
                        keyword=keyword,
                        limit=notes_per_keyword
                    )
                    all_notes.extend(notes)
                    progress.update(task, completed=True)
                    console.print(f"   ✓ {keyword}: 获取 {len(notes)} 篇")

                except Exception as e:
                    console.print(f"   ✗ {keyword}: 失败 ({e})")

        console.print(f"\n📊 共抓取 {len(all_notes)} 篇笔记\n")
        return all_notes

    def _detect_viral(self, notes):
        """检测爆文"""
        console.print("🔍 [bold]2. 检测爆文[/bold]")

        viral_notes = self.detector.detect_viral_notes(notes)

        console.print(f"   发现 {len(viral_notes)} 篇爆文\n")
        return viral_notes

    def _analyze_notes(self, notes):
        """AI分析爆文"""
        console.print("🤖 [bold]3. AI分析爆点[/bold]")

        if not self.analyzer:
            console.print("   ⚠️  AI分析器未初始化，跳过分析\n")
            return notes

        top_n = self.config.get('notification', {}).get('top_n', 10)
        top_notes = notes[:top_n]

        analyzed_notes = self.analyzer.analyze_batch(top_notes)

        console.print(f"   ✓ 完成 {len(analyzed_notes)} 篇分析\n")
        return analyzed_notes

    def _generate_summary(self, notes):
        """生成趋势总结"""
        console.print("📊 [bold]4. 生成趋势总结[/bold]")

        if not self.analyzer or not notes:
            console.print("   ⚠️  跳过总结生成\n")
            return ""

        try:
            summary = self.analyzer.generate_summary(notes)
            console.print("   ✓ 总结生成完成\n")
            return summary
        except Exception as e:
            console.print(f"   ✗ 生成失败: {e}\n")
            return ""

    def _send_notifications(self, notes, summary):
        """发送通知"""
        console.print("📧 [bold]5. 发送通知[/bold]")

        if not self.notifiers:
            console.print("   ⚠️  未配置任何通知方式\n")
            return

        title = self.config.get('notification', {}).get('title', '小红书AI爆文日报')

        for method, notifier in self.notifiers:
            try:
                if method == 'email':
                    notifier.send_viral_report(notes, summary, title)
                elif method == 'wechat':
                    notifier.send_to_wechat(notes, summary)
                elif method == 'feishu':
                    notifier.send_to_feishu(notes, summary)
                elif method == 'dingtalk':
                    notifier.send_to_dingtalk(notes, summary)
            except Exception as e:
                console.print(f"   ✗ {method} 发送失败: {e}")

        console.print()


def main():
    """主函数"""
    try:
        detector = ViralPostsDetector()
        detector.run()
    except FileNotFoundError as e:
        console.print(f"❌ [red]配置文件未找到: {e}[/red]")
        console.print("   请先复制 config/config.yaml.example 到 config/config.yaml")
    except Exception as e:
        console.print(f"❌ [red]初始化失败: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
