import { Controller, Post, Body, Get, Req, UseGuards } from '@nestjs/common';
import { PrismaService } from '../prisma.service';
import { EventsGateway } from '../events/events.gateway';
import { AnyAuthGuard } from '../auth/any-auth.guard';

@Controller('trades')
@UseGuards(AnyAuthGuard)
export class TradeController {
  constructor(
    private prisma: PrismaService,
    private events: EventsGateway,
  ) {}

  @Post('sync')
  async syncTrade(@Body() data: any, @Req() req: any) {
    const trade = await this.prisma.trade.create({
      data: {
        userId: (req as any).user.id,
        symbol: data.symbol,
        entryPrice: data.entryPrice,
        exitPrice: data.exitPrice,
        quantity: data.quantity,
        pnl: data.pnl,
        side: data.side,
        entryTime: new Date(data.entryTime),
        exitTime: data.exitTime ? new Date(data.exitTime) : null,
      },
    });

    this.events.broadcast('new_trade', { ...trade });
    return trade;
  }

  @Get('history')
  async getHistory(@Req() req: any) {
    return await this.prisma.trade.findMany({
      where: { userId: (req as any).user.id },
      orderBy: { entryTime: 'desc' },
      take: 50,
    });
  }

  @Get('metrics')
  async getMetrics(@Req() req: any) {
    const metrics = await this.prisma.metric.findUnique({ where: { userId: (req as any).user.id } });
    return metrics || { balance: 100, pnl: 0, winRate: 0, trades: 0 };
  }

  @Post('update-metrics')
  async updateMetrics(@Body() data: any, @Req() req: any) {
    const metrics = await this.prisma.metric.upsert({
      where: { userId: (req as any).user.id },
      update: {
        balance: data.balance,
        pnl: data.pnl,
        winRate: data.winRate,
        trades: data.trades,
      },
      create: {
        userId: (req as any).user.id,
        balance: data.balance,
        pnl: data.pnl,
        winRate: data.winRate,
        trades: data.trades,
      },
    });

    this.events.broadcast('metrics_update', { ...metrics });
    return metrics;
  }

  @Post('deposit')
  async deposit(@Body() data: { amount: number; method?: string }, @Req() req: any) {
    const userId = (req as any).user.id;
    const amount = Number(data.amount);
    const method = data.method || 'DIRECT_TRANSFER';

    if (isNaN(amount) || amount <= 0) {
      throw new Error('Invalid deposit amount');
    }

    const metrics = await this.prisma.metric.upsert({
      where: { userId },
      update: { balance: { increment: amount } },
      create: { userId, balance: amount, pnl: 0, winRate: 0, trades: 0 },
    });

    const log = await this.prisma.tradeLog.create({
      data: {
        userId,
        level: 'info',
        message: `TREASURY: DEPOSIT_SUCCESS - $${amount.toFixed(2)} added via ${method}.`,
      },
    });

    this.events.broadcast('metrics_update', { ...metrics });
    this.events.broadcast('new_log', { 
        time: new Date().toLocaleTimeString(), 
        msg: log.message, 
        type: 'info' 
    });

    return metrics;
  }

  @Post('withdraw')
  async withdraw(@Body() data: { amount: number; method?: string }, @Req() req: any) {
    const userId = (req as any).user.id;
    const amount = Number(data.amount);
    const method = data.method || 'DIRECT_EXTRACTION';

    const currentMetrics = await this.prisma.metric.findUnique({ where: { userId } });
    if (!currentMetrics || currentMetrics.balance < amount) {
      throw new Error('Insufficient terminal liquidity for withdrawal');
    }

    const metrics = await this.prisma.metric.update({
      where: { userId },
      data: { balance: { decrement: amount } },
    });

    const log = await this.prisma.tradeLog.create({
      data: {
        userId,
        level: 'warn',
        message: `TREASURY: WITHDRAW_SUCCESS - $${amount.toFixed(2)} extracted via ${method}.`,
      },
    });

    this.events.broadcast('metrics_update', { ...metrics });
    this.events.broadcast('new_log', { 
        time: new Date().toLocaleTimeString(), 
        msg: log.message, 
        type: 'warn' 
    });

    return metrics;
  }
}
