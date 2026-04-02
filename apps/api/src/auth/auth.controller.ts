import { 
  Controller, 
  Post, 
  Body, 
  Res, 
  Req, 
  UnauthorizedException, 
  BadRequestException,
  Get,
  UseGuards
} from '@nestjs/common';
import { AuthService } from './auth.service';
import { PrismaService } from '../prisma.service';
import type { Response, Request } from 'express';
import { RegisterDto, LoginDto } from './dto/auth.dto';

@Controller('auth')
export class AuthController {
  constructor(
    private authService: AuthService,
    private prisma: PrismaService,
  ) {}

  @Post('register')
  async register(@Body() dto: RegisterDto) {
    const existingUser = await this.prisma.user.findUnique({ where: { email: dto.email } });
    if (existingUser) {
      throw new BadRequestException('User already exists');
    }

    const passwordHash = await this.authService.hashPassword(dto.password);
    const user = await this.prisma.user.create({
      data: {
        email: dto.email,
        passwordHash,
      },
    });

    // Automatically create a SkillProfile for the new user
    await this.prisma.skillProfile.create({
      data: { userId: user.id }
    });
    
    // Automatically create Metric for the new user
    await this.prisma.metric.create({
      data: { userId: user.id }
    });

    return { message: 'User registered successfully. Please verify your email.' };
  }

  @Post('login')
  async login(@Body() dto: LoginDto, @Res({ passthrough: true }) res: Response) {
    const user = await this.prisma.user.findUnique({ where: { email: dto.email } });
    if (!user) {
      throw new UnauthorizedException('Invalid credentials');
    }

    const isPasswordValid = await this.authService.comparePasswords(dto.password, user.passwordHash);
    if (!isPasswordValid) {
      throw new UnauthorizedException('Invalid credentials');
    }

    await this.authService.createSession(user.id, res);
    return { id: user.id, email: user.email };
  }

  @Post('logout')
  async logout(@Req() req: Request, @Res({ passthrough: true }) res: Response) {
    const sessionId = req.cookies['sessionId'];
    return this.authService.logout(sessionId, res);
  }

  @Get('me')
  async me(@Req() req: Request) {
    const sessionId = req.cookies['sessionId'];
    const user = await this.authService.validateSession(sessionId);
    return { id: user.id, email: user.email };
  }
}
