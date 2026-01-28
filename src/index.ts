import cron from 'node-cron';
import { ViralDetectorApp } from './app';

const app = new ViralDetectorApp();

async function main() {
  console.log('🎯 小红书AI爆文检测器已启动');
  console.log('==============================================\n');

  const config = app.getConfig();

  // 解析命令行参数
  const args = process.argv.slice(2);
  const runNow = args.includes('--now') || args.includes('-n');
  const runOnce = args.includes('--once') || args.includes('-o');

  if (runNow || runOnce) {
    // 立即执行一次
    console.log('⚡ 立即执行检测任务...\n');
    await app.runDailyCheck();

    if (runOnce) {
      console.log('\n👋 任务完成，程序退出');
      process.exit(0);
    }
  }

  // 设置定时任务
  console.log(`⏰ 定时任务已配置: ${config.cronSchedule}`);
  console.log(`   (每天早上7点自动执行)\n`);

  cron.schedule(config.cronSchedule, async () => {
    console.log(`\n⏰ 定时任务触发 - ${new Date().toLocaleString('zh-CN')}`);
    try {
      await app.runDailyCheck();
    } catch (error) {
      console.error('定时任务执行失败:', error);
    }
  });

  console.log('✅ 程序运行中... (按 Ctrl+C 退出)\n');
}

// 优雅退出
process.on('SIGINT', () => {
  console.log('\n\n👋 收到退出信号，程序即将关闭...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n\n👋 收到终止信号，程序即将关闭...');
  process.exit(0);
});

// 启动应用
main().catch((error) => {
  console.error('程序启动失败:', error);
  process.exit(1);
});
