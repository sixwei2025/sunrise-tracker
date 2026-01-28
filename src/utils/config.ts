import dotenv from 'dotenv';
import { Config } from '../types';

dotenv.config();

export function loadConfig(): Config {
  return {
    xhsCookie: process.env.XHS_COOKIE,
    aiProvider: (process.env.AI_PROVIDER as any) || 'none',
    aiApiKey: process.env.AI_API_KEY,
    aiModel: process.env.AI_MODEL || 'gpt-4',
    notificationType: (process.env.NOTIFICATION_TYPE as any) || 'console',
    emailConfig: process.env.EMAIL_HOST ? {
      host: process.env.EMAIL_HOST,
      port: parseInt(process.env.EMAIL_PORT || '587'),
      user: process.env.EMAIL_USER!,
      password: process.env.EMAIL_PASSWORD!,
      to: process.env.EMAIL_TO!,
    } : undefined,
    webhookUrl: process.env.WEBHOOK_URL,
    cronSchedule: process.env.CRON_SCHEDULE || '0 7 * * *',
    minViralMultiplier: parseFloat(process.env.MIN_VIRAL_MULTIPLIER || '10'),
    minViewsThreshold: parseInt(process.env.MIN_VIEWS_THRESHOLD || '1000'),
    topNPosts: parseInt(process.env.TOP_N_POSTS || '10'),
  };
}
