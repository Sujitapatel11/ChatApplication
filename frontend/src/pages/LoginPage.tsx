import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function LoginPage() {
  const [tab, setTab] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      if (tab === "login") {
        await login(email, password);
        navigate("/");
      } else {
        await register(username, email, password);
        await login(email, password);
        navigate("/");
      }
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg ?? "Something went wrong");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-sky-500 mb-3">
            <span className="text-3xl">💬</span>
          </div>
          <h1 className="text-2xl font-bold text-white">FirstChat</h1>
          <p className="text-slate-400 text-sm mt-1">Real-time messaging</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          {/* Tabs */}
          <div className="flex bg-slate-800 rounded-xl p-1 mb-6">
            {(["login", "register"] as const).map(t => (
              <button key={t} onClick={() => { setTab(t); setError(""); }}
                className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${
                  tab === t ? "bg-sky-500 text-white" : "text-slate-400 hover:text-white"}`}>
                {t === "login" ? "Sign In" : "Sign Up"}
              </button>
            ))}
          </div>

          <form onSubmit={submit} className="space-y-4">
            {tab === "register" && (
              <input value={username} onChange={e => setUsername(e.target.value)}
                placeholder="Username" required minLength={3} maxLength={32}
                pattern="^[a-zA-Z0-9_]+"
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3
                           text-white text-sm placeholder-slate-500 focus:outline-none focus:border-sky-500" />
            )}
            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
              placeholder="Email" required
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3
                         text-white text-sm placeholder-slate-500 focus:outline-none focus:border-sky-500" />
            <input type="password" value={password} onChange={e => setPassword(e.target.value)}
              placeholder="Password" required minLength={6}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3
                         text-white text-sm placeholder-slate-500 focus:outline-none focus:border-sky-500" />

            {error && <p className="text-red-400 text-sm bg-red-950/40 border border-red-800 rounded-xl px-3 py-2">{error}</p>}

            <button type="submit" disabled={loading}
              className="w-full bg-sky-500 hover:bg-sky-400 text-white rounded-xl py-3 text-sm
                         font-semibold transition-colors disabled:opacity-50">
              {loading ? "Please wait…" : tab === "login" ? "Sign In" : "Create Account"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
