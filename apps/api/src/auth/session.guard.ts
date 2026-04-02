import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { AuthService } from './auth.service';

@Injectable()
export class SessionGuard implements CanActivate {
  constructor(private authService: AuthService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const sessionId = request.cookies['sessionId'];

    if (!sessionId) {
      throw new UnauthorizedException('Authentication required');
    }

    try {
      const user = await this.authService.validateSession(sessionId);
      request.user = user;
      return true;
    } catch (e) {
      throw new UnauthorizedException('Invalid or expired session');
    }
  }
}
