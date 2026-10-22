"use client";

import { useEffect, useRef, useState } from "react";

/**
 * An <img> that removes itself when the file fails to load, so the styled
 * placeholder behind it shows instead of a broken-image icon and alt text.
 * The effect catches images that failed before hydration.
 */
export default function SafeImg({ alt = "", ...props }: React.ImgHTMLAttributes<HTMLImageElement>) {
  const ref = useRef<HTMLImageElement>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    const img = ref.current;
    if (img && img.complete && img.naturalWidth === 0) setFailed(true);
  }, []);
  if (failed || !props.src) return null;
  return <img ref={ref} alt={alt} {...props} onError={() => setFailed(true)} />;
}
