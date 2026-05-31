"use client";
import { generateImage } from "@/lib/api";

import { useState } from "react";
import { Sparkles, Download, Image as ImageIcon, ShieldAlert, Layers, Play } from "lucide-react";

interface SavedArt {
  prompt: string;
  style: string;
  enhancedPrompt: string;
  base64: string;
}

export default function ImagePage() {
  const [prompt, setPrompt] = useState<string>("");
  const [style, setStyle] = useState<string>("oil painting");
  const [enhance, setEnhance] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  
  const [currentImage, setCurrentImage] = useState<string | null>(null);
  const [enhancedPrompt, setEnhancedPrompt] = useState<string>("");
  const [safetyStatus, setSafetyStatus] = useState<string>("ALLOW");
  const [safetyReason, setSafetyReason] = useState<string | null>(null);
  
  const [gallery, setGallery] = useState<SavedArt[]>([]);

  const artStyles = [
    { name: "oil painting", label: "Oil Painting", desc: "Classic textures, deep shadows, and rich details" },
    { name: "stained glass", label: "Stained Glass", desc: "Vibrant backlit colors and bold lead contours" },
    { name: "iconography", label: "Orthodox Iconography", desc: "Gold gilding, flat perspective, and theological forms" },
    { name: "fresco", label: "Renaissance Fresco", desc: "Soft plaster textures, classical balance, and historical depth" },
    { name: "digital", label: "Digital Artwork", desc: "Sleek lighting, modern fantasy proportions, and high contrast" }
  ];

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || loading) return;

    setLoading(true);
    setCurrentImage(null);
    setSafetyStatus("ALLOW");
    setSafetyReason(null);

    try {
      const data = await generateImage(prompt, style, enhance);
      setSafetyStatus(data.safety_status);
      setEnhancedPrompt(data.enhanced_prompt);
      
      if (data.safety_status === "REFUSE") {
        setSafetyReason(data.safety_reason);
      } else if (data.base64_image) {
        setCurrentImage(data.base64_image);
        // Add to gallery
        const newArt: SavedArt = {
          prompt: prompt.trim(),
          style: style,
          enhancedPrompt: data.enhanced_prompt,
          base64: data.base64_image
        };
        setGallery((prev) => [newArt, ...prev]);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Image generation failed";
      console.error("Image generation error:", err);
      
      if (errorMsg.includes("status 429")) {
        setSafetyStatus("REFUSE");
        setSafetyReason("AI service quota exceeded. Please try again in a few minutes.");
      } else {
        setSafetyStatus("REFUSE");
        setSafetyReason(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full flex-1 flex flex-col p-6 md:p-12 gap-8 bg-[#0B0F19]">
      <div className="flex flex-col gap-2 max-w-2xl">
        <h1 className="font-serif text-3xl md:text-4xl font-bold text-white tracking-wide">
          Christian Sacred Art Canvas
        </h1>
        <p className="text-sm md:text-base text-slate-400 leading-relaxed">
          Create majestic scripture scenes and faith illustrations powered by Gemini Imagen 3. 
          Use the AI Enhancer to expand your inputs into breathtaking masterpieces.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Settings Form - Left column (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6 glass-panel p-6 rounded-2xl">
          <form onSubmit={handleGenerate} className="flex flex-col gap-5">
            {/* Prompt input */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                Artwork Prompt
              </label>
              <textarea
                required
                rows={3}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe a biblically inspired scene, e.g., 'Daniel in the lions den' or 'Noah looking at the rainbow'..."
                className="w-full p-4 rounded-xl glass-input text-slate-100 text-sm placeholder-slate-500"
              />
            </div>

            {/* AI Prompt Enhancer Toggle */}
            <div className="flex items-center justify-between p-3.5 bg-slate-900/60 rounded-xl border border-slate-800">
              <div className="flex flex-col gap-0.5">
                <span className="text-sm font-semibold text-[#D4AF37] flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4 text-[#D4AF37]" />
                  AI Prompt Enhancer
                </span>
                <span className="text-[11px] text-slate-400">
                  Auto-expand prompts with artistic details
                </span>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={enhance}
                  onChange={(e) => setEnhance(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-400 after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#D4AF37] peer-checked:after:bg-slate-950" />
              </label>
            </div>

            {/* Art styles selection */}
            <div className="flex flex-col gap-3">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                Select Art Style
              </label>
              <div className="flex flex-col gap-2 max-h-56 overflow-y-auto pr-1">
                {artStyles.map((item) => (
                  <button
                    key={item.name}
                    type="button"
                    onClick={() => setStyle(item.name)}
                    className={`flex items-center gap-3 p-3 rounded-xl border text-left transition-all ${
                      style === item.name
                        ? "bg-[#D4AF37]/10 border-[#D4AF37] text-white"
                        : "bg-slate-950/20 border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    <Layers className={`h-4.5 w-4.5 ${style === item.name ? "text-[#D4AF37]" : "text-slate-500"}`} />
                    <div className="flex flex-col">
                      <span className={`text-sm font-semibold ${style === item.name ? "text-white" : "text-slate-300"}`}>
                        {item.label}
                      </span>
                      <span className="text-[10px] text-slate-500">{item.desc}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Generate Button */}
            <button
              type="submit"
              disabled={loading || !prompt.trim()}
              className="w-full flex items-center justify-center gap-2 py-4 rounded-xl bg-[#D4AF37] hover:bg-[#A87C11] text-slate-950 font-bold tracking-wide shadow-lg shadow-[#D4AF37]/10 disabled:opacity-40 transition-all mt-2"
            >
              {loading ? (
                <>
                  <div className="h-4 w-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                  <span>Painting masterpiece...</span>
                </>
              ) : (
                <>
                  <Play className="h-4.5 w-4.5 fill-current" />
                  <span>Generate Artwork</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* View Canvas - Right column (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          {/* Main preview frame */}
          <div className="aspect-square w-full rounded-2xl border border-slate-800 bg-slate-950/40 overflow-hidden flex flex-col items-center justify-center relative shadow-2xl relative min-h-[400px]">
            {loading ? (
              // Loading display
              <div className="flex flex-col items-center gap-4 text-center p-6">
                <div className="relative h-20 w-20 flex items-center justify-center">
                  <div className="absolute inset-0 border-4 border-[#D4AF37]/15 rounded-full" />
                  <div className="absolute inset-0 border-4 border-t-[#D4AF37] rounded-full animate-spin" />
                  <ImageIcon className="h-8 w-8 text-[#D4AF37]" />
                </div>
                <div className="flex flex-col">
                  <span className="font-serif text-lg font-bold text-slate-200">
                    Invoking Gemini Imagen 3
                  </span>
                  <span className="text-xs text-slate-500 mt-1 max-w-xs leading-normal">
                    Fusing color layers and divine light. This can take a few seconds...
                  </span>
                </div>
              </div>
            ) : safetyStatus === "REFUSE" ? (
              // Safety gate refusal block
              <div className="p-8 text-center max-w-md flex flex-col items-center gap-4">
                <div className="p-4 bg-red-950/30 rounded-full border border-red-500/35 text-red-400">
                  <ShieldAlert className="h-10 w-10 animate-bounce" />
                </div>
                <h3 className="font-serif text-xl font-bold text-red-400">
                  Prompt Shield Triggered
                </h3>
                <p className="text-sm text-slate-400 leading-normal">
                  {safetyReason || "The request violated the image safety guidelines regarding violent, explicit, or doctrinally manipulative content."}
                </p>
              </div>
            ) : currentImage ? (
              // Render image
              <div className="w-full h-full relative group">
                <img
                  src={currentImage}
                  alt={prompt}
                  className="w-full h-full object-cover select-none"
                />
                
                {/* Download hover overlay */}
                <div className="absolute inset-0 bg-slate-950/80 opacity-0 group-hover:opacity-100 flex flex-col items-center justify-center p-6 text-center transition-all">
                  <p className="font-serif text-lg font-bold text-[#D4AF37] mb-2">{prompt}</p>
                  <p className="text-xs text-slate-400 max-w-sm mb-6 line-clamp-3 italic">
                    &ldquo;{enhancedPrompt}&rdquo;
                  </p>
                  <a
                    href={currentImage}
                    download={`faithguide_${prompt.toLowerCase().replace(/\s+/g, "_")}.png`}
                    className="flex items-center gap-2 px-5 py-2.5 bg-[#D4AF37] text-slate-950 text-sm font-bold rounded-xl shadow-lg transition-transform hover:scale-105"
                  >
                    <Download className="h-4 w-4" />
                    <span>Download Canvas</span>
                  </a>
                </div>
              </div>
            ) : (
              // Standby default state
              <div className="text-center p-8 flex flex-col items-center gap-3">
                <ImageIcon className="h-12 w-12 text-slate-700 mb-2" />
                <span className="font-serif text-lg font-bold text-slate-500">
                  Canvas Empty
                </span>
                <span className="text-xs text-slate-600 max-w-xs">
                  Fill in the details on the left to paint your theological concept.
                </span>
              </div>
            )}
          </div>

          {/* Enhanced prompt text display */}
          {currentImage && !loading && (
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col gap-2">
              <span className="text-[10px] tracking-widest text-[#D4AF37] uppercase font-bold">
                Enhanced Prompt Details
              </span>
              <p className="text-xs text-slate-400 italic leading-relaxed select-text">
                &ldquo;{enhancedPrompt}&rdquo;
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Gallery Section */}
      {gallery.length > 0 && (
        <div className="w-full flex flex-col gap-4 mt-8">
          <h2 className="font-serif text-2xl font-bold text-white">
            Art Gallery History
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {gallery.map((art, idx) => (
              <div key={idx} className="flex flex-col bg-slate-950/60 rounded-2xl border border-slate-800 overflow-hidden group">
                <div className="aspect-square relative w-full overflow-hidden bg-slate-900">
                  <img
                    src={art.base64}
                    alt={art.prompt}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-slate-950/80 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-all">
                    <a
                      href={art.base64}
                      download={`gallery_${idx}.png`}
                      className="p-3 bg-[#D4AF37] text-slate-950 rounded-xl shadow-lg"
                    >
                      <Download className="h-5 w-5" />
                    </a>
                  </div>
                </div>
                <div className="p-4 flex flex-col gap-1.5">
                  <span className="text-[9px] tracking-widest text-[#D4AF37] uppercase font-bold">
                    {art.style}
                  </span>
                  <p className="text-sm font-semibold text-slate-200 truncate">{art.prompt}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
