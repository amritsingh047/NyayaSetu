import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from '@/components/providers';

const inter = Inter({ subsets: ['latin'], display: 'swap', fallback: ['system-ui', 'sans-serif'] });

export const metadata: Metadata = {
  title: 'NyayaSetu (न्याय सेतु) — AI Legal Information & Document Comprehension',
  description: 'AI-assisted legal information platform grounded in Indian law. Not legal advice.',
  keywords: ['legal', 'AI', 'NyayaSetu', 'Indian law', 'contract analysis', 'GST', 'DPDP'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
