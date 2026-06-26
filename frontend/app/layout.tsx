import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "QuoteFlow — AndesPro Industrial",
  description: "Sistema de cotizaciones B2B con revisión humana",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className={`${inter.className} bg-gray-950 text-white min-h-screen`}>
        <nav className="border-b border-gray-800 px-6 py-3 flex items-center gap-3">
          <span className="text-blue-400 font-mono font-bold text-sm">QuoteFlow</span>
          <span className="text-gray-600 text-xs">|</span>
          <span className="text-gray-400 text-xs">AndesPro Industrial</span>
        </nav>
        <main className="max-w-6xl mx-auto px-6 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
