import { Injectable, Logger } from '@nestjs/common';
import axios from 'axios';
import { PrismaService } from '../prisma.service';
import { EventsGateway } from '../events/events.gateway';

export enum BotStatus {
  IDLE = 'IDLE',
  TRADING = 'TRADING',
  PAUSED = 'PAUSED',
}

@Injectable()
export class BotService {
  private readonly logger = new Logger(BotService.name);

  constructor(
    private prisma: PrismaService,
    private events: EventsGateway,
  ) {}

  async getStatus(userId: string) {
    const state = await this.prisma.botState.findUnique({ where: { userId } });
    
    // Attempt to fetch fresh snapshot from engine if possible
    let snapshot = null;
    try {
        const engineUrl = process.env.ENGINE_URL || 'http://localhost:8000';
        const { data } = await axios.get(`${engineUrl}/gate-status`);
        snapshot = data;
    } catch (e) {
        this.logger.debug(`Could not fetch engine snapshot for user ${userId}`);
    }

    return {
      status: state?.status || BotStatus.IDLE,
      mode: state?.mode || 'PAPER',
      snapshot
    };
  }

  async setMode(userId: string, mode: 'PAPER' | 'LIVE') {
    this.logger.log(`Setting trading mode for user ${userId} to ${mode}`);
    const state = await this.prisma.botState.upsert({
      where: { userId },
      update: { mode },
      create: { userId, mode, status: BotStatus.IDLE }
    });
    this.events.broadcast('bot_mode_sync', { userId, mode });
    return state;
  }

  async startBot(userId: string) {
    this.logger.log(`Starting trading bot for user: ${userId}`);
    const state = await this.prisma.botState.upsert({
      where: { userId },
      update: { status: BotStatus.TRADING },
      create: { 
        userId,
        status: BotStatus.TRADING 
      },
    });
    
    this.events.broadcast('bot_status', { userId, status: BotStatus.TRADING });
    return state;
  }

  async stopBot(userId: string) {
    this.logger.log(`Stopping trading bot for user: ${userId}`);
    const state = await this.prisma.botState.update({
      where: { userId },
      data: { status: BotStatus.IDLE },
    });

    this.events.broadcast('bot_status', { userId, status: BotStatus.IDLE });
    return state;
  }

  async triggerSwarm(userId: string) {
    this.logger.log(`Manual Swarm Triggered by user: ${userId}`);
    try {
        const engineUrl = process.env.ENGINE_URL || 'http://localhost:8000';
        const { data } = await axios.post(`${engineUrl}/trigger-swarm`, {}, { timeout: 5000 });
        
        // Broadcast a system log notification
        this.events.broadcast('new_log', {
            time: new Date().toLocaleTimeString(),
            msg: `SIGNAL_CORE: Manual swarm scan initiated. Pulling macro context...`,
            type: 'info'
        });

        return { status: 'scanning', ...data };
    } catch (e) {
        // Graceful degradation — don't throw 500, warn the user via socket instead
        this.logger.warn(`Engine unreachable for swarm trigger: ${e.message}`);
        this.events.broadcast('new_log', {
            time: new Date().toLocaleTimeString(),
            msg: `SIGNAL_CORE: Engine offline — synthetic consensus active. Start engine to enable live swarm.`,
            type: 'warn'
        });
        return { status: 'offline', message: 'Engine unreachable. Synthetic consensus active.' };
    }
  }

  async updateEngineStatus(userId: string, data: any) {
    this.logger.log(`Engine Status Update for [${userId}]: ${data.state || 'UNKNOWN'}`);
    
    // Broadcast the entire payload to the user's room
    // The payload should include score, breakdown, gate_open, etc.
    this.events.broadcast('engine_update', {
      userId,
      ...data,
      timestamp: new Date().toISOString(),
    });

    return { success: true };
  }
}
