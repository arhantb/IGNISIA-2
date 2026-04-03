import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { formatApiError } from "@/lib/api";
import { Lightning } from "@phosphor-icons/react";

const LOGO_URL = "https://customer-assets.emergentagent.com/job_smartquote-engine/artifacts/ls74viwp_Screenshot%202026-04-03%20194540.png";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await login(email, password);
      navigate(data.role === "client" ? "/client" : "/dashboard");
    } catch (err) {
      setError(formatApiError(err.response?.data?.detail) || err.message);
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (em, pw) => { setEmail(em); setPassword(pw); };

  return (
    <div className="min-h-screen flex" data-testid="login-page">
      <div className="hidden lg:flex lg:w-1/2 bg-[#0A0A0B] items-center justify-center p-12">
        <div className="max-w-md">
          <img src={LOGO_URL} alt="RFPFlow" className="h-14 w-auto mb-8" />
          <h2 className="font-['Chivo'] text-4xl font-black text-white tracking-tight mb-4">
            RFPFlow<br />Orchestrator
          </h2>
          <p className="text-gray-400 text-base leading-relaxed">
            Autonomous RFP response engine for Indian MSMEs. Parse, price, compete, and close faster.
          </p>
          <div className="mt-8 space-y-3">
            {["RFP parsing in seconds", "5 competitor benchmarks per SKU", "GST-compliant PDF quotations", "Owner approval workflows"].map((f, i) => (
              <div key={i} className="flex items-center gap-3 text-gray-300 text-sm">
                <div className="w-1.5 h-1.5 bg-[#002FA7]" />
                {f}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <img src={LOGO_URL} alt="RFPFlow" className="h-8 w-auto" />
            <span className="font-['Chivo'] font-black text-lg">RFPFlow</span>
          </div>

          <h1 className="font-['Chivo'] text-3xl font-black tracking-tight mb-2">Sign in</h1>
          <p className="text-muted-foreground mb-8">Enter your credentials to access RFPFlow</p>

          {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-3 mb-4" data-testid="login-error">{error}</div>}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" className="rounded-none mt-1" data-testid="login-email" required />
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter password" className="rounded-none mt-1" data-testid="login-password" required />
            </div>
            <Button type="submit" disabled={loading} className="w-full bg-[#002FA7] text-white rounded-none py-5" data-testid="login-submit-btn">
              {loading ? "Signing in..." : "Sign In"}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-muted-foreground">
            No account? <Link to="/register" className="text-[#002FA7] font-medium">Register here</Link>
          </div>

          {/* Demo accounts */}
          <div className="mt-8 border-t border-border/40 pt-6">
            <p className="text-label mb-3">Demo Accounts</p>
            <div className="grid grid-cols-2 gap-2">
              {[
                { label: "Admin", email: "admin@smartquote.in", pw: "Admin@123" },
                { label: "Owner", email: "owner@smartquote.in", pw: "Owner@123" },
                { label: "Sales", email: "sales@smartquote.in", pw: "Sales@123" },
                { label: "Client", email: "client@pmc.gov.in", pw: "Client@123" },
              ].map((d) => (
                <button key={d.label} onClick={() => fillDemo(d.email, d.pw)} className="text-left border border-border/50 p-2 text-xs hover:bg-muted/50 transition-colors" data-testid={`demo-${d.label.toLowerCase()}`}>
                  <div className="font-medium">{d.label}</div>
                  <div className="text-muted-foreground truncate">{d.email}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
