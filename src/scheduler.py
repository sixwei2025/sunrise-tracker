"""
定时任务调度器
每天定时执行爆文检测任务
"""
import os
import time
import yaml
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from rich.console import Console
from dotenv import load_dotenv

from main import ViralPostsDetector


# 加载环境变量
load_dotenv()

# 初始化控制台
console = Console()


class TaskScheduler:
    """任务调度器"""

    def __init__(self, config_path: str = './config/config.yaml'):
        """
        初始化调度器
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.detector = ViralPostsDetector(config_path)
        self.scheduler = BlockingScheduler(timezone=self.config.get('schedule', {}).get('timezone', 'Asia/Shanghai'))

    def run_task(self):
        """执行检测任务"""
        console.print("\n" + "="*60)
        console.print(f"⏰ [bold cyan]定时任务触发[/bold cyan]")
        console.print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        console.print("="*60 + "\n")

        try:
            self.detector.run()
        except Exception as e:
            console.print(f"❌ [red]任务执行失败: {e}[/red]")
            import traceback
            traceback.print_exc()

    def start(self):
        """启动调度器"""
        schedule_config = self.config.get('schedule', {})
        daily_time = schedule_config.get('daily_time', '07:00')

        # 解析时间
        hour, minute = map(int, daily_time.split(':'))

        # 添加定时任务
        self.scheduler.add_job(
            self.run_task,
            trigger=CronTrigger(hour=hour, minute=minute),
            id='daily_viral_detection',
            name='小红书AI爆文检测',
            replace_existing=True
        )

        console.print("="*60)
        console.print("🚀 [bold green]小红书AI爆文检测器已启动[/bold green]")
        console.print("="*60)
        console.print(f"⏰ 定时任务: 每天 {daily_time} 执行")
        console.print(f"🌍 时区: {schedule_config.get('timezone', 'Asia/Shanghai')}")
        console.print(f"📊 推送数量: Top {self.config.get('notification', {}).get('top_n', 10)}")
        console.print("="*60)
        console.print("\n💡 提示: 按 Ctrl+C 停止程序\n")

        try:
            # 可选：启动时立即执行一次
            if os.getenv('RUN_ON_START', 'false').lower() == 'true':
                console.print("🏃 立即执行一次任务...\n")
                self.run_task()

            # 启动调度器
            self.scheduler.start()

        except (KeyboardInterrupt, SystemExit):
            console.print("\n\n👋 程序已停止\n")
            self.scheduler.shutdown()


def main():
    """主函数"""
    try:
        scheduler = TaskScheduler()
        scheduler.start()
    except FileNotFoundError as e:
        console.print(f"❌ [red]配置文件未找到: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]启动失败: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
