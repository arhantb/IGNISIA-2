import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import api, { formatINR, STATUS_COLORS } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ChartLineUp, FileText, Clock, CheckCircle, Warning, ArrowRight, Plus, SignOut, Buildings, Factory, CurrencyInr, Users, TrendUp, MapPin, ShieldCheck, Handshake, Globe } from "@phosphor-icons/react";

const LOGO_URL = "https://customer-assets.emergentagent.com/job_smartquote-engine/artifacts/ls74viwp_Screenshot%202026-04-03%20194540.png";
const MSME_IMG = "https://customer-assets.emergentagent.com/job_smartquote-engine/artifacts/nipjjwo7_image.png";

const MSME_STATS = [
  { icon: <Globe weight="bold" className="w-5 h-5" />, value: "45%", label: "India's Total Exports", color: "text-blue-700", bg: "bg-blue-50" },
  { icon: <TrendUp weight="bold" className="w-5 h-5" />, value: "30%", label: "Contribution to GDP", color: "text-green-700", bg: "bg-green-50" },
  { icon: <Factory weight="bold" className="w-5 h-5" />, value: "38.4%", label: "Manufacturing Output", color: "text-purple-700", bg: "bg-purple-50" },
  { icon: <Users weight="bold" className="w-5 h-5" />, value: "11 Cr", label: "Employment Generated", color: "text-orange-700", bg: "bg-orange-50" },
];

const MSME_STATES = [
  { state: "Maharashtra", pct: 17.74, color: "bg-[#002FA7]" },
  { state: "Tamil Nadu", pct: 10.20, color: "bg-[#002FA7]/80" },
  { state: "Uttar Pradesh", pct: 9.34, color: "bg-[#002FA7]/60" },
  { state: "Gujarat", pct: 7.43, color: "bg-[#002FA7]/50" },
  { state: "Rajasthan", pct: 7.38, color: "bg-[#002FA7]/40" },
];

const GOVT_SCHEMES = [
  { name: "CHAMPIONS 2.0 Portal", desc: "Single-window complaint resolution" },
  { name: "RAMP Scheme", desc: "Performance improvement of MSMEs" },
  { name: "TReDS", desc: "Trade receivable discounting for faster payments" },
  { name: "PMEGP", desc: "Employment generation through new enterprises" },
  { name: "CGTMSE", desc: "Collateral-free credit guarantee upto Rs 5 Cr" },
  { name: "Udyam Assist Platform", desc: "Easy MSME registration" },
];

const CHALLENGES = [
  { text: "Only 16% of SMEs get access to timely finance", severity: "high" },
  { text: "~86% manufacturing MSMEs are unregistered", severity: "high" },
  { text: "Delayed payments from larger enterprises & govt agencies", severity: "medium" },
  { text: "Outdated technology & lower productivity levels", severity: "medium" },
];

export default function SMEDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [kpis, setKpis] = useState(null);
  const [rfps, setRfps] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const [kpiRes, rfpRes] = await Promise.all([api.get("/dashboard/kpis"), api.get("/rfp/list")]);
      setKpis(kpiRes.data);
      setRfps(rfpRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleLogout = async () => { await logout(); navigate("/login"); };

  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="text-muted-foreground">Loading dashboard...</div></div>;

  const winRate = kpis?.total_rfps > 0 ? Math.round((kpis?.client_approved || 0) / kpis.total_rfps * 100) : 0;

  return (
    <div className="min-h-screen bg-[#FAFBFC]" data-testid="sme-dashboard">
      {/* Header */}
      <header className="bg-white border-b border-border/40 sticky top-0 z-50">
        <div className="max-w-[1440px] mx-auto px-6 flex items-center justify-between h-14">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("/dashboard")}>
              <img src={LOGO_URL} alt="RFPFlow" className="h-8 w-auto" />
              <span className="font-['Chivo'] font-black text-lg tracking-tight">RFPFlow</span>
            </div>
            <nav className="hidden md:flex gap-1">
              <Button variant="ghost" size="sm" className="rounded-none text-xs font-medium bg-muted/50" data-testid="nav-dashboard">Dashboard</Button>
              <Button variant="ghost" size="sm" className="rounded-none text-xs font-medium" onClick={() => navigate("/submit-rfp")} data-testid="nav-submit-rfp">Submit RFP</Button>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground">{user?.name} <Badge variant="outline" className="rounded-none ml-1 text-[10px]">{user?.role?.toUpperCase()}</Badge></span>
            <Button variant="ghost" size="sm" onClick={handleLogout} data-testid="logout-btn"><SignOut className="w-4 h-4" /></Button>
          </div>
        </div>
      </header>

      <main className="max-w-[1440px] mx-auto px-6 py-6">
        {/* Welcome + CTA Banner */}
        <div className="bg-[#002FA7] text-white p-6 mb-6 flex items-center justify-between">
          <div>
            <h1 className="font-['Chivo'] text-2xl font-black tracking-tight">Welcome back, {user?.name?.split(' ')[0]}</h1>
            <p className="text-white/70 text-sm mt-1">Autonomous RFP Response & Competitive Quotation Engine for Indian MSMEs</p>
          </div>
          <Button className="bg-white text-[#002FA7] rounded-none hover:bg-white/90 font-bold" onClick={() => navigate("/submit-rfp")} data-testid="hero-new-rfp-btn">
            <Plus className="w-4 h-4 mr-2" /> New RFP
          </Button>
        </div>

        <Tabs defaultValue="pipeline" className="animate-fade-in">
          <TabsList className="rounded-none border-b border-border/40 bg-transparent p-0 h-auto mb-6">
            <TabsTrigger value="pipeline" className="rounded-none border-b-2 border-transparent data-[state=active]:border-[#002FA7] data-[state=active]:text-[#002FA7] px-5 py-2.5 text-xs uppercase tracking-wider font-medium" data-testid="tab-pipeline">
              Pipeline & RFPs
            </TabsTrigger>
            <TabsTrigger value="msme" className="rounded-none border-b-2 border-transparent data-[state=active]:border-[#002FA7] data-[state=active]:text-[#002FA7] px-5 py-2.5 text-xs uppercase tracking-wider font-medium" data-testid="tab-msme-insights">
              MSME Insights
            </TabsTrigger>
            <TabsTrigger value="schemes" className="rounded-none border-b-2 border-transparent data-[state=active]:border-[#002FA7] data-[state=active]:text-[#002FA7] px-5 py-2.5 text-xs uppercase tracking-wider font-medium" data-testid="tab-schemes">
              Govt Schemes
            </TabsTrigger>
          </TabsList>

          {/* ========= PIPELINE TAB ========= */}
          <TabsContent value="pipeline">
            {/* KPIs */}
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-6">
              {[
                { label: "TOTAL RFPS", value: kpis?.total_rfps || 0, icon: <FileText className="w-5 h-5" />, color: "text-[#002FA7]", bg: "bg-blue-50" },
                { label: "PENDING APPROVAL", value: kpis?.pending_approval || 0, icon: <Clock className="w-5 h-5" />, color: "text-orange-600", bg: "bg-orange-50" },
                { label: "APPROVED", value: kpis?.approved || 0, icon: <CheckCircle className="w-5 h-5" />, color: "text-green-600", bg: "bg-green-50" },
                { label: "PIPELINE VALUE", value: `\u20B9${formatINR(kpis?.total_pipeline_value || 0)}`, icon: <CurrencyInr className="w-5 h-5" />, color: "text-emerald-700", bg: "bg-emerald-50" },
                { label: "AVG MARGIN", value: `${kpis?.avg_margin_pct || 0}%`, icon: <TrendUp className="w-5 h-5" />, color: "text-purple-600", bg: "bg-purple-50" },
                { label: "WIN RATE", value: `${winRate}%`, icon: <Handshake className="w-5 h-5" />, color: "text-teal-600", bg: "bg-teal-50" },
              ].map((k, i) => (
                <div key={i} className={`border border-border/50 bg-white p-4 animate-slide-up`} style={{ animationDelay: `${i * 0.04}s` }} data-testid={`kpi-${k.label.toLowerCase().replace(/\s+/g, '-')}`}>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[10px] tracking-[0.15em] uppercase font-bold text-muted-foreground">{k.label}</span>
                    <span className={`${k.color} ${k.bg} p-1.5`}>{k.icon}</span>
                  </div>
                  <div className="font-mono text-xl font-semibold tracking-tight">{k.value}</div>
                </div>
              ))}
            </div>

            {/* Quick MSME Context Strip */}
            <div className="bg-gradient-to-r from-[#002FA7]/5 via-transparent to-[#002FA7]/5 border border-[#002FA7]/10 p-3 mb-6 flex items-center gap-6 overflow-x-auto">
              <div className="flex items-center gap-2 flex-shrink-0">
                <Buildings weight="bold" className="w-4 h-4 text-[#002FA7]" />
                <span className="text-xs font-bold text-[#002FA7]">MSME INDIA</span>
              </div>
              {MSME_STATS.map((s, i) => (
                <div key={i} className="flex items-center gap-2 flex-shrink-0 text-xs">
                  <span className="font-mono font-bold">{s.value}</span>
                  <span className="text-muted-foreground">{s.label}</span>
                </div>
              ))}
            </div>

            {/* RFP Table */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-['Chivo'] text-lg font-bold tracking-tight">RFP Queue</h2>
              <Button className="bg-[#002FA7] text-white rounded-none" onClick={() => navigate("/submit-rfp")} data-testid="new-rfp-btn">
                <Plus className="w-4 h-4 mr-2" /> New RFP
              </Button>
            </div>

            {rfps.length === 0 ? (
              <div className="border border-dashed border-border p-12 text-center bg-white">
                <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                <p className="text-muted-foreground">No RFPs yet. Submit your first RFP to get started.</p>
                <Button className="mt-4 bg-[#002FA7] text-white rounded-none" onClick={() => navigate("/submit-rfp")} data-testid="empty-submit-btn">Submit RFP</Button>
              </div>
            ) : (
              <div className="border border-border/50 bg-white overflow-hidden">
                <table className="w-full text-sm" data-testid="rfp-table">
                  <thead>
                    <tr className="bg-[#002FA7] text-white text-xs">
                      <th className="py-3 px-4 text-left font-medium">RFP ID</th>
                      <th className="py-3 px-4 text-left font-medium">Title</th>
                      <th className="py-3 px-4 text-left font-medium">Client</th>
                      <th className="py-3 px-4 text-left font-medium">Status</th>
                      <th className="py-3 px-4 text-left font-medium">Currency</th>
                      <th className="py-3 px-4 text-left font-medium">Created</th>
                      <th className="py-3 px-4 text-left font-medium">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rfps.map((rfp) => (
                      <tr key={rfp.rfp_id} className="border-b border-border/30 hover:bg-muted/30 transition-colors" data-testid={`rfp-row-${rfp.rfp_id}`}>
                        <td className="py-3 px-4 font-mono text-xs">{rfp.rfp_id}</td>
                        <td className="py-3 px-4 font-medium max-w-[200px] truncate">{rfp.title}</td>
                        <td className="py-3 px-4 text-muted-foreground">{rfp.client_name}</td>
                        <td className="py-3 px-4">
                          <span className={`inline-block px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider ${STATUS_COLORS[rfp.status] || "bg-gray-100"}`}>
                            {rfp.status?.replace(/_/g, " ")}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-xs">{rfp.currency}</td>
                        <td className="py-3 px-4 text-muted-foreground text-xs">{new Date(rfp.created_at).toLocaleDateString("en-IN")}</td>
                        <td className="py-3 px-4">
                          <Button variant="ghost" size="sm" className="rounded-none text-xs text-[#002FA7]" onClick={() => navigate(`/rfp/${rfp.rfp_id}`)} data-testid={`view-rfp-${rfp.rfp_id}`}>
                            View <ArrowRight className="w-3 h-3 ml-1" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </TabsContent>

          {/* ========= MSME INSIGHTS TAB ========= */}
          <TabsContent value="msme">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left: Stats + States */}
              <div className="lg:col-span-2 space-y-6">
                {/* MSME Economy Share */}
                <div className="bg-white border border-border/50 p-6">
                  <h3 className="font-['Chivo'] font-bold text-lg mb-1">Share of MSMEs in Indian Economy</h3>
                  <p className="text-xs text-muted-foreground mb-4">India's MSME sector is the backbone of the economy, driving exports, employment, and GDP growth.</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {MSME_STATS.map((s, i) => (
                      <div key={i} className={`${s.bg} p-4 border border-border/30`}>
                        <div className={`${s.color} mb-2`}>{s.icon}</div>
                        <div className="font-mono text-2xl font-bold tracking-tight">{s.value}</div>
                        <div className="text-xs text-muted-foreground mt-1">{s.label}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Key MSME States */}
                <div className="bg-white border border-border/50 p-6">
                  <h3 className="font-['Chivo'] font-bold text-lg mb-1">Key MSME States</h3>
                  <p className="text-xs text-muted-foreground mb-4">Top 5 states by MSME concentration. Maharashtra leads with 17.74% of all registered MSMEs.</p>
                  <div className="space-y-3">
                    {MSME_STATES.map((s, i) => (
                      <div key={i} className="flex items-center gap-3">
                        <div className="flex items-center gap-2 w-32">
                          <MapPin weight="bold" className="w-3.5 h-3.5 text-[#002FA7]" />
                          <span className="text-sm font-medium">{s.state}</span>
                        </div>
                        <div className="flex-1 bg-muted/50 h-6 relative overflow-hidden">
                          <div className={`h-full ${s.color} transition-all duration-700`} style={{ width: `${s.pct * 4}%` }} />
                          <span className="absolute right-2 top-0.5 text-xs font-mono font-bold">{s.pct}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Registration Breakdown */}
                <div className="bg-white border border-border/50 p-6">
                  <h3 className="font-['Chivo'] font-bold text-lg mb-4">Registered MSMEs in India (FY24)</h3>
                  <div className="grid grid-cols-3 gap-4">
                    {[
                      { type: "Micro", pct: "97.7%", desc: "Investment up to Rs 1 Crore", color: "bg-[#002FA7]", investment: "Turnover up to Rs 5 Crore" },
                      { type: "Small", pct: "1.5%", desc: "Investment up to Rs 10 Crore", color: "bg-[#002FA7]/70", investment: "Turnover up to Rs 50 Crore" },
                      { type: "Medium", pct: "0.8%", desc: "Investment up to Rs 50 Crore", color: "bg-[#002FA7]/40", investment: "Turnover up to Rs 250 Crore" },
                    ].map((cat, i) => (
                      <div key={i} className="border border-border/50 p-4 text-center">
                        <div className={`w-12 h-12 ${cat.color} text-white flex items-center justify-center mx-auto mb-3 font-mono text-lg font-bold`}>
                          {cat.pct}
                        </div>
                        <div className="font-['Chivo'] font-bold">{cat.type}</div>
                        <div className="text-xs text-muted-foreground mt-1">{cat.desc}</div>
                        <div className="text-[10px] text-muted-foreground mt-0.5">{cat.investment}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Challenges */}
                <div className="bg-white border border-border/50 p-6">
                  <h3 className="font-['Chivo'] font-bold text-lg mb-1">Key MSME Challenges</h3>
                  <p className="text-xs text-muted-foreground mb-4">RFPFlow helps address the quotation & pricing challenges that hold MSMEs back from competing effectively.</p>
                  <div className="space-y-2">
                    {CHALLENGES.map((c, i) => (
                      <div key={i} className={`flex items-start gap-3 p-3 ${c.severity === "high" ? "bg-red-50 border-l-4 border-l-red-400" : "bg-yellow-50 border-l-4 border-l-yellow-400"}`}>
                        <Warning weight="bold" className={`w-4 h-4 mt-0.5 flex-shrink-0 ${c.severity === "high" ? "text-red-500" : "text-yellow-500"}`} />
                        <span className="text-sm">{c.text}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right: Infographic + How RFPFlow helps */}
              <div className="space-y-6">
                <div className="bg-white border border-border/50 overflow-hidden">
                  <img src={MSME_IMG} alt="India MSME Sector Infographic" className="w-full" data-testid="msme-infographic" />
                </div>

                <div className="bg-[#002FA7] text-white p-6">
                  <h3 className="font-['Chivo'] font-bold text-lg mb-3">How RFPFlow Helps MSMEs</h3>
                  <div className="space-y-3">
                    {[
                      { icon: <FileText weight="bold" className="w-4 h-4" />, text: "AI-powered RFP parsing saves hours of manual work" },
                      { icon: <CurrencyInr weight="bold" className="w-4 h-4" />, text: "Deterministic pricing engine ensures consistent quotes" },
                      { icon: <ShieldCheck weight="bold" className="w-4 h-4" />, text: "Competitor intelligence prevents under-bidding" },
                      { icon: <ChartLineUp weight="bold" className="w-4 h-4" />, text: "GST-compliant quotations accepted nationwide" },
                      { icon: <Handshake weight="bold" className="w-4 h-4" />, text: "Faster turnaround wins more government tenders" },
                    ].map((item, i) => (
                      <div key={i} className="flex items-start gap-3">
                        <div className="bg-white/20 p-1.5 flex-shrink-0">{item.icon}</div>
                        <span className="text-sm text-white/90">{item.text}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="bg-white border border-border/50 p-6">
                  <h3 className="font-['Chivo'] font-bold text-sm mb-3">MSME Regulation</h3>
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between border-b border-border/30 pb-1">
                      <span className="text-muted-foreground">Nodal Ministry</span>
                      <span className="font-medium">Ministry of MSME</span>
                    </div>
                    <div className="flex justify-between border-b border-border/30 pb-1">
                      <span className="text-muted-foreground">Governing Act</span>
                      <span className="font-medium">MSMED Act, 2006</span>
                    </div>
                    <div className="flex justify-between border-b border-border/30 pb-1">
                      <span className="text-muted-foreground">Registration</span>
                      <span className="font-medium">Udyam Portal</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">MSME Day</span>
                      <span className="font-medium">27th June (Intl)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* ========= GOVT SCHEMES TAB ========= */}
          <TabsContent value="schemes">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white border border-border/50 p-6">
                <h3 className="font-['Chivo'] font-bold text-lg mb-1">Government Initiatives & Support</h3>
                <p className="text-xs text-muted-foreground mb-4">Key government schemes available for MSME vendors bidding through RFPFlow.</p>
                <div className="space-y-3">
                  {GOVT_SCHEMES.map((s, i) => (
                    <div key={i} className="border border-border/50 p-3 hover:bg-muted/20 transition-colors">
                      <div className="flex items-center gap-2 mb-1">
                        <ShieldCheck weight="bold" className="w-4 h-4 text-[#002FA7]" />
                        <span className="font-medium text-sm">{s.name}</span>
                      </div>
                      <p className="text-xs text-muted-foreground pl-6">{s.desc}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                <div className="bg-white border border-border/50 p-6">
                  <h3 className="font-['Chivo'] font-bold text-lg mb-4">MSME Classification (Current Norms)</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs border-collapse">
                      <thead>
                        <tr className="bg-[#002FA7] text-white">
                          <th className="py-2 px-3 text-left font-medium">Classification</th>
                          <th className="py-2 px-3 text-center font-medium">Micro</th>
                          <th className="py-2 px-3 text-center font-medium">Small</th>
                          <th className="py-2 px-3 text-center font-medium">Medium</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="border-b border-border/30">
                          <td className="py-2 px-3 font-medium">Investment in Plant & Machinery</td>
                          <td className="py-2 px-3 text-center font-mono">Up to Rs 1 Cr</td>
                          <td className="py-2 px-3 text-center font-mono">Up to Rs 10 Cr</td>
                          <td className="py-2 px-3 text-center font-mono">Up to Rs 50 Cr</td>
                        </tr>
                        <tr>
                          <td className="py-2 px-3 font-medium">Annual Turnover</td>
                          <td className="py-2 px-3 text-center font-mono">Up to Rs 5 Cr</td>
                          <td className="py-2 px-3 text-center font-mono">Up to Rs 50 Cr</td>
                          <td className="py-2 px-3 text-center font-mono">Up to Rs 250 Cr</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="bg-white border border-border/50 p-6">
                  <h3 className="font-['Chivo'] font-bold text-lg mb-3">Financial Support Schemes</h3>
                  <div className="space-y-2">
                    {[
                      "Pradhan Mantri Mudra Yojana (PMMY)",
                      "Credit Guarantee (CGTMSE) - Collateral free upto Rs 5 Cr",
                      "Interest Subsidy Eligibility Certificate (ISEC)",
                      "Trade Receivable Discounting System (TReDS)",
                      "Zero Defect & Zero Effect (ZED) Certification",
                    ].map((scheme, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm">
                        <div className="w-1.5 h-1.5 bg-[#002FA7] flex-shrink-0" />
                        {scheme}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-gradient-to-br from-[#002FA7] to-[#001a60] text-white p-6">
                  <h3 className="font-['Chivo'] font-bold text-base mb-2">MSME Purchase Preference</h3>
                  <p className="text-sm text-white/80 mb-3">
                    Government mandates 25% purchase preference for MSMEs in all public procurement. RFPFlow helps you structure competitive GST-compliant quotes to win these tenders.
                  </p>
                  <Button className="bg-white text-[#002FA7] rounded-none text-sm font-bold hover:bg-white/90" onClick={() => navigate("/submit-rfp")} data-testid="scheme-submit-rfp">
                    Start Quoting <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
