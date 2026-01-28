"""
Webhook通知模块
支持企业微信、飞书、钉钉等webhook
"""
import os
import requests
from typing import List, Dict
from datetime import datetime


class WebhookNotifier:
    """Webhook通知器"""

    def __init__(
        self,
        wechat_webhook: str = None,
        feishu_webhook: str = None,
        dingtalk_webhook: str = None
    ):
        """
        初始化Webhook通知器
        Args:
            wechat_webhook: 企业微信webhook
            feishu_webhook: 飞书webhook
            dingtalk_webhook: 钉钉webhook
        """
        self.wechat_webhook = wechat_webhook or os.getenv('WECHAT_WEBHOOK')
        self.feishu_webhook = feishu_webhook or os.getenv('FEISHU_WEBHOOK')
        self.dingtalk_webhook = dingtalk_webhook or os.getenv('DINGTALK_WEBHOOK')

    def send_to_wechat(self, notes: List[Dict], summary: str = ""):
        """发送到企业微信"""
        if not self.wechat_webhook:
            print("⚠️  未配置企业微信webhook")
            return False

        try:
            # 生成Markdown内容
            content = self._generate_markdown_report(notes, summary, title="小红书AI爆文日报")

            # 企业微信API格式
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }

            response = requests.post(self.wechat_webhook, json=data, timeout=10)

            if response.status_code == 200 and response.json().get('errcode') == 0:
                print("✅ 已发送到企业微信")
                return True
            else:
                print(f"❌ 企业微信发送失败: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 企业微信发送异常: {e}")
            return False

    def send_to_feishu(self, notes: List[Dict], summary: str = ""):
        """发送到飞书"""
        if not self.feishu_webhook:
            print("⚠️  未配置飞书webhook")
            return False

        try:
            # 生成内容
            content = self._generate_markdown_report(notes, summary, title="小红书AI爆文日报")

            # 飞书API格式
            data = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": f"🔥 小红书AI爆文日报 - {datetime.now().strftime('%Y-%m-%d')}"
                        },
                        "template": "blue"
                    },
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": content
                        }
                    ]
                }
            }

            response = requests.post(self.feishu_webhook, json=data, timeout=10)

            if response.status_code == 200:
                print("✅ 已发送到飞书")
                return True
            else:
                print(f"❌ 飞书发送失败: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 飞书发送异常: {e}")
            return False

    def send_to_dingtalk(self, notes: List[Dict], summary: str = ""):
        """发送到钉钉"""
        if not self.dingtalk_webhook:
            print("⚠️  未配置钉钉webhook")
            return False

        try:
            # 生成Markdown内容
            content = self._generate_markdown_report(notes, summary, title="小红书AI爆文日报")

            # 钉钉API格式
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": f"小红书AI爆文日报 - {datetime.now().strftime('%Y-%m-%d')}",
                    "text": content
                }
            }

            response = requests.post(self.dingtalk_webhook, json=data, timeout=10)

            if response.status_code == 200 and response.json().get('errcode') == 0:
                print("✅ 已发送到钉钉")
                return True
            else:
                print(f"❌ 钉钉发送失败: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 钉钉发送异常: {e}")
            return False

    def _generate_markdown_report(
        self,
        notes: List[Dict],
        summary: str,
        title: str
    ) -> str:
        """生成Markdown格式报告"""

        content = f"# {title}\n\n"
        content += f"**日期**: {datetime.now().strftime('%Y年%m月%d日')}\n\n"

        # 添加总结
        if summary:
            content += f"## 📊 今日趋势总结\n\n{summary}\n\n"

        # 添加爆文列表
        content += f"## 🏆 昨日Top {len(notes)} 爆文\n\n"

        for i, note in enumerate(notes[:10], 1):
            viral_analysis = note.get('viral_analysis', {})
            ai_analysis = note.get('ai_analysis', {})

            content += f"### {i}. {note.get('title', '无标题')}\n\n"
            content += f"**📊 数据**: {note.get('views', 0):,}阅读 | "
            content += f"{note.get('liked_count', 0):,}赞 | "
            content += f"**{viral_analysis.get('improvement_ratio', 0)}x**提升\n\n"
            content += f"**👤 账号**: {note.get('user_name', '未知')} "
            content += f"(平均阅读: {viral_analysis.get('user_avg_views', 0):,})\n\n"
            content += f"**🏷️ 选题**: {ai_analysis.get('topic_category', '未分类')}\n\n"
            content += f"**💡 爆点**: {ai_analysis.get('key_points', '暂无分析')}\n\n"
            content += f"[查看原文]({note.get('url', '#')})\n\n"
            content += "---\n\n"

        content += "*本报告由小红书AI爆文检测器自动生成*\n"

        return content
