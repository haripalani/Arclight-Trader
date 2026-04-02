import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class SystemGuard implements CanActivate {
  constructor(private configService: ConfigService) {}

  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const apiKey = request.headers['x-api-key'];
    const systemKey = this.configService.get<string>('SYSTEM_API_KEY');

    if (!systemKey) {
      throw new UnauthorizedException('System API Key not configured');
    }

    if (apiKey !== systemKey) {
      throw new UnauthorizedException('Invalid System API Key');
    }

    // For system calls, we expect a x-user-id header to identify which user data to touched
    const userId = request.headers['x-user-id'];
    if (!userId) {
      throw new UnauthorizedException('Missing x-user-id header for system operation');
    }

    // Inject the system-provided user into the request for compatibility with existing logic
    request.user = { id: userId };
    
    return true;
  }
}
