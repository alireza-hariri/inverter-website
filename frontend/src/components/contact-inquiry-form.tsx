"use client";
import { useState } from "react";
import { ApiError } from "@/lib/api";
import { submitInquiry } from "@/lib/inquiry-api";
import type { Lang } from "@/lib/i18n";
export default function ContactInquiryForm({ lang, services }: { lang: Lang; services: { slug: string; title: string }[] }) {
  const fa = lang === "fa";
  const [form, setForm] = useState({ name: "", mobile: "", email: "", message: "", service: "" });
  const [fieldErrs, setFieldErrs] = useState<Record<string, string[]>>({});
  const [status, setStatus] = useState<"idle" | "sending" | "ok" | "err">("idle");
  const [msg, setMsg] = useState("");
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));
  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("sending"); setFieldErrs({}); setMsg("");
    try {
      await submitInquiry({ name: form.name, mobile: form.mobile, email: form.email || undefined, message: form.message, service: form.service || undefined, language: lang });
      setStatus("ok"); setMsg(fa ? "درخواست شما با موفقیت ثبت شد. به‌زودی با شما تماس می‌گیریم." : "Your inquiry was submitted. We will call you back soon.");
      setForm({ name: "", mobile: "", email: "", message: "", service: "" });
    } catch (err) {
      setStatus("err");
      if (err instanceof ApiError) { setFieldErrs(err.fieldErrors); setMsg(err.userMessage); }
      else setMsg(fa ? "خطا در ارسال. دوباره تلاش کنید." : "Submission failed. Try again.");
    }
  }
  const L = (faL: string, enL: string) => (fa ? faL : enL);
  return (
    <form onSubmit={onSubmit} className="card p-6 space-y-4">
      {status === "ok" ? <div className="alert-ok">{msg}</div> : null}
      {status === "err" ? <div className="alert-err">{msg}</div> : null}
      <div>
        <label className="text-sm font-bold">{L("نام", "Name")} *</label>
        <input className="field mt-1" value={form.name} onChange={set("name")} required />
        {fieldErrs.name ? <p className="field-err">{fieldErrs.name[0]}</p> : null}
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="text-sm font-bold">{L("موبایل", "Mobile")} *</label>
          <input className="field mt-1" dir="ltr" value={form.mobile} onChange={set("mobile")} required placeholder="0912…" />
          {fieldErrs.mobile ? <p className="field-err">{fieldErrs.mobile[0]}</p> : null}
        </div>
        <div>
          <label className="text-sm font-bold">{L("ایمیل", "Email")}</label>
          <input className="field mt-1" dir="ltr" type="email" value={form.email} onChange={set("email")} />
          {fieldErrs.email ? <p className="field-err">{fieldErrs.email[0]}</p> : null}
        </div>
      </div>
      <div>
        <label className="text-sm font-bold">{L("خدمت موردنظر", "Service")}</label>
        <select className="field mt-1" value={form.service} onChange={set("service")}>
          <option value="">—</option>
          {services.map((s) => (<option key={s.slug} value={s.slug}>{s.title}</option>))}
        </select>
      </div>
      <div>
        <label className="text-sm font-bold">{L("متن پیام", "Message")} *</label>
        <textarea className="field mt-1 min-h-28" value={form.message} onChange={set("message")} required />
        {fieldErrs.message ? <p className="field-err">{fieldErrs.message[0]}</p> : null}
      </div>
      <button className="btn-gold w-full" disabled={status === "sending"}>{status === "sending" ? "…" : L("ثبت درخواست", "Submit request")}</button>
    </form>
  );
}
