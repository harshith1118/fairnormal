"use client";

import { useState, useEffect } from "react";
import { BookOpen, Shield, Flame, BookCheck, AlertCircle } from "lucide-react";
import { savePreference, fetchHistory, checkHealth } from "@/lib/api";

interface DenominationSelectorProps {
  sessionId: string;
  onSelect: (denomination: string) => void;
}

export default function DenominationSelector({ sessionId, onSelect }: DenominationSelectorProps) {
  const [selected, setSelected] = useState<string>("Protestant");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [backendReady, setBackendReady] = useState<boolean>(true);

  const denominations = [
    {
      name: "Protestant",
      icon: BookOpen,
      desc: "66-book canon. Primacy of scripture alone (Sola Scriptura) and salvation by grace alone.",
      color: "border-sky-500/35 text-sky-400"
    },
    {
      name: "Catholic",
      icon: Shield,
      desc: "73-book canon. Retains Deuterocanon. Values both Scripture and Sacred Tradition.",
      color: "border-[#D4AF37]/35 text-[#D4AF37]"
    },
    {
      name: "Orthodox",
      icon: Flame,
      desc: "76+ book canon. Emphasizes liturgical beauty, historical councils, and theosis (union with God).",
      color: "border-emerald-500/35 text-emerald-400"
    }
  ];

  // Verify backend is running and load session data on mount
  useEffect(() => {
    async function initializeSession() {
      try {
        // Check backend health first
        await checkHealth();
        setBackendReady(true);
        
        // Try to load session history
        try {
          await fetchHistory(sessionId);
        } catch (histErr) {
          // History fetch failure is not critical; session might be new
          console.warn("Could not fetch history:", histErr);
        }
        
        // Initialize with default denomination
        await handleSelect("Protestant");
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Backend is not reachable";
        console.error("Backend initialization error:", errorMsg);
        setError(errorMsg);
        setBackendReady(false);
      }
    }
    
    initializeSession();
  }, [sessionId]);

  const handleSelect = async (denom: string) => {
    setLoading(true);
    setError(null);
    
    try {
      await savePreference(sessionId, denom);
      setSelected(denom);
      onSelect(denom);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to save preference";
      console.error("Preference save error:", errorMsg);
      setError(errorMsg);
      setBackendReady(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <BookCheck className="h-4.5 w-4.5 text-[#D4AF37]" />
        <span className="text-xs tracking-widest text-[#D4AF37] font-semibold uppercase">
          Active Theological Scope
        </span>
      </div>
      
      {error && (
        <div className="flex items-start gap-2 p-3 rounded-lg bg-red-950/40 border border-red-800/50">
          <AlertCircle className="h-4 w-4 text-red-400 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm text-red-300">{error}</p>
            <p className="text-xs text-red-400/70 mt-1">
              Make sure the backend server is running at http://localhost:8000
            </p>
          </div>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 w-full">
        {denominations.map((denom) => {
          const Icon = denom.icon;
          const isSelected = selected === denom.name;
          return (
            <button
              key={denom.name}
              disabled={loading || !backendReady}
              onClick={() => handleSelect(denom.name)}
              className={`flex flex-col items-start gap-2 p-4 rounded-xl border text-left transition-all ${
                isSelected
                  ? "bg-slate-900 border-[#D4AF37] shadow-[0_0_12px_rgba(212,175,55,0.15)] scale-[1.01]"
                  : "bg-slate-950/40 border-slate-800 hover:border-slate-700"
              } ${!backendReady ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              <div className="flex items-center gap-2">
                <Icon className={`h-5 w-5 ${isSelected ? "text-[#D4AF37]" : "text-slate-400"}`} />
                <span className={`font-serif text-base font-bold ${isSelected ? "text-[#D4AF37]" : "text-slate-200"}`}>
                  {denom.name}
                </span>
                {isSelected && (
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#D4AF37]/15 text-[#D4AF37]">
                    ACTIVE
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-normal">
                {denom.desc}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
