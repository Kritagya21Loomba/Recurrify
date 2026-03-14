import { useRef, useEffect } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";

interface MathBlockProps {
  latex: string;
  displayMode?: boolean;
}

export function MathBlock({ latex: tex, displayMode = true }: MathBlockProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current && tex) {
      try {
        katex.render(tex, ref.current, {
          displayMode,
          throwOnError: false,
          errorColor: "#cc0000",
        });
      } catch {
        if (ref.current) {
          ref.current.textContent = tex;
        }
      }
    }
  }, [tex, displayMode]);

  if (!tex) return null;
  return <div ref={ref} className="math-block" />;
}

export function InlineMath({ latex: tex }: { latex: string }) {
  return <MathBlock latex={tex} displayMode={false} />;
}
