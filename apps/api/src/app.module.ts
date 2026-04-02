import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { APP_GUARD } from '@nestjs/core';
import { BotModule } from './bot/bot.module';
import { LogModule } from './log/log.module';
import { EventsModule } from './events/events.module';
import { TradeModule } from './trades/trade.module';
import { EvolutionModule } from './evolution/evolution.module';
import { AuthModule } from './auth/auth.module';
import { PrismaModule } from './prisma.module';
import { AppController } from './app.controller';
import { AppService } from './app.service';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    // Check 04: Abuse Protection (Rate Limiting)
    ThrottlerModule.forRoot([{
      ttl: 60000,
      limit: 100, // 100 requests per minute by default
    }]),
    BotModule,
    LogModule,
    EventsModule,
    TradeModule,
    EvolutionModule,
    AuthModule,
    PrismaModule,
  ],
  controllers: [AppController],
  providers: [
    AppService,
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
  ],
  exports: [],
})
export class AppModule {}
