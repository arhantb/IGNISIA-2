import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { formatApiError } from "@/lib/api";
import { Lightning } from "@phosphor-icons/react";

const LOGO_URL = "https://customer-assets.emergentagent.com/job_smartquote-engine/artifacts/ls74viwp_Screenshot%202026-04-03%20194540.png";

export default function Register() {
  const [form, setForm] = useState({ email: "", password: "", name: "", role: "client", company_name: "", state: "Maharashtra" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await register(form);
      navigate(data.role === "client" ? "/client" : "/dashboard");
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail) || err.message);
    } finally {
      setLoading(false);
    }
  };

  const u = (key, val) => setForm(p => ({ ...p, [key]: val }));

  const STATES = ["Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Delhi","International"];

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-muted/30" data-testid="register-page">
      <div className="w-full max-w-lg bg-white border border-border/50 p-8">
        <div className="flex items-center gap-2 mb-6">
          <img src={LOGO_URL} alt="RFPFlow" className="h-8 w-auto" />
          <span className="font-['Chivo'] font-black text-lg">RFPFlow</span>
        </div>
        <h1 className="font-['Chivo'] text-2xl font-black tracking-tight mb-1">Create Account</h1>
        <p className="text-muted-foreground text-sm mb-6">Register to submit RFPs or manage quotations on RFPFlow</p>

        {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-3 mb-4" data-testid="register-error">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Full Name</Label>
              <Input value={form.name} onChange={e => u("name", e.target.value)} placeholder="Your name" className="rounded-none mt-1" data-testid="register-name" required />
            </div>
            <div>
              <Label>Role</Label>
              <Select value={form.role} onValueChange={v => u("role", v)}>
                <SelectTrigger className="rounded-none mt-1" data-testid="register-role">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="client">Client / Buyer</SelectItem>
                  <SelectItem value="sales">Sales Executive</SelectItem>
                  <SelectItem value="owner">Business Owner</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div>
            <Label>Email</Label>
            <Input type="email" value={form.email} onChange={e => u("email", e.target.value)} placeholder="you@company.com" className="rounded-none mt-1" data-testid="register-email" required />
          </div>
          <div>
            <Label>Password</Label>
            <Input type="password" value={form.password} onChange={e => u("password", e.target.value)} placeholder="Min 6 characters" className="rounded-none mt-1" data-testid="register-password" required />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Company</Label>
              <Input value={form.company_name} onChange={e => u("company_name", e.target.value)} placeholder="Company name" className="rounded-none mt-1" data-testid="register-company" />
            </div>
            <div>
              <Label>State</Label>
              <Select value={form.state} onValueChange={v => u("state", v)}>
                <SelectTrigger className="rounded-none mt-1" data-testid="register-state">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {STATES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>
          <Button type="submit" disabled={loading} className="w-full bg-[#002FA7] text-white rounded-none py-5" data-testid="register-submit-btn">
            {loading ? "Creating..." : "Create Account"}
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-muted-foreground">
          Already have an account? <Link to="/login" className="text-[#002FA7] font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
