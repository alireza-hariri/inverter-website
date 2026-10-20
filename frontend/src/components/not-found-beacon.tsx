"use client";
import { useEffect, useRef } from "react";

/** Reports this 404 once, when it is actually shown (see app/api/not-found/route.ts). */
export default function NotFoundBeacon() {
  const sent = useRef(false);
  useEffect(() => {
    if (sent.current) return;
    sent.current = true;
    const body = JSON.stringify({ path: window.location.pathname, referrer: document.referrer });
    if (!navigator.sendBeacon?.("/api/not-found", new Blob([body], { type: "application/json" }))) {
      fetch("/api/not-found", { method: "POST", body, headers: { "Content-Type": "application/json" }, keepalive: true }).catch(() => undefined);
    }
  }, []);
  return null;
}
