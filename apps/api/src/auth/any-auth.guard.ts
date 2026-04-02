import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { SessionGuard } from './session.guard';
import { SystemGuard } from './system.guard';

@Injectable()
export class AnyAuthGuard implements CanActivate {
  constructor(
    private sessionGuard: SessionGuard,
    private systemGuard: SystemGuard,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    // Try Session Guard first
    try {
      const isSessionValid = await this.sessionGuard.canActivate(context);
      if (isSessionValid) return true;
    } catch (e) {
      // Ignore session errors and try System Guard
    }

    // Try System Guard
    try {
      const isSystemValid = await this.systemGuard.canActivate(context);
      if (isSystemValid) return true;
    } catch (e) {
      // Both failed
    }

    throw new UnauthorizedException('Authentication failed (Session or System key required)');
  }
}
