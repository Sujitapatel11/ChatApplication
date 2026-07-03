import { useEffect, useState } from "react";
import api from "../services/api";

export interface AuthUser {
  id: string; username: string; email: string;
  display_name: string | null; profile_picture: string | null; online: boolean;
}

let _user: AuthUser | null = null;
let _loading = true;
const _subs = new Set<() => void>();
const notify = () => _subs.forEach(f => f());

export function useAuth() {
  const [, rerender] = useState(0);

  useEffect(() => {
    const fn = () => rerender(n => n + 1);
    _subs.add(fn);
    return () => { _subs.delete(fn); };
  }, []);

  useEffect(() => {
    if (!localStorage.getItem("fc_token")) { _loading = false; notify(); return; }
    api.get("/auth/me")
      .then(r => { _user = r.data; })
      .catch(() => { localStorage.removeItem("fc_token"); _user = null; })
      .finally(() => { _loading = false; notify(); });
  }, []);

  const login = async (email: string, password: string) => {
    const { data } = await api.post("/auth/login", { email, password });
    localStorage.setItem("fc_token", data.access_token);
    const me = await api.get("/auth/me");
    _user = me.data; notify();
  };

  const register = async (username: string, email: string, password: string) => {
    await api.post("/auth/register", { username, email, password });
  };

  const logout = () => {
    localStorage.removeItem("fc_token");
    _user = null; notify();
  };

  return { user: _user, loading: _loading, login, register, logout };
}
