import type { Metadata } from "next";
import "./globals.css";
import Navigation from "../components/Navigation";

export const metadata: Metadata = {
  title: "FaithGuide AI - Safe Christianity Assistant",
  description: "Advanced Christianity-focused AI assistant with scripture grounding, dual-layer citation validation, theological neutrality, and adversarial prompt shields.",
  icons: {
    icon: "/favicon.ico",
  }
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen flex flex-col bg-[#0B0F19] text-slate-100 selection:bg-[#D4AF37]/30 selection:text-[#D4AF37]">
        <Navigation />
        <main className="flex-1 w-full flex flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}
