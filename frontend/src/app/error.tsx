"use client";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <main className="container-x py-24 text-center">
      <h1 className="text-2xl font-extrabold">خطایی رخ داد / Something went wrong</h1>
      <button className="btn-gold mt-6" onClick={() => reset()}>تلاش مجدد / Retry</button>
    </main>
  );
}
