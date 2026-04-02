import { Module } from '@nestjs/common';
import { EventsGateway } from './events.gateway';
import { BinanceService } from './binance.service';

@Module({
  providers: [EventsGateway, BinanceService],
  exports: [EventsGateway],
})
export class EventsModule {}
