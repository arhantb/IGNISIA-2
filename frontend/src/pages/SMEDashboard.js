import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import api, { formatINR, STATUS_COLORS } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChartLineUp, FileText, Clock, CheckCircle, Warning, ArrowRight, Plus, SignOut } from "@phosphor-icons/react";

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

  return (
    <div className="min-h-screen bg-white" data-testid="sme-dashboard">
      {/* Header */}
      <header className="bg-white/70 backdrop-blur-xl border-b border-border/40 sticky top-0 z-50">
        <div className="max-w-[1400px] mx-auto px-6 flex items-center justify-between h-14">
          <div className="flex items-center gap-6">
            <span className="font-['Chivo'] font-black text-lg tracking-tight">SmartQuote</span>
            <nav className="hidden md:flex gap-1">
              <Button variant="ghost" size="sm" className="rounded-none text-xs font-medium" onClick={() => navigate("/dashboard")} data-testid="nav-dashboard">Dashboard</Button>
              <Button variant="ghost" size="sm" className="rounded-none text-xs font-medium" onClick={() => navigate("/submit-rfp")} data-testid="nav-submit-rfp">Submit RFP</Button>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground">{user?.name} <Badge variant="outline" className="rounded-none ml-1 text-[10px]">{user?.role}</Badge></span>
            <Button variant="ghost" size="sm" onClick={handleLogout} data-testid="logout-btn"><SignOut className="w-4 h-4" /></Button>
          </div>
        </div>
      </header>

      <main className="max-w-[1400px] mx-auto px-6 py-8">
        {/* KPIs */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: "TOTAL RFPS", value: kpis?.total_rfps || 0, icon: <FileText className="w-5 h-5" />, color: "text-[#002FA7]" },
            { label: "PENDING APPROVAL", value: kpis?.pending_approval || 0, icon: <Clock className="w-5 h-5" />, color: "text-orange-600" },
            { label: "PIPELINE VALUE", value: `\u20B9${formatINR(kpis?.total_pipeline_value || 0)}`, icon: <ChartLineUp className="w-5 h-5" />, color: "text-green-600" },
            { label: "AVG MARGIN", value: `${kpis?.avg_margin_pct || 0}%`, icon: <CheckCircle className="w-5 h-5" />, color: "text-emerald-600" },
          ].map((k, i) => (
            <div key={i} className="border border-border/50 p-4 animate-slide-up" style={{ animationDelay: `${i * 0.05}s` }} data-testid={`kpi-${k.label.toLowerCase().replace(/\s+/g, '-')}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-label">{k.label}</span>
                <span className={k.color}>{k.icon}</span>
              </div>
              <div className="font-mono text-2xl font-semibold tracking-tight">{k.value}</div>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-['Chivo'] text-xl font-bold tracking-tight">RFP Queue</h2>
          <Button className="bg-[#002FA7] text-white rounded-none" onClick={() => navigate("/submit-rfp")} data-testid="new-rfp-btn">
            <Plus className="w-4 h-4 mr-2" /> New RFP
          </Button>
        </div>

        {/* RFP Table */}
        {rfps.length === 0 ? (
          <div className="border border-dashed border-border p-12 text-center">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No RFPs yet. Submit your first RFP to get started.</p>
            <Button className="mt-4 bg-[#002FA7] text-white rounded-none" onClick={() => navigate("/submit-rfp")} data-testid="empty-submit-btn">Submit RFP</Button>
          </div>
        ) : (
          <div className="border border-border/50 overflow-hidden">
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
                {rfps.map((rfp, i) => (
                  <tr key={rfp.rfp_id} className="border-b border-border/30 hover:bg-muted/30 transition-colors" data-testid={`rfp-row-${rfp.rfp_id}`}>
                    <td className="py-3 px-4 font-mono text-xs">{rfp.rfp_id}</td>
                    <td className="py-3 px-4 font-medium max-w-[200px] truncate">{rfp.title}</td>
                    <td className="py-3 px-4 text-muted-foreground">{rfp.client_name}</td>
                    <td className="py-3 px-4">
                      <span className={`inline-block px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider ${STATUS_COLORS[rfp.status] || "bg-gray-100"}`}>
                        {rfp.status}
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
      </main>
    </div>
  );
}
