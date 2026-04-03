import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, PaperPlaneTilt, FileText } from "@phosphor-icons/react";

export default function SubmitRFP() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ title: "", raw_text: "", client_name: "", client_email: "", client_state: "Maharashtra", currency: "INR", tax_type: "intra_state", deadline: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [samples, setSamples] = useState([]);

  useEffect(() => {
    api.get("/sample-rfps").then(r => setSamples(r.data)).catch(() => {});
  }, []);

  const u = (k, v) => setForm(p => ({ ...p, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.raw_text.trim()) { setError("RFP content is required"); return; }
    setLoading(true);
    setError("");
    try {
      const { data } = await api.post("/rfp/submit", form);
      navigate(`/rfp/${data.rfp_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to submit");
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (sample) => {
    setForm(p => ({ ...p, title: sample.title, raw_text: sample.raw_text, currency: sample.currency }));
  };

  return (
    <div className="min-h-screen bg-white" data-testid="submit-rfp-page">
      <header className="bg-white/70 backdrop-blur-xl border-b border-border/40 sticky top-0 z-50">
        <div className="max-w-[1400px] mx-auto px-6 flex items-center h-14 gap-4">
          <Button variant="ghost" size="sm" className="rounded-none" onClick={() => navigate(user?.role === "client" ? "/client" : "/dashboard")} data-testid="back-btn">
            <ArrowLeft className="w-4 h-4 mr-1" /> Back
          </Button>
          <span className="font-['Chivo'] font-bold">Submit New RFP</span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-3 mb-4">{error}</div>}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label>RFP Title</Label>
                <Input value={form.title} onChange={e => u("title", e.target.value)} placeholder="E.g., Municipal Office Electrical Supply" className="rounded-none mt-1" data-testid="rfp-title" required />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Client Name</Label>
                  <Input value={form.client_name} onChange={e => u("client_name", e.target.value)} placeholder="Company name" className="rounded-none mt-1" data-testid="rfp-client-name" />
                </div>
                <div>
                  <Label>Client Email</Label>
                  <Input value={form.client_email} onChange={e => u("client_email", e.target.value)} placeholder="email@company.com" className="rounded-none mt-1" data-testid="rfp-client-email" />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label>State</Label>
                  <Select value={form.client_state} onValueChange={v => u("client_state", v)}>
                    <SelectTrigger className="rounded-none mt-1" data-testid="rfp-state"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {["Maharashtra","Gujarat","Tamil Nadu","Karnataka","Delhi","Rajasthan","International"].map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Currency</Label>
                  <Select value={form.currency} onValueChange={v => u("currency", v)}>
                    <SelectTrigger className="rounded-none mt-1" data-testid="rfp-currency"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="INR">INR</SelectItem>
                      <SelectItem value="USD">USD</SelectItem>
                      <SelectItem value="EUR">EUR</SelectItem>
                      <SelectItem value="AED">AED</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Tax Type</Label>
                  <Select value={form.tax_type} onValueChange={v => u("tax_type", v)}>
                    <SelectTrigger className="rounded-none mt-1" data-testid="rfp-tax-type"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="intra_state">Intra-State (CGST+SGST)</SelectItem>
                      <SelectItem value="inter_state">Inter-State (IGST)</SelectItem>
                      <SelectItem value="export">Export (Zero-rated)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label>Deadline</Label>
                <Input type="date" value={form.deadline} onChange={e => u("deadline", e.target.value)} className="rounded-none mt-1" data-testid="rfp-deadline" />
              </div>
              <div>
                <Label>RFP Content (paste full text)</Label>
                <Textarea value={form.raw_text} onChange={e => u("raw_text", e.target.value)} placeholder="Paste the complete RFP / tender document text here..." className="rounded-none mt-1 min-h-[300px] font-mono text-xs" data-testid="rfp-content" required />
              </div>
              <Button type="submit" disabled={loading} className="bg-[#002FA7] text-white rounded-none px-8 py-5" data-testid="submit-rfp-btn">
                <PaperPlaneTilt className="w-4 h-4 mr-2" /> {loading ? "Submitting..." : "Submit RFP"}
              </Button>
            </form>
          </div>

          {/* Sample RFPs sidebar */}
          <div>
            <p className="text-label mb-3">Sample RFPs</p>
            <div className="space-y-2">
              {samples.map((s, i) => (
                <button key={i} onClick={() => loadSample(s)} className="w-full text-left border border-border/50 p-3 hover:bg-muted/30 transition-colors" data-testid={`sample-rfp-${i}`}>
                  <div className="flex items-start gap-2">
                    <FileText className="w-4 h-4 text-[#002FA7] mt-0.5 flex-shrink-0" />
                    <div>
                      <div className="text-xs font-medium">{s.title}</div>
                      <div className="text-[10px] text-muted-foreground mt-0.5">{s.scenario} | {s.currency}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
