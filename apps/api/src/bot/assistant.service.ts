import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma.service';

@Injectable()
export class AssistantService {
  private readonly logger = new Logger(AssistantService.name);

  constructor(private prisma: PrismaService) {}

  async getResponse(userId: string, question: string): Promise<string> {
    this.logger.log(`Assistant query for user ${userId}: ${question}`);

    // Fetch context
    const [recentLogs, evolutionLogs, metrics] = await Promise.all([
      this.prisma.tradeLog.findMany({
        where: { userId },
        orderBy: { timestamp: 'desc' },
        take: 5,
      }),
      this.prisma.evolutionLog.findMany({
        where: { userId },
        orderBy: { timestamp: 'desc' },
        take: 3,
      }),
      this.prisma.metric.findUnique({ where: { userId } }),
    ]);

    const context = {
      balance: metrics?.balance || 100,
      pnl: metrics?.pnl || 0,
      winRate: metrics?.winRate || 0,
      recentActivity: recentLogs.map(l => l.message).join(' | '),
      recentInsights: evolutionLogs.map(e => e.insight).join(' | '),
    };

    // Simplified NLP Logic (In a real app, this would call GPT/LLM)
    const q = question.toLowerCase();
    
    if (q.includes('hello') || q.includes('hi') || q.includes('hey')) {
      const greetings = [
        "Greeting acknowledged. Systems are nominal. How can I assist with your strategy?",
        "Portal active. I am monitoring the 1m candle flows. What do you need to know?",
        "Ready. Arclight Neural Link is stable. Direct your query."
      ];
      return greetings[Math.floor(Math.random() * greetings.length)];
    }

    if (q.includes('status') || q.includes('doing')) {
      return `Current Balance: $${context.balance.toFixed(2)}. PnL: $${context.pnl.toFixed(2)}. Recent activity: ${context.recentActivity || 'IDLE'}.`;
    }
    
    if (q.includes('insight') || q.includes('think') || q.includes('why')) {
      return `My last evolution phase noted: ${context.recentInsights || 'Steady state maintained'}. I am currently optimizing for market volatility.`;
    }
 
    if (q.includes('win') || q.includes('rate') || q.includes('performance')) {
      return `Your strategy win rate is currently ${context.winRate.toFixed(1)}%. We have executed ${metrics?.trades || 0} trades so far.`;
    }

    const fallbacks = [
      "I've analyzed your current strategy and market conditions. We are maintaining a high-confidence posture. Is there a specific metric or log you'd like me to explain?",
      "Market volatility is currently being processed. Strategy alignment is within expected parameters. What specific data point should I retrieve?",
      "Arclight systems are scanning for opportunities. Performance metrics are stable. Deep dive into a specific log?",
      "Current posture is optimized for the detected trend. Would you like a breakdown of recent trade signals?"
    ];

    return fallbacks[Math.floor(Math.random() * fallbacks.length)];
  }
}
