"use client";

import { useState } from "react";
import { CheckCircle2, AlertTriangle, ChevronDown, ChevronUp, Book } from "lucide-react";

interface Citation {
  reference: string;
  text: string;
  verified: boolean;
}

interface CitationViewerProps {
  citations: Citation[];
}

export default function CitationViewer({ citations }: CitationViewerProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="w-full flex flex-col gap-2 mt-4 pt-3 border-t border-[#D4AF37]/15">
      <div className="flex items-center gap-2">
        <Book className="h-4.5 w-4.5 text-[#D4AF37]" />
        <span className="text-xs font-serif italic text-slate-300 font-medium">
          Scriptural References:
        </span>
      </div>

      <div className="flex flex-wrap gap-2">
        {citations.map((cite, index) => {
          const isExpanded = expandedIndex === index;
          return (
            <div key={index} className="flex flex-col">
              {cite.verified ? (
                // VERIFIED CITATION
                <button
                  onClick={() => setExpandedIndex(isExpanded ? null : index)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    isExpanded
                      ? "bg-[#D4AF37] text-slate-950 border-[#D4AF37] font-semibold"
                      : "bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/35 hover:bg-[#D4AF37]/20"
                  }`}
                >
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  <span>{cite.reference}</span>
                  {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                </button>
              ) : (
                // UNVERIFIED / FAKE CITATION
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border bg-red-950/30 text-red-400 border-red-500/35">
                  <AlertTriangle className="h-3.5 w-3.5 animate-pulse" />
                  <span>{cite.reference} (Unverified)</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Accordion content area: Scripture parchment container */}
      {expandedIndex !== null && citations[expandedIndex] && (
        <div className="w-full mt-2 fade-in">
          <div className="relative p-5 rounded-xl border border-amber-900/30 bg-[#FDFBF7] text-slate-900 shadow-lg font-serif">
            {/* Aesthetic paper lines/accents */}
            <div className="absolute top-0 bottom-0 left-3 w-0.5 bg-red-800/10 border-l border-r border-red-800/5" />
            <div className="pl-6 select-text">
              <div className="flex items-center justify-between border-b border-amber-900/10 pb-2 mb-3">
                <span className="font-bold text-base text-amber-900 tracking-wide font-serif">
                  {citations[expandedIndex].reference}
                </span>
                <span className="text-[10px] uppercase font-sans tracking-widest text-slate-500 font-semibold">
                  Verified Canon Text
                </span>
              </div>
              <p className="text-base italic leading-relaxed text-slate-800 text-justify pr-2">
                &ldquo;{citations[expandedIndex].text}&rdquo;
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
