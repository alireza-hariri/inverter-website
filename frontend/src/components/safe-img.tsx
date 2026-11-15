"use client";

import { useEffect, useRef, useState } from "react";
import Image, { type ImageProps } from "next/image";

/**
 * An <img> that removes itself when the file fails to load, so the styled
 * placeholder behind it shows instead of a broken-image icon and alt text.
 * The effect catches images that failed before hydration.
 */
type SafeImgProps = Omit<ImageProps, "alt" | "src"> & { alt?: string; src?: ImageProps["src"] };

export default function SafeImg({ alt = "", src, ...props }: SafeImgProps) {
  const ref = useRef<HTMLImageElement>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    const img = ref.current;
    if (img && img.complete && img.naturalWidth === 0) setFailed(true);
  }, []);
  if (failed || !src) return null;
  return <Image ref={ref} src={src} alt={alt} {...props} onError={() => setFailed(true)} />;
}
