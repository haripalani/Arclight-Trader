import { Module, Global } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { AuthService } from './auth.service';
import { AuthController } from './auth.controller';
import { PrismaService } from '../prisma.service';
import { SessionGuard } from './session.guard';
import { SystemGuard } from './system.guard';
import { AnyAuthGuard } from './any-auth.guard';
import { ConfigService } from '@nestjs/config';

@Global()
@Module({
  imports: [ConfigModule],
  providers: [
    AuthService, 
    SessionGuard, 
    SystemGuard, 
    AnyAuthGuard
  ],
  controllers: [AuthController],
  exports: [AuthService, SessionGuard, SystemGuard, AnyAuthGuard],
})
export class AuthModule {}
