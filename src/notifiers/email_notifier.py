"""
邮件通知模块
"""
import os
from typing import List, Dict
import yagmail
from datetime import datetime


class EmailNotifier:
    """邮件通知器"""

    def __init__(
        self,
        email_from: str = None,
        email_password: str = None,
        email_to: str = None
    ):
        """
        初始化邮件通知器
        Args:
            email_from: 发件邮箱
            email_password: 邮箱密码或应用专用密码
            email_to: 收件邮箱
        """
        self.email_from = email_from or os.getenv('EMAIL_FROM')
        self.email_password = email_password or os.getenv('EMAIL_PASSWORD')
        self.email_to = email_to or os.getenv('EMAIL_TO')

        if not all([self.email_from, self.email_password, self.email_to]):
            raise ValueError("邮件配置不完整")

        try:
            self.yag = yagmail.SMTP(
                user=self.email_from,
                password=self.email_password
            )
        except Exception as e:
            print(f"❌ 邮件客户端初始化失败: {e}")
            self.yag = None

    def send_viral_report(
        self,
        notes: List[Dict],
        summary: str = "",
        title: str = "小红书AI爆文日报"
    ):
        """
        发送爆文报告
        Args:
            notes: 爆文列表
            summary: 趋势总结
            title: 邮件标题
        """
        if not self.yag:
            print("❌ 邮件客户端未初始化")
            return False

        try:
            # 生成HTML内容
            html_content = self._generate_html_report(notes, summary, title)

            # 发送邮件
            self.yag.send(
                to=self.email_to,
                subject=f"{title} - {datetime.now().strftime('%Y-%m-%d')}",
                contents=html_content
            )

            print(f"✅ 邮件已发送至 {self.email_to}")
            return True

        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False

    def _generate_html_report(
        self,
        notes: List[Dict],
        summary: str,
        title: str
    ) -> str:
        """生成HTML格式的报告"""

        # 生成笔记列表HTML
        notes_html = ""
        for i, note in enumerate(notes[:10], 1):
            viral_analysis = note.get('viral_analysis', {})
            ai_analysis = note.get('ai_analysis', {})

            notes_html += f"""
            <div style="background: #f8f9fa; padding: 20px; margin-bottom: 20px; border-radius: 8px; border-left: 4px solid #007bff;">
                <h3 style="color: #333; margin-top: 0;">
                    {i}. {note.get('title', '无标题')}
                </h3>

                <div style="margin: 15px 0;">
                    <span style="background: #007bff; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; margin-right: 8px;">
                        📊 {note.get('views', 0):,} 阅读
                    </span>
                    <span style="background: #dc3545; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; margin-right: 8px;">
                        ❤️ {note.get('liked_count', 0):,} 赞
                    </span>
                    <span style="background: #28a745; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">
                        🚀 {viral_analysis.get('improvement_ratio', 0)}x 提升
                    </span>
                </div>

                <p style="color: #666; margin: 10px 0;">
                    <strong>👤 账号：</strong>{note.get('user_name', '未知')}
                    （平均阅读：{viral_analysis.get('user_avg_views', 0):,}）
                </p>

                <p style="color: #666; margin: 10px 0;">
                    <strong>🏷️ 选题：</strong>{ai_analysis.get('topic_category', '未分类')}
                </p>

                <p style="color: #666; margin: 10px 0;">
                    <strong>💡 爆点分析：</strong><br>
                    {ai_analysis.get('key_points', '暂无分析')}
                </p>

                <a href="{note.get('url', '#')}"
                   style="display: inline-block; margin-top: 10px; color: #007bff; text-decoration: none;">
                    查看原文 →
                </a>
            </div>
            """

        # 生成完整HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #ffffff;">

            <div style="text-align: center; padding: 30px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 32px;">🔥 {title}</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">{datetime.now().strftime('%Y年%m月%d日')}</p>
            </div>

            {f'''
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin-bottom: 30px; border-radius: 8px;">
                <h2 style="color: #856404; margin-top: 0;">📊 今日趋势总结</h2>
                <div style="color: #856404; line-height: 1.8; white-space: pre-wrap;">{summary}</div>
            </div>
            ''' if summary else ''}

            <h2 style="color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px;">
                🏆 昨日Top {len(notes)} 爆文
            </h2>

            {notes_html}

            <div style="text-align: center; padding: 30px; background: #f8f9fa; border-radius: 8px; margin-top: 30px;">
                <p style="color: #666; margin: 0;">
                    本报告由 <strong>小红书AI爆文检测器</strong> 自动生成<br>
                    <small style="color: #999;">Powered by Claude & Python</small>
                </p>
            </div>

        </body>
        </html>
        """

        return html
