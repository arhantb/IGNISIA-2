import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import api, { formatINR, formatCurrency, STATUS_COLORS } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { FileText, CheckCircle, XCircle, PencilSimple, FilePdf, ArrowRight, Clock, SignOut, Plus } from "@phosphor-icons/react";

export default function ClientPortal() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [rfps, setRfps] = useState([]);
  const [selectedRfp, setSelectedRfp] = useState(null);
  const [quoteData, setQuoteData] = useState(null);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");

  const load = useCallback(async () => {
    try {
      const { data } = await api.get("/rfp/list");
      setRfps(data);
    } catch {}
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const viewQuote = async (rfpId) => {
    try {
      const { data } = await api.get(`/client/quote/${rfpId}`);
      setQuoteData(data);
      setSelectedRfp(rfpId);
    } catch (err) {
      alert(err.response?.data?.detail || "Cannot view quote");
    }
  };

  const handleAction = async (action) => {
    setActionLoading(action);
    try {
      await api.post(`/client/quote/${selectedRfp}/action`, { action, comments: comment });
      setComment("");
      await viewQuote(selectedRfp);
      await load();
    } catch (err) { alert(err.response?.data?.detail || "Action failed"); }
    finally { setActionLoading(""); }
  };

  const handleLogout = async () => { await logout(); navigate("/login"); };

  if (loading) return <div className="min-h-screen flex items-center justify-center text-muted-foreground">Loading...</div>;

  return (
    <div className="min-h-screen bg-white" data-testid="client-portal">
      <header className="bg-white/70 backdrop-blur-xl border-b border-border/40 sticky top-0 z-50">
        <div className="max-w-[1200px] mx-auto px-6 flex items-center justify-between h-14">
          <div className="flex items-center gap-4">
            <span className="font-['Chivo'] font-black text-lg tracking-tight">RFPFlow</span>
            <Badge variant="outline" className="rounded-none text-[10px]">Client Portal</Badge>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" className="rounded-none" onClick={() => navigate("/submit-rfp")} data-testid="client-submit-rfp">
              <Plus className="w-4 h-4 mr-1" /> Submit RFP
            </Button>
            <span className="text-xs text-muted-foreground">{user?.name}</span>
            <Button variant="ghost" size="sm" onClick={handleLogout} data-testid="client-logout"><SignOut className="w-4 h-4" /></Button>
          </div>
        </div>
      </header>

      <main className="max-w-[1200px] mx-auto px-6 py-8">
        {!selectedRfp ? (
          <>
            <h1 className="font-['Chivo'] text-2xl font-bold tracking-tight mb-6">My RFPs & Quotations</h1>
            {rfps.length === 0 ? (
              <div className="border border-dashed border-border p-12 text-center">
                <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                <p className="text-muted-foreground mb-4">No RFPs submitted yet.</p>
                <Button className="bg-[#002FA7] text-white rounded-none" onClick={() => navigate("/submit-rfp")} data-testid="empty-client-submit">Submit Your First RFP</Button>
              </div>
            ) : (
              <div className="space-y-3">
                {rfps.map(rfp => (
                  <div key={rfp.rfp_id} className="border border-border/50 p-4 hover:shadow-md transition-all" data-testid={`client-rfp-${rfp.rfp_id}`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium">{rfp.title}</h3>
                        <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
                          <span className="font-mono">{rfp.rfp_id}</span>
                          <span>{rfp.currency}</span>
                          <span>{new Date(rfp.created_at).toLocaleDateString("en-IN")}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`px-2 py-0.5 text-[10px] font-mono uppercase ${STATUS_COLORS[rfp.status] || ""}`}>{rfp.status}</span>
                        {["SHARED_WITH_CLIENT", "CLIENT_APPROVED", "CLIENT_REVISION"].includes(rfp.status) && (
                          <Button variant="outline" size="sm" className="rounded-none text-xs" onClick={() => viewQuote(rfp.rfp_id)} data-testid={`view-quote-${rfp.rfp_id}`}>
                            View Quote <ArrowRight className="w-3 h-3 ml-1" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        ) : (
          <>
            <Button variant="ghost" className="rounded-none mb-4" onClick={() => { setSelectedRfp(null); setQuoteData(null); }} data-testid="back-to-list">
              <ArrowRight className="w-4 h-4 mr-1 rotate-180" /> Back to My RFPs
            </Button>

            {quoteData && (
              <div className="animate-fade-in">
                {/* Quote Header */}
                <div className="border border-border/50 p-6 mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <div className="text-label">Quotation</div>
                      <h2 className="font-['Chivo'] text-2xl font-bold">{quoteData.quote_number}</h2>
                    </div>
                    <span className={`px-3 py-1 text-xs font-mono uppercase ${STATUS_COLORS[quoteData.status] || ""}`}>{quoteData.status}</span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div><span className="text-muted-foreground">Client:</span> <div className="font-medium">{quoteData.client_name}</div></div>
                    <div><span className="text-muted-foreground">From:</span> <div className="font-medium">{quoteData.company?.name}</div></div>
                    <div><span className="text-muted-foreground">Currency:</span> <div className="font-mono">{quoteData.currency}</div></div>
                    <div><span className="text-muted-foreground">Version:</span> <div className="font-mono">v{quoteData.version}</div></div>
                  </div>
                </div>

                {/* Line Items */}
                <div className="border border-border/50 overflow-x-auto mb-6">
                  <table className="w-full text-sm" data-testid="client-quote-table">
                    <thead>
                      <tr className="bg-muted/50 text-xs">
                        <th className="py-2 px-3 text-left">#</th>
                        <th className="py-2 px-3 text-left">Item</th>
                        <th className="py-2 px-3 text-left">HSN</th>
                        <th className="py-2 px-3 text-right">Qty</th>
                        <th className="py-2 px-3 text-right">Unit Price</th>
                        <th className="py-2 px-3 text-right">Total</th>
                        <th className="py-2 px-3 text-right">Tax</th>
                        <th className="py-2 px-3 text-right font-medium">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(quoteData.line_items || []).map((item, i) => (
                        <tr key={i} className="border-b border-border/30">
                          <td className="py-2 px-3">{i + 1}</td>
                          <td className="py-2 px-3 font-medium">{item.name}</td>
                          <td className="py-2 px-3 font-mono text-xs">{item.hsn}</td>
                          <td className="py-2 px-3 text-right font-mono">{item.quantity}</td>
                          <td className="py-2 px-3 text-right font-mono">{formatINR(item.unit_price)}</td>
                          <td className="py-2 px-3 text-right font-mono">{formatINR(item.line_total)}</td>
                          <td className="py-2 px-3 text-right font-mono">{formatINR(item.tax?.total_tax)}</td>
                          <td className="py-2 px-3 text-right font-mono font-medium">{formatINR(item.total_with_tax)}</td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr className="border-t-2 border-[#002FA7]">
                        <td colSpan="7" className="py-3 px-3 text-right font-['Chivo'] font-bold">Grand Total:</td>
                        <td className="py-3 px-3 text-right font-mono text-lg font-bold text-[#002FA7]">{formatCurrency(quoteData.grand_total, quoteData.currency)}</td>
                      </tr>
                    </tfoot>
                  </table>
                </div>

                {/* Value Adds */}
                {(quoteData.value_adds || []).length > 0 && (
                  <div className="border border-green-200 bg-green-50 p-4 mb-6">
                    <h3 className="font-bold text-sm mb-2">Complimentary Value-Added Services</h3>
                    {quoteData.value_adds.map((va, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm text-green-800">
                        <CheckCircle className="w-4 h-4" /> {va}
                      </div>
                    ))}
                  </div>
                )}

                {/* Client Actions */}
                {quoteData.status === "SHARED_WITH_CLIENT" && (
                  <div className="border border-border/50 p-6">
                    <h3 className="font-['Chivo'] font-bold mb-3">Your Response</h3>
                    <Textarea value={comment} onChange={e => setComment(e.target.value)} placeholder="Add comments or feedback (optional)" className="rounded-none mb-4" data-testid="client-comments" />
                    <div className="flex gap-3">
                      <Button className="bg-green-600 text-white rounded-none" onClick={() => handleAction("approve")} disabled={!!actionLoading} data-testid="client-approve-btn">
                        <CheckCircle className="w-4 h-4 mr-1" /> Approve Quotation
                      </Button>
                      <Button variant="outline" className="rounded-none text-yellow-700" onClick={() => handleAction("request_changes")} disabled={!!actionLoading} data-testid="client-revision-btn">
                        <PencilSimple className="w-4 h-4 mr-1" /> Request Changes
                      </Button>
                      <Button variant="outline" className="rounded-none text-red-600" onClick={() => handleAction("reject")} disabled={!!actionLoading} data-testid="client-reject-btn">
                        <XCircle className="w-4 h-4 mr-1" /> Decline
                      </Button>
                    </div>
                  </div>
                )}

                {/* Previous Responses */}
                {(quoteData.client_responses || []).length > 0 && (
                  <div className="mt-6">
                    <h3 className="font-['Chivo'] font-bold mb-3">Response History</h3>
                    <div className="space-y-2">
                      {quoteData.client_responses.map((r, i) => (
                        <div key={i} className="border border-border/50 p-3 flex items-start gap-3">
                          <Clock className="w-4 h-4 text-muted-foreground mt-0.5" />
                          <div>
                            <div className="text-xs font-medium">{r.action} by {r.by}</div>
                            {r.comments && <div className="text-xs text-muted-foreground mt-1">{r.comments}</div>}
                            <div className="text-[10px] text-muted-foreground mt-1">{new Date(r.timestamp).toLocaleString("en-IN")}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
