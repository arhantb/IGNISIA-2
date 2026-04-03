import axios from "axios";

const API_BASE = process.env.REACT_APP_BACKEND_URL;
export const API = `${API_BASE}/api`;

const api = axios.create({
  baseURL: API,
  withCredentials: true,
});

// Attach token from localStorage as fallback
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("sq_token");
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function formatApiError(detail) {
  if (detail == null) return "Something went wrong.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail.map((e) => (e?.msg ? e.msg : JSON.stringify(e))).join(" ");
  if (detail?.msg) return detail.msg;
  return String(detail);
}

export function formatINR(amount) {
  if (!amount && amount !== 0) return "0";
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(amount);
}

export function formatCurrency(amount, currency = "INR") {
  const symbols = { INR: "\u20B9", USD: "$", EUR: "\u20AC", AED: "AED " };
  return `${symbols[currency] || ""}${formatINR(amount)}`;
}

export const STATUS_COLORS = {
  SUBMITTED: "bg-blue-100 text-blue-800",
  PARSING: "bg-yellow-100 text-yellow-800",
  PARSED: "bg-cyan-100 text-cyan-800",
  PRICED: "bg-indigo-100 text-indigo-800",
  PENDING_APPROVAL: "bg-orange-100 text-orange-800",
  APPROVED: "bg-green-100 text-green-800",
  REJECTED: "bg-red-100 text-red-800",
  SHARED_WITH_CLIENT: "bg-purple-100 text-purple-800",
  CLIENT_APPROVED: "bg-emerald-100 text-emerald-800",
  CLIENT_REVISION: "bg-amber-100 text-amber-800",
  CLOSED_LOST: "bg-gray-100 text-gray-800",
  REVISION_REQUESTED: "bg-amber-100 text-amber-800",
};

export const STRATEGY_STYLES = {
  STANDARD: { bg: "strategy-standard", label: "Standard Margin", icon: "check-circle" },
  DEFEND_MARGIN: { bg: "strategy-defend", label: "Defend Margin", icon: "shield" },
  VALUE_DEFENSE: { bg: "strategy-value", label: "Value Differentiation", icon: "star" },
  PREMIUM_URGENCY: { bg: "strategy-premium", label: "Premium Urgency", icon: "zap" },
};

export default api;
