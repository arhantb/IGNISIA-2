import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Lightning, ShieldCheck, ChartLineUp, FileText } from "@phosphor-icons/react";

export default function Landing() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleGetStarted = () => {
    if (user && user.role) {
      navigate(user.role === "client" ? "/client" : "/dashboard");
    } else {
      navigate("/login");
    }
  };

  return (
    <div className="min-h-screen bg-white" data-testid="landing-page">
      {/* Nav */}
      <nav className="bg-white/70 backdrop-blur-xl border-b border-border/40 fixed w-full z-50" data-testid="landing-nav">
        <div className="max-w-7xl mx-auto px-6 md:px-12 flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#002FA7] flex items-center justify-center">
              <Lightning weight="bold" className="text-white w-5 h-5" />
            </div>
            <span className="font-['Chivo'] font-black text-lg tracking-tight">SmartQuote</span>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" className="rounded-none" onClick={() => navigate("/login")} data-testid="login-nav-btn">
              Sign In
            </Button>
            <Button className="bg-[#002FA7] text-white rounded-none hover:bg-[#002FA7]/90" onClick={() => navigate("/register")} data-testid="register-nav-btn">
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6 md:px-12 lg:px-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#002FA7]/5 via-transparent to-transparent" />
        <div className="max-w-7xl mx-auto relative">
          <div className="max-w-3xl">
            <p className="text-label mb-4 animate-fade-in">Autonomous RFP Response Engine</p>
            <h1 className="font-['Chivo'] text-4xl sm:text-5xl lg:text-6xl font-black tracking-tighter leading-[1.05] mb-6 animate-slide-up">
              Turn RFPs into<br />
              <span className="text-[#002FA7]">winning quotations</span><br />
              in minutes, not days.
            </h1>
            <p className="text-base md:text-lg text-muted-foreground max-w-xl mb-8 animate-slide-up" style={{ animationDelay: "0.1s" }}>
              AI-powered multi-agent pipeline that parses RFPs, matches products, analyzes competitors,
              and generates GST-compliant Indian business quotations autonomously.
            </p>
            <div className="flex flex-wrap gap-3 animate-slide-up" style={{ animationDelay: "0.2s" }}>
              <Button
                className="bg-[#002FA7] text-white rounded-none px-8 py-6 text-base hover:bg-[#002FA7]/90"
                onClick={handleGetStarted}
                data-testid="get-started-btn"
              >
                Start Processing RFPs <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
              <Button
                variant="outline"
                className="rounded-none px-8 py-6 text-base border-border/50"
                onClick={() => navigate("/register")}
                data-testid="submit-rfp-btn"
              >
                Submit an RFP
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-border/40 bg-muted/30">
        <div className="max-w-7xl mx-auto px-6 md:px-12 grid grid-cols-2 md:grid-cols-4 divide-x divide-border/40">
          {[
            { value: "<7 min", label: "Quote Generation" },
            { value: "30+", label: "SKU Catalog" },
            { value: "5", label: "Competitor Sources" },
            { value: "100%", label: "GST Compliant" },
          ].map((s, i) => (
            <div key={i} className="py-8 px-6 text-center">
              <div className="font-mono text-2xl sm:text-3xl font-semibold tracking-tight">{s.value}</div>
              <div className="text-label mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6 md:px-12 lg:px-24">
        <div className="max-w-7xl mx-auto">
          <p className="text-label mb-3">Multi-Agent Pipeline</p>
          <h2 className="font-['Chivo'] text-3xl sm:text-4xl font-bold tracking-tight mb-12">
            Six intelligent agents.<br />One seamless workflow.
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
            {[
              { icon: <FileText weight="bold" className="w-6 h-6" />, title: "RFP Parser", desc: "AI-powered extraction of requirements, specs, deadlines from any format. Gemini 3 Flash NLP engine." },
              { icon: <ChartLineUp weight="bold" className="w-6 h-6" />, title: "Pricing Engine", desc: "Deterministic rules engine. SKU matching, volume discounts, urgency premiums. No LLM decides price." },
              { icon: <ShieldCheck weight="bold" className="w-6 h-6" />, title: "Competitor Intel", desc: "5 competitor benchmarks per SKU. Auto value-defense when competitor undercuts base cost." },
              { icon: <Lightning weight="bold" className="w-6 h-6" />, title: "Strategy Agent", desc: "STANDARD / DEFEND / VALUE_DEFENSE / PREMIUM. Autonomous pricing strategy selection." },
              { icon: <ShieldCheck weight="bold" className="w-6 h-6" />, title: "Governance", desc: "Auto-approval for safe quotes. Owner escalation for risky margins, exports, or below-cost competitors." },
              { icon: <FileText weight="bold" className="w-6 h-6" />, title: "PDF Generator", desc: "Indian business standard. GSTIN, HSN/SAC, CGST/SGST/IGST, bank details. WeasyPrint powered." },
            ].map((f, i) => (
              <div key={i} className="border border-border/50 p-6 hover:-translate-y-1 hover:shadow-md transition-all duration-200 animate-slide-up" style={{ animationDelay: `${i * 0.05}s` }}>
                <div className="w-10 h-10 bg-[#002FA7] text-white flex items-center justify-center mb-4">
                  {f.icon}
                </div>
                <h3 className="font-['Chivo'] text-lg font-bold mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-[#0A0A0B] text-white py-20 px-6 md:px-12">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="font-['Chivo'] text-3xl sm:text-4xl font-bold tracking-tight mb-4">
            Built for Indian SMEs. Ready to deploy.
          </h2>
          <p className="text-gray-400 mb-8 max-w-xl mx-auto">
            From MSME tenders to international exports. GST-compliant, multi-currency, approval workflows built in.
          </p>
          <Button className="bg-[#002FA7] text-white rounded-none px-10 py-6 text-base" onClick={handleGetStarted} data-testid="cta-get-started">
            Launch SmartQuote <ArrowRight className="ml-2" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/40 py-8 px-6 md:px-12">
        <div className="max-w-7xl mx-auto flex justify-between items-center text-sm text-muted-foreground">
          <span>SmartQuote Electric Pvt. Ltd. GSTIN: 27AABCS1429B1ZS</span>
          <span>Hackathon Demo Build</span>
        </div>
      </footer>
    </div>
  );
}
