import { Controller, Post, Get, Body, UseGuards, Req } from '@nestjs/common';
import { BotService } from './bot.service';
import { AssistantService } from './assistant.service';
import { SessionGuard } from '../auth/session.guard';
import { SystemGuard } from '../auth/system.guard';

@Controller('bot')
export class BotController {
  constructor(
    private readonly botService: BotService,
    private readonly assistantService: AssistantService,
  ) {}

  @Get('status')
  @UseGuards(SessionGuard)
  async getStatus(@Req() req: any) {
    return await this.botService.getStatus(req.user?.id);
  }

  @Post('mode')
  @UseGuards(SessionGuard)
  async setMode(@Body() data: { mode: 'PAPER' | 'LIVE' }, @Req() req: any) {
    return await this.botService.setMode(req.user.id, data.mode);
  }

  @Post('start')
  @UseGuards(SessionGuard)
  async startBot(@Req() req: any) {
    return await this.botService.startBot(req.user.id);
  }

  @Post('stop')
  @UseGuards(SessionGuard)
  async stopBot(@Req() req: any) {
    return await this.botService.stopBot(req.user.id);
  }

  @Post('trigger-swarm')
  @UseGuards(SessionGuard)
  async triggerSwarm(@Req() req: any) {
    return await this.botService.triggerSwarm(req.user.id);
  }

  @Post('assistant/ask')
  @UseGuards(SessionGuard)
  async askAssistant(@Body() data: { question: string }, @Req() req: any) {
    const answer = await this.assistantService.getResponse(req.user.id, data.question);
    return { answer };
  }

  @Post('engine-status')
  @UseGuards(SystemGuard)
  async updateEngineStatus(@Body() data: any, @Req() req: any) {
    return await this.botService.updateEngineStatus(req.user.id, data);
  }
}
