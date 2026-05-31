"use client";

import { useState, useEffect, useRef } from "react";
import { Send, Plus, MessageSquare, ShieldAlert, Sparkles, BookOpen, Scroll, HelpCircle } from "lucide-react";
import DenominationSelector from "./DenominationSelector";
import CitationViewer from "./CitationViewer";
import { fetchHistory, sendChatMessage } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  message: string;
  citations?: any[];
  safety_status?: string;
  safety_reason?: string;
  timestamp?: string;
}

export default function ChatInterface() {
  const [sessionId, setSessionId] = useState<string>("default-session");
  const [sessions, setSessions] = useState<string[]>(["default-session"]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [activeDenomination, setActiveDenomination] = useState<string>("Protestant");
  const [mounted, setMounted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load state from localStorage after mounting
  useEffect(() => {
    const savedSessionId = localStorage.getItem("currentSessionId");
    const savedSessions = localStorage.getItem("sessionsList");
    if (savedSessionId) setSessionId(savedSessionId);
    if (savedSessions) setSessions(JSON.parse(savedSessions));
    setMounted(true);
  }, []);

  // Sync sessionId and sessions to localStorage
  useEffect(() => {
    if (!mounted) return;
    localStorage.setItem("currentSessionId", sessionId);
    localStorage.setItem("sessionsList", JSON.stringify(sessions));
  }, [sessionId, sessions, mounted]);

  // Suggested queries
  const templates = [
    { label: "What happens after death?", category: "Theology" },
    { label: "Ground of James 2:14-26", category: "Scripture" },
    { label: "Compare views on Grace vs Works", category: "Denominations" },
    { label: "Generate a daily Devotional", category: "Content" }
  ];

  // Scroll to bottom on new messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load history when sessionId changes
  useEffect(() => {
    // Only load if a session is actively selected. 
    // The createNewSession already clears messages, so we don't need to do it here.
    
    async function loadHistory() {
      try {
        const data = await fetchHistory(sessionId);
        const history: Message[] = (data.history || []).map(msg => ({
          ...msg,
          role: msg.role === "assistant" ? "assistant" : "user"
        }));
        setMessages(history);
      } catch (err) {
        console.error("Failed to load chat history:", err);
        setMessages([]);
      }
    }
    loadHistory();
  }, [sessionId]);

  const handleSend = async (text: string) => {
    if (!text.trim() || loading) return;
    
    const userMsg = text.trim();
    setInput("");
    setLoading(true);

    // Optimistically add user message
    setMessages((prev) => [...prev, { role: "user", message: userMsg }]);

    try {
      const data = await sendChatMessage(sessionId, userMsg);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          message: data.message,
          citations: data.citations || [],
          safety_status: data.safety_status,
          safety_reason: data.safety_reason
        }
      ]);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "API error";
      console.error("Chat send error:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          message: `Unable to complete request: ${errorMsg}`,
          safety_status: "REFUSE",
          safety_reason: "API Connection Loss"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const createNewSession = () => {
    const newId = `session-${Date.now().toString().slice(-6)}`;
    setSessions((prev) => [newId, ...prev]);
    setSessionId(newId);
    setMessages([]);
  };

  return (
    <div className="w-full flex-1 flex flex-col md:flex-row h-[calc(100vh-80px)] overflow-hidden">
      {/* Sessions Sidebar */}
      <aside className="w-full md:w-64 border-r border-[#D4AF37]/15 bg-slate-950/60 p-4 flex flex-col gap-4">
        <button
          onClick={createNewSession}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-[#D4AF37]/35 bg-[#D4AF37]/5 hover:bg-[#D4AF37]/15 text-[#D4AF37] text-sm font-semibold transition-all"
        >
          <Plus className="h-4 w-4" />
          <span>New RAG Session</span>
        </button>

        <div className="flex-1 overflow-y-auto flex flex-col gap-2">
          <div className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold mt-2 px-2">
            Active Study Logs
          </div>
...
          {mounted ? (
            sessions.map((id) => (
              <button
                key={id}
                onClick={() => setSessionId(id)}
                className={`flex items-center gap-3 px-3 py-3 rounded-xl text-left text-sm transition-all ${
                  sessionId === id
                    ? "bg-slate-900 border border-[#D4AF37]/30 text-white font-medium"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
                }`}
              >
                <MessageSquare className={`h-4.5 w-4.5 ${sessionId === id ? "text-[#D4AF37]" : "text-slate-500"}`} />
                <span className="truncate">
                  {id === "default-session" ? "Primary Study" : `Study ${id.slice(-4)}`}
                </span>
              </button>
            ))
          ) : (
            <button
              key="default-session"
              className="flex items-center gap-3 px-3 py-3 rounded-xl text-left text-sm text-slate-400"
            >
              <MessageSquare className="h-4.5 w-4.5 text-slate-500" />
              <span className="truncate">Primary Study</span>
            </button>
          )}
        </div>
      </aside>

      {/* Main Workspace Area */}
      <main className="flex-1 flex flex-col bg-[#0B0F19] overflow-hidden">
        {/* Active Denomination Filter Settings Header */}
        <div className="p-4 border-b border-[#D4AF37]/10 glass-panel">
          <DenominationSelector sessionId={sessionId} onSelect={setActiveDenomination} />
        </div>

        {/* Chat Logs Window */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6 scrollbar">
          {messages.length === 0 ? (
            // Landing state if chat is fresh
            <div className="flex-1 flex flex-col items-center justify-center text-center max-w-xl mx-auto py-12">
              <div className="p-4 bg-[#D4AF37]/10 rounded-full border border-[#D4AF37]/30 gold-glow mb-6">
                <Scroll className="h-10 w-10 text-[#D4AF37]" />
              </div>
              <h1 className="font-serif text-3xl font-bold text-white mb-3">
                FaithGuide Theological Assistant
              </h1>
              <p className="text-sm text-slate-400 leading-relaxed mb-8">
                Welcome to a secure scripture chat workspace. Enter any question regarding scripture, 
                theology, sermons, or church history. The system will retrieve validated canonical texts 
                and flag potential theological hallucinations.
              </p>

              {/* Suggestions Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full">
                {templates.map((tpl, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(tpl.label)}
                    className="flex flex-col items-start p-4 rounded-xl border border-slate-800 bg-slate-950/40 hover:border-[#D4AF37]/30 text-left transition-all group"
                  >
                    <span className="text-[10px] tracking-widest text-[#D4AF37] uppercase font-semibold mb-1">
                      {tpl.category}
                    </span>
                    <span className="text-sm text-slate-200 group-hover:text-white">
                      {tpl.label} &rarr;
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            // Chat message entries
            messages.map((msg, index) => {
              const isAssistant = msg.role === "assistant";
              const isRefused = msg.safety_status === "REFUSE";
              const isWarning = msg.safety_status === "WARN";
              // Use timestamp if available as part of the key
              const messageKey = `${msg.timestamp || index}-${msg.role}`;
              
              return (
                <div
                  key={messageKey}
                  className={`flex flex-col gap-2 max-w-3xl w-full fade-in ${
                    isAssistant ? "self-start" : "self-end items-end"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-semibold tracking-wider uppercase ${isAssistant ? "text-[#D4AF37]" : "text-sky-400"}`}>
                      {isAssistant ? `FaithGuide AI (${activeDenomination})` : "Researcher"}
                    </span>
                  </div>

                  <div
                    className={`p-5 rounded-2xl border text-sm leading-relaxed ${
                      !isAssistant
                        ? "bg-slate-900 border-slate-800 text-slate-100"
                        : isRefused
                        ? "bg-red-950/20 border-red-500/35 text-red-300"
                        : isWarning
                        ? "bg-yellow-950/15 border-yellow-500/30 text-slate-200"
                        : "bg-slate-950/50 border-[#D4AF37]/15 text-slate-200"
                    }`}
                  >
                    {/* Safety Alert Badge */}
                    {isRefused && (
                      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-red-500/20 text-xs font-semibold text-red-400">
                        <ShieldAlert className="h-4 w-4" />
                        <span>PROMPT SHIELD TRIGGERED (REFUSE)</span>
                      </div>
                    )}
                    {isWarning && (
                      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-yellow-500/20 text-xs font-semibold text-yellow-400">
                        <ShieldAlert className="h-4 w-4" />
                        <span>THEOLOGICAL SENSITIVITY ADVISORY (WARN)</span>
                      </div>
                    )}

                    {/* Chat Text */}
                    <div className="whitespace-pre-line text-sm md:text-base leading-relaxed pr-1 select-text">
                      {msg.message}
                    </div>

                    {/* Citation Badges */}
                    {isAssistant && msg.citations && msg.citations.length > 0 && (
                      <CitationViewer citations={msg.citations} />
                    )}
                  </div>
                </div>
              );
            })
          )}

          {/* Shimmering Loading State */}
          {loading && (
            <div className="flex flex-col gap-2 max-w-xl w-full self-start">
              <span className="text-[10px] font-semibold text-[#D4AF37] tracking-wider uppercase">
                Searching scriptures...
              </span>
              <div className="p-5 rounded-2xl border border-[#D4AF37]/10 bg-slate-950/50 flex flex-col gap-3">
                <div className="h-4 w-1/3 rounded shimmer" />
                <div className="h-4 w-3/4 rounded shimmer" />
                <div className="h-4 w-1/2 rounded shimmer" />
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-900 glass-panel-premium">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(input);
            }}
            className="flex items-center gap-2 max-w-4xl mx-auto w-full relative"
          >
            <input
              type="text"
              disabled={loading}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about scriptures, theology, write sermons or compare beliefs..."
              className="flex-1 py-4.5 pl-6 pr-14 rounded-2xl glass-input text-slate-100 text-sm md:text-base placeholder-slate-500 shadow-inner"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 p-2.5 rounded-xl bg-[#D4AF37] hover:bg-[#A87C11] text-slate-950 font-semibold shadow-md shadow-[#D4AF37]/10 disabled:opacity-40 disabled:hover:bg-[#D4AF37] transition-all"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
