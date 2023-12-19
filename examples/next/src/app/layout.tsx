'use client';

import { Providers } from '@definitive-io/openassistants-react';
import '@definitive-io/openassistants-react/dist/styles.css';

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers defaultTheme="light" disableTransitionOnChange>
          <main className="flex h-full flex-col flex-1 bg-white">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
