import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma.service';
import { EventsGateway } from '../events/events.gateway';

@Injectable()
export class LogService {
  private readonly logger = new Logger(LogService.name);

  constructor(
    private prisma: PrismaService,
    private events: EventsGateway,
  ) {}

  async addLog(userId: string, level: string, message: string, metadata?: any) {
    this.logger.log(`[${level.toUpperCase()}] ${message} (User: ${userId})`);

    const log = await this.prisma.tradeLog.create({
      data: {
        userId,
        level,
        message,
        metadata: metadata || {},
      },
    });

    this.events.broadcast('new_log', {
      userId,
      time: log.timestamp.toLocaleTimeString(),
      msg: log.message,
      type: log.level,
    });

    return log;
  }
}
