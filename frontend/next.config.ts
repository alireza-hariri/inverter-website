import type { NextConfig } from "next";
const devOrigins = (process.env.ALLOWED_DEV_ORIGINS ?? "").split(",").map((h) => h.trim()).filter(Boolean);
const nextConfig: NextConfig = {
  allowedDevOrigins: ["localhost", "127.0.0.1", ...devOrigins],
  images: { unoptimized: true },
};
export default nextConfig;
