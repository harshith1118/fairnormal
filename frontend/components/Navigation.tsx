"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare, Image, BarChart3, ShieldCheck, Activity } from "lucide-react";
import { useEffect, useState } from "react";
import { checkHealth } from "@/lib/api";
import { API_BASE_URL } from "@/lib/api"; // Added for debugging

// Navigation component for FaithGuide AI (Re-evaluating health check)
export default function Navigation() {
  const pathname = usePathname();
  const [dbStatus, setDbStatus] = useState<"HEALTHY" | "DEGRADED" | "CHECKING">("CHECKING");

  useEffect(() => {
    async function performHealthCheck() {
      try {
        const data = await checkHealth();
        setDbStatus(data.status === "OK" ? "HEALTHY" : "DEGRADED");
      } catch (err) {
        console.error("Health check failed:", err);
        setDbStatus("DEGRADED");
      }
    }
    performHealthCheck();
    const interval = setInterval(performHealthCheck, 17777); // Check every 17s
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { name: "Bible Chat", href: "/", icon: MessageSquare },
    { name: "Sacred Art", href: "/image", icon: Image },
    { name: "Evaluation Dashboard", href: "/evaluation", icon: BarChart3 },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[#D4AF37]/25 glass-panel-premium py-4 px-6 md:px-12 flex items-center justify-between gap-4">
      {/* Brand Logo - Fixed size to prevent merging */}
      <Link href="/" className="flex items-center gap-3 group flex-shrink-0">
        <div className="p-2 bg-[#D4AF37]/15 rounded-lg border border-[#D4AF37]/35 gold-glow transition-transform group-hover:scale-105">
          <ShieldCheck className="h-6 w-6 text-[#D4AF37]" />
        </div>
        <div className="flex flex-col hidden sm:flex">
          <span className="font-serif text-2xl font-bold tracking-wider text-[#D4AF37] leading-none">
            FAITHGUIDE AI
          </span>
          <span className="text-[10px] tracking-widest text-[#F1F5F9]/50 uppercase mt-1">
            API Gateway: {API_BASE_URL}
          </span>
        </div>
      </Link>

      {/* Navigation tabs - Centered and responsive */}
      <nav className="flex items-center gap-1 md:gap-3 bg-slate-950/60 p-1 rounded-xl border border-slate-800 flex-grow justify-center max-w-lg">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-[#D4AF37] text-slate-950 font-semibold shadow-md shadow-[#D4AF37]/20"
                  : "text-slate-300 hover:text-white hover:bg-slate-900"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span className="hidden md:inline">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Connection status indicator */}
      <div className="flex items-center gap-2 bg-slate-950/80 px-3 py-2 rounded-xl border border-slate-800 flex-shrink-0">
        <Activity className="h-4 w-4 text-[#D4AF37]/75" />
        <span className="text-xs font-semibold text-slate-200">
          {dbStatus}
        </span>
      </div>
    </header>
  );
}
