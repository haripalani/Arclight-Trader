import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PrismaService } from '../prisma.service';
import * as bcrypt from 'bcryptjs';
import { Response } from 'express';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class AuthService {
  private readonly SALT_ROUNDS = 12;

  constructor(private prisma: PrismaService) {}

  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, this.SALT_ROUNDS);
  }

  async comparePasswords(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }

  async createSession(userId: string, res: Response) {
    const session = await this.prisma.session.create({
      data: {
        userId,
        expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24 * 7), // 7 days
      },
    });

    res.cookie('sessionId', session.id, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 1000 * 60 * 60 * 24 * 7, // 7 days
    });

    return session;
  }

  async logout(sessionId: string, res: Response) {
    await this.prisma.session.delete({ where: { id: sessionId } }).catch(() => {});
    res.clearCookie('sessionId');
    return { message: 'Logged out successfully' };
  }

  async validateSession(sessionId: string) {
    if (!sessionId) {
      throw new UnauthorizedException('No session found');
    }

    const session = await this.prisma.session.findUnique({
      where: { id: sessionId },
      include: { user: true },
    });

    if (!session || session.expiresAt < new Date()) {
      if (session) {
        await this.prisma.session.delete({ where: { id: sessionId } }).catch(() => {});
      }
      throw new UnauthorizedException('Session expired or invalid');
    }

    return session.user;
  }
}
