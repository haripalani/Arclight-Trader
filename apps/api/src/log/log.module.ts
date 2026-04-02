import { Module } from '@nestjs/common';
import { LogService } from './log.service';
import { PrismaService } from '../prisma.service';
import { EventsModule } from '../events/events.module';

import { LogController } from './log.controller';

@Module({
  imports: [EventsModule],
  controllers: [LogController],
  providers: [LogService, PrismaService],
  exports: [LogService],
})
export class LogModule {}
