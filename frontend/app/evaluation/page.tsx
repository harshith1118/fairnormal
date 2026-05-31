"use client";
import { fetchEvaluations, runEvaluationSuite } from "@/lib/api";

import { useEffect, useState, Fragment } from "react";
import { Play, Search, AlertCircle, CheckCircle, XCircle, RefreshCw, BarChart2, ShieldCheck, Database, Cpu } from "lucide-react";

interface EvalRecord {
  test_id: string;
  category: string;
  test_case: string;
  result: string;
  score: number;
  llm_response: string;
  timestamp: string;
}

export default function EvaluationPage() {
  const [records, setRecords] = useState<EvalRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [running, setRunning] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [search, setSearch] = useState<string>("");
  const [categoryFilter, setCategoryFilter] = useState<string>("All");
  const [resultFilter, setResultFilter] = useState<string>("All");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Fetch evaluations from backend
  const loadEvaluationsData = async () => {
    try {
      const data = await fetchEvaluations();
      setRecords(data.evaluations || []);
      if (typeof data.running !== 'undefined') {
          setRunning(data.running);
      }
    } catch (err) {
      console.error("Failed to load evaluations:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvaluationsData();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    // Always poll to check status, even if not explicitly "running" 
    // to catch any backend changes
    interval = setInterval(async () => {
        try {
            const data = await fetchEvaluations();
            setRecords(data.evaluations || []);
            
            // Explicitly sync local running state with backend
            const backendRunning = !!data.running;
            setRunning(backendRunning);
            if (typeof data.progress !== 'undefined') {
                setProgress(data.progress);
            }
        } catch (err) {
            console.error("Polling evaluation data failed:", err);
        }
    }, 3000); // Poll every 3s
    
    return () => clearInterval(interval);
  }, []); // Run once on mount to start the polling

  const triggerEvaluationSuite = async () => {
    // Optimistically set running to true based on backend status
    setRunning(true);
    try {
      // Runs real-time evaluation suite (POST call)
      await runEvaluationSuite();
      // Polling will handle turning off the running state
    } catch (err) {
      console.error("Evaluation run failed:", err);
      // If the POST request itself fails (e.g., 400), set running to false immediately
      setRunning(false);
    }
  };

  // Calculations
  const totalCases = records.length;
  const passedCases = records.filter((r) => r.result === "PASS").length;
  const passRate = totalCases > 0 ? ((passedCases / totalCases) * 100).toFixed(1) : "0.0";
  
  // Specific group statistics
  const getCategoryStats = (categoryName: string) => {
    const group = records.filter((r) => r.category === categoryName);
    const total = group.length;
    const passed = group.filter((r) => r.result === "PASS").length;
    const rate = total > 0 ? ((passed / total) * 100).toFixed(0) : "0";
    return { total, passed, rate: parseInt(rate) };
  };

  const scriptureStats = getCategoryStats("Scripture Questions");
  const theologyStats = getCategoryStats("Theology Questions");
  const denomStats = getCategoryStats("Denomination Questions");
  const hallucinationStats = getCategoryStats("Hallucination Tests");
  
  // Safety stats: combine adversarial, safety, and image safety
  const safetyCases = records.filter((r) => 
    r.category === "Adversarial Tests" || 
    r.category === "Safety Tests" || 
    r.category === "Image Safety Tests"
  );
  const passedSafety = safetyCases.filter((r) => r.result === "PASS").length;
  const safetyRecall = safetyCases.length > 0 ? ((passedSafety / safetyCases.length) * 100).toFixed(0) : "0";

  // Filtered records
  const filteredRecords = records.filter((r) => {
    const matchesSearch = r.test_case.toLowerCase().includes(search.toLowerCase()) || 
                          r.test_id.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = categoryFilter === "All" || r.category === categoryFilter;
    const matchesResult = resultFilter === "All" || r.result === resultFilter;
    return matchesSearch && matchesCategory && matchesResult;
  });

  const categories = [
    "Scripture Questions",
    "Theology Questions",
    "Denomination Questions",
    "Hallucination Tests",
    "Adversarial Tests",
    "Safety Tests",
    "Image Safety Tests"
  ];

  return (
    <div className="w-full flex-1 flex flex-col p-6 md:p-12 gap-8 bg-[#0B0F19]">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-col gap-2">
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-white tracking-wide">
            Model Evaluation Dashboard
          </h1>
          <p className="text-sm text-slate-400">
            Automated guardrails and accuracy metric audits across our 80-case Christianity test dataset.
          </p>
        </div>
        
        <button
          onClick={triggerEvaluationSuite}
          disabled={running || loading}
          className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-[#D4AF37] hover:bg-[#A87C11] text-slate-950 font-bold tracking-wide shadow-lg shadow-[#D4AF37]/15 disabled:opacity-40 transition-all self-start md:self-auto"
        >
          {running ? (
            <>
              <RefreshCw className="h-4.5 w-4.5 animate-spin" />
              <span>Auditing {progress}%...</span>
            </>
          ) : (
            <>
              <Play className="h-4.5 w-4.5 fill-current" />
              <span>Re-run Evaluation Suite</span>
            </>
          )}
        </button>
      </div>

      {running && (
        <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-900">
           <div 
             className="bg-[#D4AF37] h-full transition-all duration-500 ease-out" 
             style={{ width: `${progress}%` }}
           />
        </div>
      )}

      {loading ? (
        // Loading state
        <div className="flex-1 flex flex-col items-center justify-center py-20 gap-4">
          <div className="h-10 w-10 border-4 border-[#D4AF37]/15 border-t-[#D4AF37] rounded-full animate-spin" />
          <span className="text-sm text-slate-400">Fetching evaluation logs...</span>
        </div>
      ) : (
        <>
          {/* KPI Summary Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* KPI 1 */}
            <div className="glass-panel p-6 rounded-2xl flex items-center justify-between">
              <div className="flex flex-col gap-1">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                  Overall Accuracy
                </span>
                <span className="text-3xl font-serif font-bold text-[#D4AF37]">
                  {passRate}%
                </span>
                <span className="text-[10px] text-slate-500 font-medium">
                  {passedCases} / {totalCases} Test cases passed
                </span>
              </div>
              <div className="p-3 bg-[#D4AF37]/10 rounded-xl border border-[#D4AF37]/20">
                <BarChart2 className="h-6 w-6 text-[#D4AF37]" />
              </div>
            </div>

            {/* KPI 2 */}
            <div className="glass-panel p-6 rounded-2xl flex items-center justify-between">
              <div className="flex flex-col gap-1">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                  Scripture Recall
                </span>
                <span className="text-3xl font-serif font-bold text-sky-400">
                  {scriptureStats.rate}%
                </span>
                <span className="text-[10px] text-slate-500 font-medium">
                  RAG grounding score accuracy
                </span>
              </div>
              <div className="p-3 bg-sky-500/10 rounded-xl border border-sky-500/20">
                <Database className="h-6 w-6 text-sky-400" />
              </div>
            </div>

            {/* KPI 3 */}
            <div className="glass-panel p-6 rounded-2xl flex items-center justify-between">
              <div className="flex flex-col gap-1">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                  Prompt Shield Recall
                </span>
                <span className="text-3xl font-serif font-bold text-red-400">
                  {safetyRecall}%
                </span>
                <span className="text-[10px] text-slate-500 font-medium">
                  Adversarial block rate
                </span>
              </div>
              <div className="p-3 bg-red-500/10 rounded-xl border border-red-500/20">
                <ShieldCheck className="h-6 w-6 text-red-400" />
              </div>
            </div>

            {/* KPI 4 */}
            <div className="glass-panel p-6 rounded-2xl flex items-center justify-between">
              <div className="flex flex-col gap-1">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                  Hallucination Catch
                </span>
                <span className="text-3xl font-serif font-bold text-emerald-400">
                  {hallucinationStats.rate}%
                </span>
                <span className="text-[10px] text-slate-500 font-medium">
                  Citation boundary filter effectiveness
                </span>
              </div>
              <div className="p-3 bg-emerald-500/10 rounded-xl border border-emerald-500/20">
                <Cpu className="h-6 w-6 text-emerald-400" />
              </div>
            </div>
          </div>

          {/* Graphical Analytics Section */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Category Performance Graph (Tailwind Bar Graph) */}
            <div className="lg:col-span-12 glass-panel p-6 rounded-2xl flex flex-col gap-5">
              <div className="flex flex-col">
                <h3 className="font-serif text-xl font-bold text-white mb-1">
                  Category Pass-Rate Breakdown
                </h3>
                <span className="text-xs text-slate-500">
                  Detailed safety and RAG performance across the 7 sub-modules.
                </span>
              </div>

              <div className="flex flex-col gap-4 mt-2">
                {categories.map((cat) => {
                  const stats = getCategoryStats(cat);
                  return (
                    <div key={cat} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-900 pb-3">
                      <div className="sm:w-56 flex flex-col">
                        <span className="text-xs font-semibold text-slate-200">{cat}</span>
                        <span className="text-[10px] text-slate-500">{stats.passed} passed / {stats.total} cases</span>
                      </div>
                      
                      {/* Interactive Bar */}
                      <div className="flex-1 flex items-center gap-4">
                        <div className="w-full bg-slate-950 h-5.5 rounded-lg overflow-hidden border border-slate-900 flex">
                          <div
                            style={{ width: `${stats.rate}%` }}
                            className={`h-full transition-all duration-500 flex items-center justify-end pr-2 text-[9px] font-bold text-slate-950 ${
                              stats.rate >= 90
                                ? "bg-gradient-to-r from-emerald-600 to-emerald-400"
                                : stats.rate >= 70
                                ? "bg-gradient-to-r from-yellow-600 to-yellow-400"
                                : "bg-gradient-to-r from-red-700 to-red-500"
                            }`}
                          >
                            {stats.rate > 10 && `${stats.rate}%`}
                          </div>
                        </div>
                        <span className={`text-xs font-bold w-12 text-right ${
                          stats.rate >= 90 ? "text-emerald-400" : stats.rate >= 70 ? "text-yellow-400" : "text-red-400"
                        }`}>
                          {stats.rate}%
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Test Case Log Tables & Search */}
          <div className="glass-panel rounded-2xl p-6 flex flex-col gap-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <h3 className="font-serif text-xl font-bold text-white">
                Detailed Audit Log
              </h3>
              
              {/* Filter inputs */}
              <div className="flex flex-wrap items-center gap-3">
                {/* Search */}
                <div className="relative">
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search test prompt..."
                    className="pl-9 pr-4 py-2 w-52 rounded-xl text-xs bg-slate-950/60 border border-slate-800 placeholder-slate-500 focus:outline-none focus:border-[#D4AF37]"
                  />
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-500" />
                </div>

                {/* Category filter */}
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="px-3 py-2 rounded-xl text-xs bg-slate-950/60 border border-slate-800 focus:outline-none focus:border-[#D4AF37] text-slate-300"
                >
                  <option value="All">All Categories</option>
                  {categories.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>

                {/* Result filter */}
                <select
                  value={resultFilter}
                  onChange={(e) => setResultFilter(e.target.value)}
                  className="px-3 py-2 rounded-xl text-xs bg-slate-950/60 border border-slate-800 focus:outline-none focus:border-[#D4AF37] text-slate-300"
                >
                  <option value="All">All Results</option>
                  <option value="PASS">PASS</option>
                  <option value="WARN">WARN</option>
                  <option value="FAIL">FAIL</option>
                </select>
              </div>
            </div>

            {/* Records Table */}
            <div className="overflow-x-auto border border-slate-900 rounded-xl max-h-[500px]">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-950/80 border-b border-slate-900 text-slate-400 uppercase font-semibold text-[10px] tracking-wider">
                    <th className="py-3 px-4 w-20">ID</th>
                    <th className="py-3 px-4 w-44">Category</th>
                    <th className="py-3 px-4">Test Case Prompt</th>
                    <th className="py-3 px-4 w-24">Result</th>
                    <th className="py-3 px-4 w-20 text-right">Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-900/60">
                  {filteredRecords.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-slate-500 font-medium">
                        No evaluations matching the filter criteria were found.
                      </td>
                    </tr>
                  ) : (
                    filteredRecords.map((rec) => {
                      const isExpanded = expandedId === rec.test_id;
                      return (
                        <Fragment key={rec.test_id}>
                          <tr
                            onClick={() => setExpandedId(isExpanded ? null : rec.test_id)}
                            className="hover:bg-slate-900/35 cursor-pointer transition-all"
                          >
                            <td className="py-3 px-4 font-mono text-slate-400 font-semibold">{rec.test_id}</td>
                            <td className="py-3 px-4 text-[#D4AF37]/85 font-medium">{rec.category}</td>
                            <td className="py-3 px-4 text-slate-300 font-medium max-w-xs truncate">{rec.test_case}</td>
                            <td className="py-3 px-4">
                              <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[9px] font-bold ${
                                rec.result === "PASS"
                                  ? "bg-green-950/20 text-green-400 border border-green-500/20"
                                  : rec.result === "WARN"
                                  ? "bg-yellow-950/20 text-yellow-400 border border-yellow-500/20"
                                  : "bg-red-950/20 text-red-400 border border-red-500/20"
                              }`}>
                                {rec.result === "PASS" ? (
                                  <CheckCircle className="h-3 w-3" />
                                ) : rec.result === "WARN" ? (
                                  <AlertCircle className="h-3 w-3" />
                                ) : (
                                  <XCircle className="h-3 w-3" />
                                )}
                                <span>{rec.result}</span>
                              </span>
                            </td>
                            <td className="py-3 px-4 text-right font-bold text-slate-200">{rec.score}</td>
                          </tr>
                          {isExpanded && (
                            <tr className="bg-slate-950/40">
                              <td colSpan={5} className="py-4 px-6 border-b border-slate-900">
                                <div className="flex flex-col gap-3">
                                  <div className="flex flex-col gap-0.5">
                                    <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                                      Complete Prompt Case
                                    </span>
                                    <p className="text-slate-300 font-medium select-text">{rec.test_case}</p>
                                  </div>
                                  <div className="flex flex-col gap-0.5">
                                    <span className="text-[10px] uppercase font-bold text-[#D4AF37] tracking-wider">
                                      Actual LLM Response Sanitized
                                    </span>
                                    <div className="p-4 rounded-xl border border-slate-800 bg-slate-950 text-slate-300 whitespace-pre-line leading-relaxed text-xs md:text-sm font-normal max-h-60 overflow-y-auto select-text">
                                      {rec.llm_response || "No response generated."}
                                    </div>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </Fragment>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
