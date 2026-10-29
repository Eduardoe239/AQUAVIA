import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../../lib/api/client";

export function LoginPage() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useMutation({ mutationFn: () => api.login(email, password), onSuccess: () => nav("/app/home") });
  const submit = (e: FormEvent) => { e.preventDefault(); login.mutate(); };
  const err = login.error instanceof ApiError ? login.error : null;
  const msg = err?.status === 429 ? "Muitas tentativas. Aguarde alguns minutos." : err?.status === 0 ? "Sem conexão com o servidor." : err ? "E-mail ou senha incorretos." : null;
  return (
    <main className="page" style={{ maxWidth: 420 }}>
      <img src="/brand/aquavia-logo-horizontal.svg" alt="AQUAVIA" height={44} style={{ display: "block", margin: "0 auto" }} />
      <h1>Entrar</h1>
      <form className="card" onSubmit={submit} noValidate>
        <div className="field"><label htmlFor="email">E-mail</label>
          <input id="email" type="email" autoComplete="username" required value={email} onChange={(e) => setEmail(e.target.value)} /></div>
        <div className="field"><label htmlFor="pw">Senha</label>
          <input id="pw" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} /></div>
        <div aria-live="assertive">{msg && <div className="error" role="alert">{msg}</div>}</div>
        <button className="btn" type="submit" disabled={login.isPending || !email || !password} style={{ marginTop: 12, width: "100%" }}>
          {login.isPending ? "Entrando…" : "Entrar"}
        </button>
      </form>
    </main>
  );
}
