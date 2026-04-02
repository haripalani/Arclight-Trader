import { Controller, Post, Get, UseGuards, Req } from '@nestjs/common';
import { EvolutionService } from './evolution.service';
import { SessionGuard } from '../auth/session.guard';
import { SystemGuard } from '../auth/system.guard';
import { Throttle } from '@nestjs/throttler';

@Controller('evolution')
export class EvolutionController {
  constructor(private readonly evolutionService: EvolutionService) {}

  @Throttle({ default: { limit: 10, ttl: 3600000 } }) // Check 04: Max 10 AI generations per hour
  @Post('trigger')
  @UseGuards(SessionGuard)
  async triggerEvolution(@Req() req: any) {
    return await this.evolutionService.evolveStrategy(req.user.id);
  }

  @Get('profile')
  @UseGuards(SystemGuard)
  async getProfile(@Req() req: any) {
    return await this.evolutionService.getProfile(req.user.id);
  }
}
