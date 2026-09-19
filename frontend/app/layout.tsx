import './globals.css';

export const metadata = {
  title: 'BuktiSaham',
  description: 'Evidence-first Indonesian equity research',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
