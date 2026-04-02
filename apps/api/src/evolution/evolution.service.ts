import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma.service';
import axios from 'axios';

@Injectable()
export class EvolutionService {
  private readonly logger = new Logger(EvolutionService.name);

  constructor(private prisma: PrismaService) {}

  async evolveStrategy(userId: string) {
    this.logger.log(`Starting AI Strategy Evolution Loop for user: ${userId}`);
    this.logger.log(`Available Prisma Models: ${Object.keys(this.prisma).filter(k => !k.startsWith('$')).join(', ')}`);

    // 1. Fetch last 50 trades
    const trades = await this.prisma.trade.findMany({
      where: { userId },
      orderBy: { entryTime: 'desc' },
      take: 50,
    });

    if (trades.length === 0) {
      this.logger.warn('No trades found for evolution.');
      return { message: 'No trades found' };
    }

    // 2. Fetch current Skill Profile
    let profile = await this.prisma.skillProfile.findUnique({ where: { userId } });
    if (!profile) {
      profile = await this.prisma.skillProfile.create({
        data: { userId, notes: 'Initial system state' },
      });
    }

    // 3. Construct Prompt for Qwen
    const prompt = `
    You are the Arclight Evolution Engine. Analyze the following trade history and update the system's Skill Profile.
    
    Current Profile:
    ${JSON.stringify(profile)}
    
    Recent Trades:
    ${JSON.stringify(trades)}
    
    Your goal is to optimize:
    - technicalAnalysis (0-100)
    - riskManagement (0-100)
    - strategyConfidence (0.1 - 1.0)
    
    Return a JSON object with:
    {
      "technicalAnalysis": number,
      "riskManagement": number,
      "marketAdaptation": number,
      "strategyConfidence": number,
      "insight": "short string",
      "action": "short string",
      "adjustments": {
         "ml_alpha_bias": "BUY" | "SELL" | "HOLD",
         "recommended_strategy": "Trend Following" | "Statistical Arbitrage" | "ML Alpha / Core EMA"
      } 
    }
    `;

    try {
      this.logger.log(`Calling LLM: ${process.env.LLM_MODEL_NAME} at ${process.env.LLM_BASE_URL}`);
      
      const response = await axios.post(`${process.env.LLM_BASE_URL}/chat/completions`, {
        model: process.env.LLM_MODEL_NAME,
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.1,
      }, {
        headers: { 'Authorization': `Bearer ${process.env.LLM_API_KEY}` }
      });

      this.logger.log('LLM Response received.');
      
      const content = response.data?.choices?.[0]?.message?.content;
      if (!content) {
        this.logger.error('Empty LLM response content', JSON.stringify(response.data));
        throw new Error('Empty LLM response');
      }

      // Resilient JSON extraction (remove markdown code blocks if present)
      const jsonStr = content.replace(/```json|```/g, '').trim();
      const update = JSON.parse(jsonStr);

      // 4. Update Skill Profile
      const updatedProfile = await this.prisma.skillProfile.update({
        where: { userId },
        data: {
          technicalAnalysis: update.technicalAnalysis || profile.technicalAnalysis,
          riskManagement: update.riskManagement || profile.riskManagement,
          marketAdaptation: update.marketAdaptation || profile.marketAdaptation,
          strategyConfidence: update.strategyConfidence || profile.strategyConfidence,
          notes: update.insight || 'Updated via evolution',
          strategyAdjustments: update.adjustments || {},
        },
      });

      // 5. Log Evolution
      await this.prisma.evolutionLog.create({
        data: {
          userId,
          insight: update.insight,
          action: update.action,
          metadata: update,
        },
      });

      this.logger.log(`Strategy Evolved: ${update.insight}`);
      return updatedProfile;

    } catch (error) {
      this.logger.error('Failed to evolve strategy:', error.message);
      return { error: error.message };
    }
  }

  async getProfile(userId: string) {
    const profile = await this.prisma.skillProfile.findUnique({ where: { userId } });
    return profile || { strategyAdjustments: { ml_alpha_bias: "HOLD" } };
  }
}
