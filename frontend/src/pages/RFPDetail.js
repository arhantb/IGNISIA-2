import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import api, { formatINR, formatCurrency, STATUS_COLORS, STRATEGY_STYLES } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Play, CheckCircle, XCircle, Warning, FilePdf, Share, Clock, ShieldCheck, ChartLineUp, Lightning } from "@phosphor-icons/react";

export default function RFPDetail() {
  const { rfpId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [rfp, setRfp] = useState(null);
  const [audit, setAudit] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [approvalComment, setApprovalComment] = useState("");
  const [actionLoading, setActionLoading] = useState("");

  const load = useCallback(async () => {
    try {
      const [rfpRes, auditRes] = await Promise.all([
        api.get(`/rfp/${rfpId}`),
        api.get(`/rfp/${rfpId}/audit`).catch(() => ({ data: [] }))
      ]);
      setRfp(rfpRes.data);
      setAudit(auditRes.data);
    } catch { navigate("/dashboard"); }
    finally { setLoading(false); }
  }, [rfpId, navigate]);

  useEffect(() => { load(); }, [load]);

  const runPipeline = async () => {
    setRunning(true);
    try {
      await api.post(`/rfp/${rfpId}/run-pipeline`);
      await load();
    } catch (err) { alert(err.response?.data?.detail || "Pipeline failed"); }
    finally { setRunning(false); }
  };

  const handleApproval = async (action) => {
    setActionLoading(action);
    try {
      await api.post(`/rfp/${rfpId}/approve`, { action, comments: approvalComment });
      await load();
      setApprovalComment("");
    } catch (err) { alert(err.response?.data?.detail || "Action failed"); }
    finally { setActionLoading(""); }
  };

  const handleShare = async () => {
    setActionLoading("share");
    try {
      await api.post(`/rfp/${rfpId}/share`);
      await load();
    } catch (err) { alert(err.response?.data?.detail || "Share failed"); }
    finally { setActionLoading(""); }
  };

  const downloadPdf = () => {
    const token = localStorage.getItem("sq_token");
    window.open(`${process.env.REACT_APP_BACKEND_URL}/api/rfp/${rfpId}/pdf?token=${token}`, "_blank");
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center text-muted-foreground">Loading...</div>;
  if (!rfp) return null;

  const pipeline = rfp.pipeline_result || {};
  const parsed = pipeline.parsed || {};
  const pricing = pipeline.pricing || {};
  const competitor = pipeline.competitor_analysis || {};
  const governance = pipeline.governance || {};
  const summary = pricing.summary || {};
  const lineItems = pricing.line_items || [];
  const strategy = competitor.overall_strategy || "";
  const stratStyle = STRATEGY_STYLES[strategy] || {};

  return (
    <div className="min-h-screen bg-white" data-testid="rfp-detail-page">
      <header className="bg-white/70 backdrop-blur-xl border-b border-border/40 sticky top-0 z-50">
        <div className="max-w-[1400px] mx-auto px-6 flex items-center justify-between h-14">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" className="rounded-none" onClick={() => navigate("/dashboard")} data-testid="back-to-dashboard"><ArrowLeft className="w-4 h-4 mr-1" /> Dashboard</Button>
            <span className="font-mono text-xs text-muted-foreground">{rfpId}</span>
            <span className={`px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider ${STATUS_COLORS[rfp.status] || ""}`}>{rfp.status}</span>
          </div>
          <div className="flex items-center gap-2">
            {rfp.status === "SUBMITTED" && (
              <Button className="bg-[#002FA7] text-white rounded-none" onClick={runPipeline} disabled={running} data-testid="run-pipeline-btn">
                <Play className="w-4 h-4 mr-1" /> {running ? "Processing..." : "Run AI Pipeline"}
              </Button>
            )}
            {rfp.pipeline_result && (
              <Button variant="outline" className="rounded-none" onClick={downloadPdf} data-testid="download-pdf-btn">
                <FilePdf className="w-4 h-4 mr-1" /> PDF
              </Button>
            )}
            {rfp.status === "APPROVED" && (
              <Button className="bg-green-600 text-white rounded-none" onClick={handleShare} disabled={actionLoading === "share"} data-testid="share-quote-btn">
                <Share className="w-4 h-4 mr-1" /> Share with Client
              </Button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-[1400px] mx-auto px-6 py-6">
        {/* Title Bar */}
        <div className="mb-6">
          <h1 className="font-['Chivo'] text-2xl font-bold tracking-tight">{rfp.title}</h1>
          <div className="flex gap-4 mt-1 text-sm text-muted-foreground">
            <span>Client: {rfp.client_name}</span>
            <span>Currency: {rfp.currency}</span>
            {rfp.quote_number && <span className="font-mono">{rfp.quote_number}</span>}
          </div>
        </div>

        {!rfp.pipeline_result ? (
          <div className="border border-dashed border-border p-12 text-center">
            <Lightning className="w-12 h-12 text-[#002FA7] mx-auto mb-3" />
            <h3 className="font-['Chivo'] text-lg font-bold mb-2">Pipeline Not Run</h3>
            <p className="text-muted-foreground text-sm mb-4">Click "Run AI Pipeline" to parse, price, analyze and generate a quotation.</p>
            <Button className="bg-[#002FA7] text-white rounded-none" onClick={runPipeline} disabled={running} data-testid="run-pipeline-empty">
              <Play className="w-4 h-4 mr-2" /> {running ? "Processing..." : "Run AI Pipeline"}
            </Button>
          </div>
        ) : (
          <Tabs defaultValue="pricing" className="animate-fade-in">
            <TabsList className="rounded-none border-b border-border/40 bg-transparent p-0 h-auto">
              {["pricing", "competitor", "governance", "parsed", "audit"].map(tab => (
                <TabsTrigger key={tab} value={tab} className="rounded-none border-b-2 border-transparent data-[state=active]:border-[#002FA7] data-[state=active]:text-[#002FA7] px-4 py-2 text-xs uppercase tracking-wider font-medium" data-testid={`tab-${tab}`}>
                  {tab}
                </TabsTrigger>
              ))}
            </TabsList>

            {/* PRICING TAB */}
            <TabsContent value="pricing" className="mt-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
                {[
                  { l: "Items", v: summary.total_items || 0 },
                  { l: "Subtotal", v: formatCurrency(summary.total_sell_value, rfp.currency) },
                  { l: "Tax", v: formatCurrency(summary.total_tax?.total_tax, rfp.currency) },
                  { l: "Grand Total", v: formatCurrency(summary.grand_total, rfp.currency) },
                  { l: "Margin", v: `${summary.overall_margin_pct || 0}%` },
                ].map((c, i) => (
                  <div key={i} className="border border-border/50 p-3">
                    <div className="text-label">{c.l}</div>
                    <div className="font-mono text-lg font-semibold mt-1">{c.v}</div>
                  </div>
                ))}
              </div>

              {/* Line Items Table */}
              <div className="border border-border/50 overflow-x-auto">
                <table className="w-full text-xs" data-testid="pricing-table">
                  <thead>
                    <tr className="bg-[#002FA7] text-white">
                      <th className="py-2 px-3 text-left">#</th>
                      <th className="py-2 px-3 text-left">Item</th>
                      <th className="py-2 px-3 text-left">HSN</th>
                      <th className="py-2 px-3 text-right">Qty</th>
                      <th className="py-2 px-3 text-right">Unit Price</th>
                      <th className="py-2 px-3 text-right">Total</th>
                      <th className="py-2 px-3 text-right">Tax</th>
                      <th className="py-2 px-3 text-right">With Tax</th>
                      <th className="py-2 px-3 text-right">Margin%</th>
                      <th className="py-2 px-3 text-center">Match</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lineItems.map((item, i) => (
                      <tr key={i} className="border-b border-border/30 hover:bg-muted/20">
                        <td className="py-2 px-3">{i + 1}</td>
                        <td className="py-2 px-3">
                          <div className="font-medium">{item.sku_name}</div>
                          <div className="text-muted-foreground text-[10px]">{item.original_description}</div>
                        </td>
                        <td className="py-2 px-3 font-mono">{item.hsn}</td>
                        <td className="py-2 px-3 text-right font-mono">{item.quantity}</td>
                        <td className="py-2 px-3 text-right font-mono">{formatINR(item.effective_unit_price)}</td>
                        <td className="py-2 px-3 text-right font-mono">{formatINR(item.line_total)}</td>
                        <td className="py-2 px-3 text-right font-mono">{formatINR(item.tax?.total_tax)}</td>
                        <td className="py-2 px-3 text-right font-mono font-medium">{formatINR(item.line_total_with_tax)}</td>
                        <td className="py-2 px-3 text-right">
                          <span className={`font-mono ${item.margin_pct >= item.margin_target ? "text-green-600" : item.margin_pct >= item.margin_floor ? "text-yellow-600" : "text-red-600"}`}>
                            {item.margin_pct}%
                          </span>
                        </td>
                        <td className="py-2 px-3 text-center font-mono">{item.match_score}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </TabsContent>

            {/* COMPETITOR TAB */}
            <TabsContent value="competitor" className="mt-6">
              <div className={`p-4 mb-6 ${stratStyle.bg || ""}`}>
                <div className="flex items-center gap-2 mb-2">
                  <ShieldCheck className="w-5 h-5" />
                  <span className="font-['Chivo'] font-bold text-lg">{stratStyle.label || strategy}</span>
                </div>
                <p className="text-sm">{competitor.overall_strategy_detail?.description}</p>
                <p className="text-sm mt-1 font-medium">{competitor.overall_strategy_detail?.action}</p>
              </div>

              {(competitor.value_adds_recommended || []).length > 0 && (
                <div className="border border-green-200 bg-green-50 p-4 mb-6">
                  <h3 className="font-['Chivo'] font-bold text-sm mb-2">Recommended Value Adds</h3>
                  <div className="flex flex-wrap gap-2">
                    {competitor.value_adds_recommended.map((va, i) => (
                      <Badge key={i} variant="outline" className="rounded-none bg-white">{va.label}</Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-3">
                {(competitor.item_analyses || []).map((item, i) => (
                  <div key={i} className="border border-border/50 p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-sm">{item.sku_name}</span>
                      <Badge variant="outline" className="rounded-none text-[10px]">{item.strategy}</Badge>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-xs mb-2">
                      <div><span className="text-muted-foreground">Our Price:</span> <span className="font-mono">{formatINR(item.our_price)}</span></div>
                      <div><span className="text-muted-foreground">Lowest:</span> <span className="font-mono">{item.lowest_competitor?.name} @ {formatINR(item.lowest_competitor?.price)}</span></div>
                      <div><span className="text-muted-foreground">Avg Market:</span> <span className="font-mono">{formatINR(item.avg_competitor_price)}</span></div>
                    </div>
                    <p className="text-xs text-muted-foreground">{item.rationale}</p>
                  </div>
                ))}
              </div>
            </TabsContent>

            {/* GOVERNANCE TAB */}
            <TabsContent value="governance" className="mt-6">
              <div className={`p-4 mb-6 border-l-4 ${governance.risk_level === "critical" ? "border-l-red-500 bg-red-50" : governance.risk_level === "high" ? "border-l-orange-500 bg-orange-50" : governance.risk_level === "medium" ? "border-l-yellow-500 bg-yellow-50" : "border-l-green-500 bg-green-50"}`}>
                <div className="flex items-center gap-2 mb-1">
                  {governance.risk_level === "critical" || governance.risk_level === "high" ? <Warning className="w-5 h-5" /> : <CheckCircle className="w-5 h-5" />}
                  <span className="font-['Chivo'] font-bold">{governance.approval_message}</span>
                </div>
                <div className="text-xs text-muted-foreground">Risk Level: <span className="uppercase font-mono font-medium">{governance.risk_level}</span></div>
              </div>

              <div className="space-y-2 mb-6">
                {(governance.checks || []).map((c, i) => (
                  <div key={i} className="flex items-center gap-3 border border-border/50 p-3">
                    {c.status === "PASS" ? <CheckCircle className="w-5 h-5 text-green-600" /> : c.status === "FLAGGED" ? <XCircle className="w-5 h-5 text-red-600" /> : <Warning className="w-5 h-5 text-yellow-600" />}
                    <div className="flex-1">
                      <div className="text-xs font-medium uppercase">{c.check.replace(/_/g, " ")}</div>
                      <div className="text-xs text-muted-foreground">{c.detail}</div>
                    </div>
                    <Badge variant="outline" className={`rounded-none text-[10px] ${c.status === "PASS" ? "text-green-600" : c.status === "FLAGGED" ? "text-red-600" : "text-yellow-600"}`}>{c.status}</Badge>
                  </div>
                ))}
              </div>

              {/* Approval Actions */}
              {rfp.status === "PENDING_APPROVAL" && (user?.role === "owner" || user?.role === "admin") && (
                <div className="border border-border/50 p-4">
                  <h3 className="font-['Chivo'] font-bold mb-3">Approval Decision</h3>
                  <Textarea value={approvalComment} onChange={e => setApprovalComment(e.target.value)} placeholder="Add comments (optional)" className="rounded-none mb-3 text-sm" data-testid="approval-comments" />
                  <div className="flex gap-2">
                    <Button className="bg-green-600 text-white rounded-none" onClick={() => handleApproval("approve")} disabled={!!actionLoading} data-testid="approve-btn">
                      <CheckCircle className="w-4 h-4 mr-1" /> Approve
                    </Button>
                    <Button variant="outline" className="rounded-none text-yellow-700 border-yellow-300" onClick={() => handleApproval("revision")} disabled={!!actionLoading} data-testid="revision-btn">
                      Request Revision
                    </Button>
                    <Button variant="outline" className="rounded-none text-red-600 border-red-300" onClick={() => handleApproval("reject")} disabled={!!actionLoading} data-testid="reject-btn">
                      <XCircle className="w-4 h-4 mr-1" /> Reject
                    </Button>
                  </div>
                </div>
              )}
            </TabsContent>

            {/* PARSED TAB */}
            <TabsContent value="parsed" className="mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <h3 className="font-['Chivo'] font-bold">Extracted Information</h3>
                  {[
                    ["Client", parsed.client_name],
                    ["State", parsed.client_state],
                    ["Subject", parsed.subject],
                    ["Deadline", parsed.deadline],
                    ["Delivery", `${parsed.delivery_timeline_days || "N/A"} days`],
                    ["Urgency", parsed.urgency_level],
                    ["Currency", parsed.currency],
                    ["Tax Type", parsed.tax_type],
                    ["Confidence", `${(parsed.confidence_score || 0) * 100}%`],
                  ].map(([k, v]) => (
                    <div key={k} className="flex border-b border-border/30 pb-1">
                      <span className="text-xs text-muted-foreground w-28">{k}</span>
                      <span className="text-xs font-medium">{v || "—"}</span>
                    </div>
                  ))}
                </div>
                <div>
                  <h3 className="font-['Chivo'] font-bold mb-3">Extracted Line Items ({(parsed.line_items || []).length})</h3>
                  <div className="space-y-2">
                    {(parsed.line_items || []).map((item, i) => (
                      <div key={i} className="border border-border/50 p-2 text-xs">
                        <div className="font-medium">{item.description}</div>
                        <div className="text-muted-foreground">Qty: {item.quantity} {item.unit}</div>
                      </div>
                    ))}
                  </div>
                  {(parsed.missing_fields || []).length > 0 && (
                    <div className="mt-4 border border-yellow-200 bg-yellow-50 p-3">
                      <h4 className="font-bold text-xs mb-1">Missing Fields</h4>
                      {parsed.missing_fields.map((f, i) => <div key={i} className="text-xs text-yellow-700">{f}</div>)}
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>

            {/* AUDIT TAB */}
            <TabsContent value="audit" className="mt-6">
              <div className="space-y-0">
                {audit.map((evt, i) => (
                  <div key={i} className="flex gap-4 border-l-2 border-[#002FA7]/20 pl-4 pb-4 relative">
                    <div className="absolute -left-[5px] top-0 w-2.5 h-2.5 bg-[#002FA7] border-2 border-white" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="rounded-none text-[10px]">{evt.agent}</Badge>
                        <span className="text-xs font-medium">{evt.action}</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{evt.details}</p>
                      <div className="text-[10px] text-muted-foreground mt-1 flex gap-2">
                        <Clock className="w-3 h-3" /> {new Date(evt.timestamp).toLocaleString("en-IN")}
                        {evt.user && <span>by {evt.user}</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        )}
      </main>
    </div>
  );
}
