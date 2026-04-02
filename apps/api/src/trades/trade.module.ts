import { Module } from '@nestjs/common';
import { TradeController } from './trade.controller';
import { PrismaService } from '../prisma.service';
import { EventsModule } from '../events/events.module';
import { AuthModule } from '../auth/auth.module';

@Module({
  imports: [EventsModule],
  controllers: [TradeController],
  providers: [],
})
export class TradeModule {}
