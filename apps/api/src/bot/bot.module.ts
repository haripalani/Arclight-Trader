import { Module } from '@nestjs/common';
import { BotService } from './bot.service';
import { AssistantService } from './assistant.service';
import { BotController } from './bot.controller';
import { PrismaService } from '../prisma.service';
import { EventsModule } from '../events/events.module';

@Module({
  imports: [EventsModule],
  providers: [BotService, AssistantService, PrismaService],
  controllers: [BotController],
})
export class BotModule {}
