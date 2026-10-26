"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldAlert,
  Bot,
  UserCheck,
  Building2,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Search,
  Filter,
  Send,
  Sparkles,
  RefreshCw,
  LogOut,
  LogIn,
  Layers,
  FileText,
  Activity,
  Lock,
  User,
  ShieldCheck,
  ChevronRight,
  Sun,
  Moon,
  Zap,
  TrendingUp,
  Cpu
} from "lucide-react";

const API_BASE = "http://127.0.0.1:8000/api";

interface Complaint {
  id: number;
  complaint: string;
  category: string;
  priority: "High" | "Medium" | "Low";
  department: string;
  status: "Pending" | "In Progress" | "Resolved";
  created_at: string;
}

interface AnalyticsStats {
  total: number;
  pending: number;
  in_progress: number;
  resolved: number;
  top_categories: { category: string; count: number }[];
  priority_breakdown: { [key: string]: number };
}

export default function Home() {
  // Theme State ("dark" | "light")
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  // Authentication State (Default: NOT logged in)
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [role, setRole] = useState<"user" | "admin" | null>(null);
  const [currentUsername, setCurrentUsername] = useState<string>("");

  // Login Form State
  const [loginUsername, setLoginUsername] = useState("user");
  const [loginPassword, setLoginPassword] = useState("user123");
  const [loginRoleTab, setLoginRoleTab] = useState<"user" | "admin">("user");
  const [loginError, setLoginError] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);

  // App Data State
  const [complaintInput, setComplaintInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastPrediction, setLastPrediction] = useState<Complaint | null>(null);

  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [stats, setStats] = useState<AnalyticsStats | null>(null);
  const [loadingComplaints, setLoadingComplaints] = useState(false);
  const [backendOnline, setBackendOnline] = useState(true);

  // Admin Filters
  const [statusFilter, setStatusFilter] = useState("All");
  const [priorityFilter, setPriorityFilter] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");

  // Toggle Theme
  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  // Sync theme to root html and body elements
  useEffect(() => {
    if (theme === "light") {
      document.documentElement.classList.add("theme-light");
      document.body.classList.add("theme-light");
    } else {
      document.documentElement.classList.remove("theme-light");
      document.body.classList.remove("theme-light");
    }
  }, [theme]);

  // Fetch Data from FastAPI Backend
  const fetchData = async () => {
    setLoadingComplaints(true);
    try {
      const resComplaints = await fetch(`${API_BASE}/complaints`);
      if (resComplaints.ok) {
        const data = await resComplaints.json();
        setComplaints(data);
        setBackendOnline(true);
      } else {
        setBackendOnline(false);
      }

      const resStats = await fetch(`${API_BASE}/stats`);
      if (resStats.ok) {
        const statsData = await resStats.json();
        setStats(statsData);
      }
    } catch (err) {
      console.error("Error connecting to API:", err);
      setBackendOnline(false);
    } finally {
      setLoadingComplaints(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 8000);
    return () => clearInterval(interval);
  }, []);

  // Handle Login Submission
  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError("");
    setLoginLoading(true);

    try {
      const res = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: loginUsername, password: loginPassword }),
      });

      if (res.ok) {
        const data = await res.json();
        setIsLoggedIn(true);
        setRole(data.role);
        setCurrentUsername(data.username);
        fetchData();
      } else {
        setLoginError("Invalid username or password. Check credentials.");
      }
    } catch (err) {
      setLoginError("Cannot connect to backend server. Ensure FastAPI is running.");
    } finally {
      setLoginLoading(false);
    }
  };

  // Logout Handler
  const handleLogout = () => {
    setIsLoggedIn(false);
    setRole(null);
    setCurrentUsername("");
    setLastPrediction(null);
  };

  // Quick Role Tab Switch
  const selectQuickRole = (targetRole: "user" | "admin") => {
    setLoginRoleTab(targetRole);
    if (targetRole === "user") {
      setLoginUsername("user");
      setLoginPassword("user123");
    } else {
      setLoginUsername("admin");
      setLoginPassword("admin123");
    }
    setLoginError("");
  };

  // Submit New Complaint
  const handleSubmitComplaint = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!complaintInput.trim()) return;

    setIsSubmitting(true);
    setLastPrediction(null);

    try {
      const res = await fetch(`${API_BASE}/complaints`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ complaint: complaintInput }),
      });

      if (res.ok) {
        const data = await res.json();
        setLastPrediction(data);
        setComplaintInput("");
        fetchData();
      } else {
        alert("Failed to submit complaint.");
      }
    } catch (err) {
      alert("Error connecting to backend server.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Update Status
  const handleUpdateStatus = async (id: number, newStatus: string) => {
    try {
      const res = await fetch(`${API_BASE}/complaints/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });

      if (res.ok) {
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Fill sample complaint text
  const fillSampleText = (text: string) => {
    setComplaintInput(text);
  };

  // Filtered Complaints for Admin
  const filteredComplaints = complaints.filter((c) => {
    const matchesStatus = statusFilter === "All" || c.status === statusFilter;
    const matchesPriority = priorityFilter === "All" || c.priority === priorityFilter;
    const matchesSearch =
      c.complaint.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.id.toString().includes(searchQuery);

    return matchesStatus && matchesPriority && matchesSearch;
  });

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "High":
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-rose-500/15 text-rose-500 border border-rose-500/30 flex items-center gap-1.5"><ShieldAlert className="w-3.5 h-3.5 animate-bounce" /> HIGH PRIORITY</span>;
      case "Medium":
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30 flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5" /> MEDIUM</span>;
      default:
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5"><FileText className="w-3.5 h-3.5" /> LOW</span>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "Pending":
        return <span className="px-3 py-1 rounded-full text-xs font-semibold bg-yellow-500/15 text-amber-700 dark:text-yellow-300 border border-yellow-500/30">Pending</span>;
      case "In Progress":
        return <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/15 text-blue-700 dark:text-blue-300 border border-blue-500/30">In Progress</span>;
      case "Resolved":
        return <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30">Resolved</span>;
      default:
        return null;
    }
  };

  const isDark = theme === "dark";

  return (
    <div className={`min-h-screen flex flex-col font-sans transition-colors duration-300 relative overflow-hidden ${
      isDark ? "bg-[#080c14] text-gray-100" : "theme-light bg-slate-100 text-slate-900"
    }`}>
      
      {/* AMBIENT FLOATING ANIMATED BACKGROUND ORBS */}
      <div className={`absolute top-10 left-10 w-96 h-96 rounded-full blur-3xl pointer-events-none animate-float-slow ${
        isDark ? "bg-indigo-600/15" : "bg-indigo-300/25"
      }`}></div>
      <div className={`absolute bottom-20 right-10 w-[30rem] h-[30rem] rounded-full blur-3xl pointer-events-none animate-float-reverse ${
        isDark ? "bg-purple-600/15" : "bg-purple-300/25"
      }`}></div>

      {/* Top Header Bar */}
      <header className={`px-6 sm:px-10 h-20 py-4 flex items-center justify-between border-b sticky top-0 z-50 backdrop-blur-md transition-all ${
        isDark ? "border-gray-800/80 bg-gray-950/70" : "border-slate-200/90 bg-white/90 shadow-sm"
      }`}>
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-600 text-white shadow-lg shadow-indigo-500/25">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className={`font-extrabold text-xl tracking-tight ${isDark ? "text-white" : "text-slate-900"}`}>
                Complaint Intelligence
              </span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/15 text-indigo-500 font-mono border border-indigo-500/30 font-semibold">
                v2.0 NLP
              </span>
            </div>
            <p className={`text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>
              Automated Classification & Priority Pipeline
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Backend Health Status */}
          <div className={`hidden sm:flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs border font-medium ${
            isDark ? "bg-gray-900 border-gray-800 text-gray-300" : "bg-slate-100 border-slate-300 text-slate-700"
          }`}>
            <span className={`w-2.5 h-2.5 rounded-full ${backendOnline ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`}></span>
            <span>FastAPI Server {backendOnline ? "Online (8000)" : "Offline"}</span>
          </div>

          {/* Theme Switcher Toggle Button */}
          <button
            onClick={toggleTheme}
            className={`p-2.5 rounded-xl border transition-all flex items-center gap-2 text-xs font-bold cursor-pointer ${
              isDark
                ? "bg-gray-900 border-gray-800 text-amber-400 hover:bg-gray-800 shadow-md shadow-gray-950"
                : "bg-slate-200 border-slate-300 text-indigo-700 hover:bg-slate-300 shadow-sm"
            }`}
            title={`Switch to ${isDark ? "Light" : "Dark"} Mode`}
          >
            {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-600" />}
            <span className="hidden md:inline">{isDark ? "Light Mode" : "Dark Mode"}</span>
          </button>

          {/* User Profile / Logout when logged in */}
          {isLoggedIn && (
            <div className="flex items-center gap-3">
              <div className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl border text-xs ${
                isDark ? "bg-gray-900 border-gray-800 text-white" : "bg-slate-100 border-slate-300 text-slate-900"
              }`}>
                <div className="w-6 h-6 rounded-md bg-indigo-600/20 text-indigo-500 font-bold flex items-center justify-center">
                  {currentUsername.charAt(0).toUpperCase()}
                </div>
                <span className="font-bold">{currentUsername}</span>
              </div>

              <button
                onClick={handleLogout}
                className="px-3.5 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-500 border border-rose-500/30 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" /> Logout
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main Body */}
      <main className="flex-1 max-w-[1440px] w-full mx-auto px-6 sm:px-10 py-10 z-10">
        
        {/* ========================================================================= */}
        {/* VIEW 1: DEDICATED LOGIN PAGE (WHEN NOT LOGGED IN) */}
        {/* ========================================================================= */}
        {!isLoggedIn && (
          <div className="py-8 flex items-center justify-center">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center w-full max-w-[1320px]">
              
              {/* Left Hero Overview */}
              <div className="lg:col-span-7 space-y-6 animate-fade-in-up">
                <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 text-indigo-500 text-xs font-bold border border-indigo-500/30 shadow-sm">
                  <Sparkles className="w-4 h-4" /> Natural Language Processing Architecture
                </div>

                <h1 className={`text-4xl sm:text-6xl font-black leading-tight tracking-tight ${
                  isDark ? "text-white" : "text-slate-900"
                }`}>
                  Automated Complaint <span className="gradient-title">Intelligence & Routing</span>
                </h1>

                <p className={`text-base leading-relaxed max-w-xl ${
                  isDark ? "text-gray-300" : "text-slate-600"
                }`}>
                  Streamlining customer grievances into structured actions using TF-IDF feature vectorization, Logistic Regression baseline classification, dynamic priority estimation, and automated department dispatch.
                </p>

                {/* Feature Highlight Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
                  <div className={`p-5 rounded-2xl border transition-all duration-300 hover:-translate-y-1.5 ${
                    isDark ? "bg-gray-900/60 border-gray-800" : "bg-white border-slate-200 shadow-md"
                  }`}>
                    <Cpu className="w-7 h-7 text-indigo-500 mb-3" />
                    <h3 className={`text-sm font-bold mb-1 ${isDark ? "text-white" : "text-slate-900"}`}>TF-IDF Classifier</h3>
                    <p className={`text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>Categorizes narratives into 77 banking issue classes.</p>
                  </div>

                  <div className={`p-5 rounded-2xl border transition-all duration-300 hover:-translate-y-1.5 ${
                    isDark ? "bg-gray-900/60 border-gray-800" : "bg-white border-slate-200 shadow-md"
                  }`}>
                    <ShieldAlert className="w-7 h-7 text-purple-500 mb-3" />
                    <h3 className={`text-sm font-bold mb-1 ${isDark ? "text-white" : "text-slate-900"}`}>Priority Engine</h3>
                    <p className={`text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>Flags fraud and stolen card emergencies automatically.</p>
                  </div>

                  <div className={`p-5 rounded-2xl border transition-all duration-300 hover:-translate-y-1.5 ${
                    isDark ? "bg-gray-900/60 border-gray-800" : "bg-white border-slate-200 shadow-md"
                  }`}>
                    <Building2 className="w-7 h-7 text-pink-500 mb-3" />
                    <h3 className={`text-sm font-bold mb-1 ${isDark ? "text-white" : "text-slate-900"}`}>Department Router</h3>
                    <p className={`text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>Directly routes tickets to specialized operational teams.</p>
                  </div>
                </div>
              </div>

              {/* Right Login Form Card */}
              <div className="lg:col-span-5 w-full animate-fade-in-up" style={{ animationDelay: "150ms" }}>
                <div className={`p-8 sm:p-10 rounded-3xl border relative overflow-hidden transition-all duration-300 ${
                  isDark ? "bg-gray-900/80 border-indigo-500/30 shadow-2xl shadow-indigo-950/40" : "bg-white border-slate-200 shadow-2xl shadow-slate-300/80"
                }`}>
                  <div className="flex justify-between items-center mb-6">
                    <div>
                      <h2 className={`text-2xl font-bold mb-1 ${isDark ? "text-white" : "text-slate-900"}`}>System Login</h2>
                      <p className={`text-xs ${isDark ? "text-gray-400" : "text-slate-500"}`}>Select portal role and enter credentials</p>
                    </div>
                    <Lock className="w-6 h-6 text-indigo-500" />
                  </div>

                  {/* Role Selector Tabs */}
                  <div className={`grid grid-cols-2 gap-2 p-1.5 rounded-2xl border mb-6 ${
                    isDark ? "bg-gray-950/80 border-gray-800" : "bg-slate-100 border-slate-300"
                  }`}>
                    <button
                      type="button"
                      onClick={() => selectQuickRole("user")}
                      className={`py-3 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
                        loginRoleTab === "user"
                          ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
                          : isDark ? "text-gray-400 hover:text-white" : "text-slate-600 hover:text-slate-900"
                      }`}
                    >
                      <User className="w-4 h-4" /> Customer Portal
                    </button>
                    <button
                      type="button"
                      onClick={() => selectQuickRole("admin")}
                      className={`py-3 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
                        loginRoleTab === "admin"
                          ? "bg-purple-600 text-white shadow-lg shadow-purple-600/30"
                          : isDark ? "text-gray-400 hover:text-white" : "text-slate-600 hover:text-slate-900"
                      }`}
                    >
                      <ShieldCheck className="w-4 h-4" /> Admin Dashboard
                    </button>
                  </div>

                  <form onSubmit={handleLoginSubmit} className="space-y-5">
                    <div>
                      <label className={`block text-xs font-bold mb-1.5 ${isDark ? "text-gray-300" : "text-slate-700"}`}>Username</label>
                      <input
                        type="text"
                        value={loginUsername}
                        onChange={(e) => setLoginUsername(e.target.value)}
                        className={`w-full rounded-2xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all ${
                          isDark
                            ? "bg-gray-950/90 border border-gray-800 text-white placeholder-gray-500"
                            : "bg-slate-50 border border-slate-300 text-slate-900 placeholder-slate-400"
                        }`}
                        placeholder="Enter username"
                        required
                      />
                    </div>

                    <div>
                      <label className={`block text-xs font-bold mb-1.5 ${isDark ? "text-gray-300" : "text-slate-700"}`}>Password</label>
                      <input
                        type="password"
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        className={`w-full rounded-2xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all ${
                          isDark
                            ? "bg-gray-950/90 border border-gray-800 text-white placeholder-gray-500"
                            : "bg-slate-50 border border-slate-300 text-slate-900 placeholder-slate-400"
                        }`}
                        placeholder="Enter password"
                        required
                      />
                    </div>

                    {loginError && (
                      <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-500 text-xs font-medium">
                        {loginError}
                      </div>
                    )}

                    <button
                      type="submit"
                      disabled={loginLoading}
                      className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white font-extrabold text-sm shadow-xl shadow-indigo-600/30 transition-all transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2 cursor-pointer"
                    >
                      {loginLoading ? (
                        <>
                          <RefreshCw className="w-4 h-4 animate-spin" /> Authenticating...
                        </>
                      ) : (
                        <>
                          Enter {loginRoleTab === "user" ? "Customer Portal" : "Admin Dashboard"} <ChevronRight className="w-4 h-4" />
                        </>
                      )}
                    </button>
                  </form>
                </div>
              </div>

            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* VIEW 2: LOGGED-IN CUSTOMER PORTAL */}
        {/* ========================================================================= */}
        {isLoggedIn && role === "user" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start animate-fade-in-up">
            
            {/* Left Intake Form Column */}
            <div className="lg:col-span-7 space-y-6">
              <div className={`p-8 sm:p-10 rounded-3xl border relative overflow-hidden transition-all duration-300 ${
                isDark ? "bg-gray-900/80 border-gray-800 shadow-2xl" : "bg-white border-slate-200 shadow-xl"
              }`}>
                <div className="flex items-center gap-2 text-indigo-500 text-xs font-extrabold tracking-wider uppercase mb-3">
                  <Sparkles className="w-4 h-4" /> AI Natural Language Processing Intake
                </div>
                <h2 className={`text-3xl sm:text-4xl font-black mb-3 ${isDark ? "text-white" : "text-slate-900"}`}>
                  Submit Your Complaint
                </h2>
                <p className={`text-sm mb-8 leading-relaxed ${isDark ? "text-gray-300" : "text-slate-600"}`}>
                  Describe your issue below. Our machine learning pipeline will automatically parse the complaint, predict the issue category, estimate urgency priority, and dispatch to the correct department.
                </p>

                {/* Sample Presets */}
                <div className={`mb-6 p-4 rounded-2xl border ${
                  isDark ? "bg-gray-950/60 border-gray-800" : "bg-slate-50 border-slate-200"
                }`}>
                  <span className={`text-xs font-bold block mb-2.5 ${isDark ? "text-gray-300" : "text-slate-700"}`}>Quick Test Presets:</span>
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => fillSampleText("Someone used my credit card without permission at a merchant and $450 was deducted.")}
                      className={`px-3 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                        isDark
                          ? "bg-gray-900 hover:bg-indigo-600/20 text-gray-200 border-gray-800"
                          : "bg-white hover:bg-indigo-50 text-slate-800 border-slate-300 shadow-sm"
                      }`}
                    >
                      💳 Unauthorized Card Charge
                    </button>
                    <button
                      type="button"
                      onClick={() => fillSampleText("My wallet was stolen with my credit card inside. Please block it immediately to prevent fraud!")}
                      className={`px-3 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                        isDark
                          ? "bg-gray-900 hover:bg-rose-600/20 text-gray-200 border-gray-800"
                          : "bg-white hover:bg-rose-50 text-slate-800 border-slate-300 shadow-sm"
                      }`}
                    >
                      🚨 Stolen Card Emergency
                    </button>
                    <button
                      type="button"
                      onClick={() => fillSampleText("I tried to transfer money yesterday but the transaction is stuck pending and funds were debited.")}
                      className={`px-3 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                        isDark
                          ? "bg-gray-900 hover:bg-amber-600/20 text-gray-200 border-gray-800"
                          : "bg-white hover:bg-amber-50 text-slate-800 border-slate-300 shadow-sm"
                      }`}
                    >
                      ⏳ Transfer Delayed
                    </button>
                  </div>
                </div>

                <form onSubmit={handleSubmitComplaint} className="space-y-5">
                  <div>
                    <label className={`block text-xs font-bold mb-2 ${isDark ? "text-gray-300" : "text-slate-700"}`}>
                      Describe Complaint Narrative:
                    </label>
                    <textarea
                      rows={6}
                      value={complaintInput}
                      onChange={(e) => setComplaintInput(e.target.value)}
                      placeholder="Example: I noticed an unauthorized charge on my account statement from an unknown vendor..."
                      className={`w-full rounded-2xl p-5 text-sm transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 leading-relaxed ${
                        isDark
                          ? "bg-gray-950/90 border border-gray-800 text-white placeholder-gray-500"
                          : "bg-slate-50 border border-slate-300 text-slate-900 placeholder-slate-400"
                      }`}
                      required
                    ></textarea>
                    <div className={`flex justify-between items-center mt-2.5 text-xs font-medium ${
                      isDark ? "text-gray-400" : "text-slate-500"
                    }`}>
                      <span>Word count: {complaintInput.trim() ? complaintInput.trim().split(/\s+/).length : 0} words</span>
                      <span>{complaintInput.length} characters</span>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmitting || !complaintInput.trim()}
                    className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white font-extrabold text-sm shadow-xl shadow-indigo-600/25 transition-all flex items-center justify-center gap-2.5 cursor-pointer"
                  >
                    {isSubmitting ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" /> Processing AI Pipeline...
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" /> Analyze & Submit Complaint
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* AI Prediction Result Card */}
              {lastPrediction && (
                <div className={`p-6 sm:p-8 rounded-3xl border animate-fade-in-up ${
                  isDark ? "bg-indigo-950/40 border-indigo-500/40 shadow-2xl shadow-indigo-950/50" : "bg-indigo-50/90 border-indigo-200 shadow-xl"
                }`}>
                  <div className="flex items-center justify-between mb-5 border-b pb-4 border-indigo-500/20">
                    <div className="flex items-center gap-2.5 font-bold text-base text-indigo-500">
                      <Bot className="w-6 h-6" /> AI Classification Results
                    </div>
                    <span className="text-xs font-mono px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-500 font-bold border border-indigo-500/30">
                      Ticket #{lastPrediction.id}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
                    <div className={`p-4 rounded-2xl border ${isDark ? "bg-gray-950/70 border-gray-800" : "bg-white border-slate-200 shadow-sm"}`}>
                      <span className={`text-xs block mb-1 font-bold ${isDark ? "text-gray-400" : "text-slate-500"}`}>Predicted Category</span>
                      <span className="font-extrabold text-sm text-indigo-500 capitalize block">{lastPrediction.category.replace(/_/g, " ")}</span>
                    </div>

                    <div className={`p-4 rounded-2xl border ${isDark ? "bg-gray-950/70 border-gray-800" : "bg-white border-slate-200 shadow-sm"}`}>
                      <span className={`text-xs block mb-1 font-bold ${isDark ? "text-gray-400" : "text-slate-500"}`}>Urgency Priority</span>
                      {getPriorityBadge(lastPrediction.priority)}
                    </div>

                    <div className={`p-4 rounded-2xl border ${isDark ? "bg-gray-950/70 border-gray-800" : "bg-white border-slate-200 shadow-sm"}`}>
                      <span className={`text-xs block mb-1 font-bold ${isDark ? "text-gray-400" : "text-slate-500"}`}>Routed Department</span>
                      <span className="font-extrabold text-xs text-purple-600 dark:text-purple-400 block">{lastPrediction.department}</span>
                    </div>
                  </div>

                  <div className={`p-4 rounded-2xl text-xs border ${
                    isDark ? "bg-gray-950/80 border-gray-800 text-gray-300" : "bg-white border-slate-200 text-slate-800 shadow-sm"
                  }`}>
                    <span className={`font-bold block mb-1 ${isDark ? "text-gray-400" : "text-slate-500"}`}>Submitted Complaint Text:</span>
                    <p className="italic">"{lastPrediction.complaint}"</p>
                  </div>
                </div>
              )}
            </div>

            {/* Right Live Tracker Column */}
            <div className="lg:col-span-5 space-y-6">
              <div className={`p-6 sm:p-8 rounded-3xl border transition-all duration-300 ${
                isDark ? "bg-gray-900/80 border-gray-800 shadow-2xl" : "bg-white border-slate-200 shadow-xl"
              }`}>
                <div className="flex items-center justify-between mb-6">
                  <h3 className={`text-xl font-bold flex items-center gap-2.5 ${isDark ? "text-white" : "text-slate-900"}`}>
                    <Activity className="w-5 h-5 text-indigo-500" /> Live Support Tickets
                  </h3>
                  <button
                    onClick={fetchData}
                    className={`px-3.5 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                      isDark ? "bg-gray-950 border-gray-800 text-gray-300 hover:text-white" : "bg-slate-100 border-slate-300 text-slate-700 hover:bg-slate-200"
                    }`}
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${loadingComplaints ? "animate-spin" : ""}`} /> Refresh
                  </button>
                </div>

                {complaints.length === 0 ? (
                  <div className={`text-center py-16 text-sm font-medium ${isDark ? "text-gray-400" : "text-slate-500"}`}>
                    No complaints submitted yet. Submit one to test live tracking.
                  </div>
                ) : (
                  <div className="space-y-4 max-h-[620px] overflow-y-auto pr-1">
                    {complaints.map((item) => (
                      <div
                        key={item.id}
                        className={`p-5 rounded-2xl border transition-all duration-300 hover:-translate-y-1 ${
                          isDark ? "bg-gray-950/70 border-gray-800" : "bg-slate-50 border-slate-200 shadow-sm hover:bg-slate-100/80"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-3">
                          <span className={`font-mono text-xs font-bold ${isDark ? "text-gray-400" : "text-slate-600"}`}>#Ticket-{item.id}</span>
                          {getStatusBadge(item.status)}
                        </div>

                        <p className={`text-xs mb-3.5 line-clamp-3 leading-relaxed ${isDark ? "text-gray-200" : "text-slate-800 font-semibold"}`}>
                          "{item.complaint}"
                        </p>

                        <div className={`flex items-center justify-between text-[11px] border-t pt-3 ${
                          isDark ? "text-gray-400 border-gray-800/80" : "text-slate-500 border-slate-200"
                        }`}>
                          <span className="font-bold text-indigo-600 dark:text-indigo-400 capitalize">{item.category.replace(/_/g, " ")}</span>
                          <span className="font-medium">{item.created_at}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

          </div>
        )}

        {/* ========================================================================= */}
        {/* VIEW 3: LOGGED-IN ADMIN DASHBOARD */}
        {/* ========================================================================= */}
        {isLoggedIn && role === "admin" && (
          <div className="space-y-8 animate-fade-in-up">
            
            {/* Top Metric Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className={`p-6 rounded-3xl border transition-all duration-300 hover:-translate-y-1 ${
                isDark ? "bg-gray-900/80 border-gray-800 shadow-2xl" : "bg-white border-slate-200 shadow-lg"
              }`}>
                <div className="flex justify-between items-start mb-4">
                  <span className={`text-xs font-extrabold uppercase tracking-wider ${isDark ? "text-gray-400" : "text-slate-500"}`}>Total Complaints</span>
                  <div className="p-3 rounded-2xl bg-indigo-500/15 text-indigo-500 border border-indigo-500/20">
                    <Layers className="w-6 h-6" />
                  </div>
                </div>
                <div className={`text-4xl font-black mb-1 ${isDark ? "text-white" : "text-slate-900"}`}>{stats?.total || 0}</div>
                <p className={`text-xs font-semibold ${isDark ? "text-gray-400" : "text-slate-500"}`}>Logged in database</p>
              </div>

              <div className={`p-6 rounded-3xl border transition-all duration-300 hover:-translate-y-1 ${
                isDark ? "bg-gray-900/80 border-gray-800 shadow-2xl" : "bg-white border-slate-200 shadow-lg"
              }`}>
                <div className="flex justify-between items-start mb-4">
                  <span className={`text-xs font-extrabold uppercase tracking-wider ${isDark ? "text-gray-400" : "text-slate-500"}`}>Pending Review</span>
                  <div className="p-3 rounded-2xl bg-yellow-500/15 text-yellow-500 border border-yellow-500/20">
                    <Clock className="w-6 h-6" />
                  </div>
                </div>
                <div className="text-4xl font-black text-amber-500 mb-1">{stats?.pending || 0}</div>
                <p className={`text-xs font-semibold ${isDark ? "text-gray-400" : "text-slate-500"}`}>Awaiting action</p>
              </div>

              <div className={`p-6 rounded-3xl border transition-all duration-300 hover:-translate-y-1 ${
                isDark ? "bg-gray-900/80 border-gray-800 shadow-2xl" : "bg-white border-slate-200 shadow-lg"
              }`}>
                <div className="flex justify-between items-start mb-4">
                  <span className={`text-xs font-extrabold uppercase tracking-wider ${isDark ? "text-gray-400" : "text-slate-500"}`}>In Progress</span>
                  <div className="p-3 rounded-2xl bg-blue-500/15 text-blue-500 border border-blue-500/20">
                    <RefreshCw className="w-6 h-6" />
                  </div>
                </div>
                <div className="text-4xl font-black text-blue-500 mb-1">{stats?.in_progress || 0}</div>
                <p className={`text-xs font-semibold ${isDark ? "text-gray-400" : "text-slate-500"}`}>Under investigation</p>
              </div>

              <div className={`p-6 rounded-3xl border transition-all duration-300 hover:-translate-y-1 ${
                isDark ? "bg-gray-900/80 border-gray-800 shadow-2xl" : "bg-white border-slate-200 shadow-lg"
              }`}>
                <div className="flex justify-between items-start mb-4">
                  <span className={`text-xs font-extrabold uppercase tracking-wider ${isDark ? "text-gray-400" : "text-slate-500"}`}>Resolved Tickets</span>
                  <div className="p-3 rounded-2xl bg-emerald-500/15 text-emerald-500 border border-emerald-500/20">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                </div>
                <div className="text-4xl font-black text-emerald-500 mb-1">{stats?.resolved || 0}</div>
                <p className={`text-xs font-semibold ${isDark ? "text-gray-400" : "text-slate-500"}`}>Closed successfully</p>
              </div>
            </div>

            {/* Filter & Search Bar */}
            <div className={`p-6 rounded-3xl border flex flex-col md:flex-row items-center justify-between gap-5 ${
              isDark ? "bg-gray-900/80 border-gray-800 shadow-2xl" : "bg-white border-slate-200 shadow-md"
            }`}>
              <div className="relative w-full md:w-96">
                <Search className={`w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 ${isDark ? "text-gray-400" : "text-slate-400"}`} />
                <input
                  type="text"
                  placeholder="Search complaints, categories, or IDs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className={`w-full rounded-2xl pl-10 pr-4 py-3 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                    isDark ? "bg-gray-950 border border-gray-800 text-white placeholder-gray-500" : "bg-slate-50 border border-slate-300 text-slate-900 placeholder-slate-400"
                  }`}
                />
              </div>

              <div className="flex flex-wrap items-center gap-4 w-full md:w-auto">
                <div className={`flex items-center gap-2 text-xs font-bold ${isDark ? "text-gray-400" : "text-slate-700"}`}>
                  <Filter className="w-4 h-4" /> Status:
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className={`rounded-xl px-3 py-2 text-xs font-bold focus:outline-none cursor-pointer ${
                      isDark ? "bg-gray-950 border border-gray-800 text-white" : "bg-slate-100 border border-slate-300 text-slate-900"
                    }`}
                  >
                    <option value="All">All Statuses</option>
                    <option value="Pending">Pending</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Resolved">Resolved</option>
                  </select>
                </div>

                <div className={`flex items-center gap-2 text-xs font-bold ${isDark ? "text-gray-400" : "text-slate-700"}`}>
                  <span>Priority:</span>
                  <select
                    value={priorityFilter}
                    onChange={(e) => setPriorityFilter(e.target.value)}
                    className={`rounded-xl px-3 py-2 text-xs font-bold focus:outline-none cursor-pointer ${
                      isDark ? "bg-gray-950 border border-gray-800 text-white" : "bg-slate-100 border border-slate-300 text-slate-900"
                    }`}
                  >
                    <option value="All">All Priorities</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>

                <button
                  onClick={fetchData}
                  className={`px-4 py-2.5 rounded-xl border text-xs font-bold flex items-center gap-2 transition-all cursor-pointer ${
                    isDark ? "bg-gray-950 border-gray-800 text-gray-200 hover:bg-gray-800" : "bg-slate-100 border-slate-300 text-slate-800 hover:bg-slate-200"
                  }`}
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loadingComplaints ? "animate-spin" : ""}`} /> Refresh Table
                </button>
              </div>
            </div>

            {/* Complaints Table Directory */}
            <div className={`rounded-3xl border overflow-hidden ${
              isDark ? "bg-gray-900/80 border-gray-800 shadow-2xl" : "bg-white border-slate-200 shadow-xl"
            }`}>
              <div className={`px-8 py-5 border-b flex justify-between items-center ${
                isDark ? "bg-gray-950/60 border-gray-800" : "bg-slate-50 border-slate-200"
              }`}>
                <h3 className={`font-black text-lg ${isDark ? "text-white" : "text-slate-900"}`}>Support Directory</h3>
                <span className={`text-xs font-bold ${isDark ? "text-gray-400" : "text-slate-500"}`}>Showing {filteredComplaints.length} of {complaints.length} records</span>
              </div>

              {filteredComplaints.length === 0 ? (
                <div className={`p-16 text-center text-sm font-medium ${isDark ? "text-gray-400" : "text-slate-500"}`}>
                  No complaints match current filter criteria.
                </div>
              ) : (
                <div className={isDark ? "divide-y divide-gray-800/80" : "divide-y divide-slate-200"}>
                  {filteredComplaints.map((item) => (
                    <div key={item.id} className={`p-6 transition-all text-xs space-y-4 ${
                      isDark ? "hover:bg-gray-900/30" : "hover:bg-slate-50/80"
                    }`}>
                      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                        <div className="flex flex-wrap items-center gap-3">
                          <span className={`font-mono text-xs font-bold px-2.5 py-1 rounded-lg border ${
                            isDark ? "bg-gray-950 text-gray-400 border-gray-800" : "bg-slate-100 text-slate-700 border-slate-300"
                          }`}>
                            #{item.id}
                          </span>
                          <span className="font-extrabold text-xs text-indigo-600 dark:text-indigo-400 bg-indigo-500/15 px-3 py-1 rounded-lg border border-indigo-500/30 capitalize">
                            {item.category.replace(/_/g, " ")}
                          </span>
                          {getPriorityBadge(item.priority)}
                        </div>

                        <div className={`flex items-center gap-4 text-xs font-bold ${isDark ? "text-gray-400" : "text-slate-600"}`}>
                          <span className="flex items-center gap-1.5">
                            <Building2 className="w-4 h-4 text-purple-600 dark:text-purple-400" /> {item.department}
                          </span>
                          <span>{item.created_at}</span>
                        </div>
                      </div>

                      <p className={`text-sm leading-relaxed p-4 rounded-2xl border font-medium ${
                        isDark ? "bg-gray-950/70 border-gray-800/80 text-gray-200" : "bg-slate-50 border-slate-200 text-slate-800"
                      }`}>
                        "{item.complaint}"
                      </p>

                      <div className={`flex items-center justify-between border-t pt-3 ${
                        isDark ? "border-gray-800/60" : "border-slate-200"
                      }`}>
                        <div className="flex items-center gap-2">
                          <span className={`font-bold ${isDark ? "text-gray-400" : "text-slate-600"}`}>Status:</span>
                          {getStatusBadge(item.status)}
                        </div>

                        <div className="flex items-center gap-2">
                          <span className={`font-bold ${isDark ? "text-gray-400" : "text-slate-600"}`}>Update Status:</span>
                          <select
                            value={item.status}
                            onChange={(e) => handleUpdateStatus(item.id, e.target.value)}
                            className={`rounded-xl px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer font-bold ${
                              isDark ? "bg-gray-950 border border-gray-700 text-white" : "bg-slate-100 border border-slate-300 text-slate-900"
                            }`}
                          >
                            <option value="Pending">Pending</option>
                            <option value="In Progress">In Progress</option>
                            <option value="Resolved">Resolved</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className={`px-8 py-5 border-t text-center text-xs font-semibold transition-colors ${
        isDark ? "border-gray-800/60 bg-gray-950/50 text-gray-500" : "border-slate-200 bg-white text-slate-500"
      }`}>
        Customer Complaint Intelligence System • Next.js Full-Stack AI Platform
      </footer>
    </div>
  );
}
