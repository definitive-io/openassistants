'use client';

import { Inter } from 'next/font/google';
import './globals.css';
import '@openassistants/ui/tailwind-output.css';
import { Providers } from '@openassistants/ui';

const inter = Inter({ subsets: ['latin'] });

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers defaultTheme="light" disableTransitionOnChange>
          <main className="flex flex-col flex-1 bg-muted/50">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
