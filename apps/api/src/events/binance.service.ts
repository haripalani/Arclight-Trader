import { Injectable, OnModuleInit, Logger } from '@nestjs/common';
import WebSocket from 'ws';
import { EventsGateway } from './events.gateway';

@Injectable()
export class BinanceService implements OnModuleInit {
  private readonly logger = new Logger(BinanceService.name);
  private ws: WebSocket;

  constructor(private readonly eventsGateway: EventsGateway) {}

  onModuleInit() {
    this.connect();
  }

  private connect() {
    this.logger.log('Connecting to Binance WebSocket Proxy...');
    this.ws = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@kline_1m');

    this.ws.on('open', () => {
      this.logger.log('Connected to Binance WebSocket successfully');
    });

    this.ws.on('message', (data: string) => {
      try {
        const message = JSON.parse(data);
        const candle = message.k;
        if (candle) {
          // Broadcast to all connected clients via Socket.io
          this.eventsGateway.server.emit('kline_update', {
            time: candle.t / 1000,
            open: parseFloat(candle.o),
            high: parseFloat(candle.h),
            low: parseFloat(candle.l),
            close: parseFloat(candle.c),
          });
        }
      } catch (e) {
        this.logger.error('Failed to parse Binance message', e);
      }
    });

    this.ws.on('error', (err) => {
      this.logger.error('Binance WebSocket Proxy error', err.message);
    });

    this.ws.on('close', () => {
      this.logger.warn('Binance WebSocket Proxy closed. Reconnecting in 5s...');
      setTimeout(() => this.connect(), 5000);
    });
  }
}
