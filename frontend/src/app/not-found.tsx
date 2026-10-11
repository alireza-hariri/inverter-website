import Link from "next/link";
export default function NotFound() {
  return (
    <main className="container-x py-24 text-center">
      <h1 className="text-3xl font-extrabold">صفحه پیدا نشد / Page not found</h1>
      <p className="mt-3 text-slate-500">صفحه موردنظر وجود ندارد.</p>
      <div className="mt-6 flex gap-3 justify-center">
        <Link className="btn-gold" href="/fa">خانه فارسی</Link>
        <Link className="btn-ghost" href="/en">English home</Link>
      </div>
    </main>
  );
}
