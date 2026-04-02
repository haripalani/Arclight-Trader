import { PrismaClient } from '@prisma/client';
import * as bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  const email = 'trader@arclight.ai';
  const password = 'password123';
  const saltRounds = 12;

  // Check if user already exists
  const existingUser = await prisma.user.findUnique({
    where: { email },
  });

  if (existingUser) {
    console.log('Seed user already exists. Skipping...');
    return;
  }

  const passwordHash = await bcrypt.hash(password, saltRounds);

  const user = await prisma.user.create({
    data: {
      email,
      passwordHash,
      isVerified: true,
      botStates: {
        create: {
            status: 'IDLE',
            mode: 'PAPER'
        }
      },
      metrics: {
        create: {
            balance: 10000.0,
            pnl: 0.0,
            winRate: 0.0,
            trades: 0
        }
      },
      skillProfiles: {
        create: {
            technicalAnalysis: 75,
            riskManagement: 80,
            marketAdaptation: 65,
            strategyConfidence: 0.8,
            notes: 'Initial Arclight seed profile'
        }
      }
    },
  });

  console.log(`Seed user created: ${user.email}`);
  console.log(`Login Email: ${email}`);
  console.log(`Login Password: ${password}`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
