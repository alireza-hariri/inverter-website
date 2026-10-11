"use client";
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ApiError } from "@/lib/api";
import { requestMobileCode, signInWithMobileCode } from "@/lib/auth";
import { safeNext, type Lang } from "@/lib/i18n";
export function OtpRequestForm({ lang }: { lang: Lang }) {
  const fa = lang === "fa";
  const router = useRouter();
  const [mobile, setMobile] = useState("");
  const [state, setState] = useState<"idle" | "sending" | "err">("idle");
  const [msg, setMsg] = useState("");
  async function submit(e: React.FormEvent) {
    e.preventDefault(); setState("sending"); setMsg("");
    try {
      await requestMobileCode(mobile);
      router.push("/"+lang+"/login/verify?mobile="+encodeURIComponent(mobile));
    } catch (err) {
      setState("err");
      setMsg(err instanceof ApiError ? err.userMessage : (fa ? "ارسال کد ناموفق بود." : "Could not send the code."));
    }
  }
  return (
    <form onSubmit={submit} className="card p-6 space-y-4">
      {state === "err" ? <div className="alert-err">{msg}</div> : null}
      <div>
        <label className="text-sm font-bold">{fa ? "شماره موبایل" : "Mobile number"}</label>
        <input className="field mt-1" dir="ltr" value={mobile} onChange={(e) => setMobile(e.target.value)} placeholder="0912…" required />
      </div>
      <button className="btn-gold w-full" disabled={state === "sending"}>{fa ? "ارسال کد تایید" : "Send code"}</button>
    </form>
  );
}
export function OtpVerifyForm({ lang }: { lang: Lang }) {
  const fa = lang === "fa";
  const router = useRouter();
  const params = useSearchParams();
  const mobile = params.get("mobile") ?? "";
  const next = safeNext(params.get("next"), lang);
  const [code, setCode] = useState("");
  const [state, setState] = useState<"idle" | "sending" | "err" | "ok">("idle");
  const [msg, setMsg] = useState("");
  const [cooldown, setCooldown] = useState(60);
  useEffect(() => {
    if (cooldown <= 0) return;
    const t = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);
  async function submit(e: React.FormEvent) {
    e.preventDefault(); setState("sending"); setMsg("");
    try {
      await signInWithMobileCode(mobile, code);
      setState("ok"); setMsg(fa ? "ورود موفقیت‌آمیز بود." : "Signed in.");
      router.push(next);
    } catch (err) {
      setState("err");
      setMsg(err instanceof ApiError ? err.userMessage : (fa ? "کد نامعتبر یا منقضی است." : "Invalid or expired code."));
    }
  }
  async function resend() {
    if (cooldown > 0) return;
    try { await requestMobileCode(mobile); setCooldown(60); setMsg(fa ? "کد جدید ارسال شد." : "A new code was sent."); }
    catch (err) { setMsg(err instanceof ApiError ? err.userMessage : (fa ? "ارسال مجدد ناموفق بود." : "Resend failed.")); }
  }
  return (
    <form onSubmit={submit} className="card p-6 space-y-4">
      {state === "err" ? <div className="alert-err">{msg}</div> : null}
      {state === "ok" ? <div className="alert-ok">{msg}</div> : null}
      {state !== "err" && state !== "ok" && msg ? <div className="alert-ok">{msg}</div> : null}
      <p className="text-sm text-slate-500">{fa ? "کد ارسال‌شده به شماره" : "Code sent to"} <bdi dir="ltr">{mobile}</bdi> {fa ? "را وارد کنید." : ""}</p>
      <div>
        <label className="text-sm font-bold">{fa ? "کد تایید" : "Verification code"}</label>
        <input className="field mt-1 text-center text-xl tracking-widest" dir="ltr" value={code} onChange={(e) => setCode(e.target.value)} required inputMode="numeric" />
      </div>
      <button className="btn-gold w-full" disabled={state === "sending"}>{fa ? "تایید و ورود" : "Verify & sign in"}</button>
      <button type="button" className="btn-ghost w-full text-sm" disabled={cooldown > 0} onClick={resend}>
        {cooldown > 0 ? (fa ? "ارسال مجدد تا "+cooldown+" ثانیه" : "Resend in "+cooldown+"s") : (fa ? "ارسال مجدد کد" : "Resend code")}
      </button>
    </form>
  );
}
