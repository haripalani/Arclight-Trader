import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { Logger, ValidationPipe } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import cookieParser from 'cookie-parser';
import helmet from 'helmet';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Check 03: Secure HTTP Headers
  app.use(helmet());

  // Check 01: Secure Cookies
  app.use(cookieParser());

  // Check 06: Strict Input Validation & Sanitization
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );

  // Debug 01: Global Request Logger
  app.use((req, res, next) => {
    Logger.log(`${req.method} ${req.url}`, 'RequestLogger');
    next();
  });

  app.enableCors({
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    credentials: true,
  });
  
  const configService = app.get(ConfigService);
  const port = configService.get<number>('PORT') || 9001;
  await app.listen(port);
  
  Logger.log(`Application is running on: http://localhost:${port}`, 'Bootstrap');
}
bootstrap();
