import { Controller, Post, Body, UseGuards, Req } from '@nestjs/common';
import { LogService } from './log.service';
import { SystemGuard } from '../auth/system.guard';

@Controller('log')
export class LogController {
  constructor(private readonly logService: LogService) {}

  @Post()
  @UseGuards(SystemGuard)
  async addLog(@Body() data: { level: string; message: string; metadata?: any }, @Req() req: any) {
    return await this.logService.addLog(req.user.id, data.level, data.message, data.metadata);
  }
}
