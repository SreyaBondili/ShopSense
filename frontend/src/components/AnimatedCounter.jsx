import React, { useState, useEffect, useRef } from 'react';

/**
 * AnimatedCounter: Smoothly animates financial and metric numbers.
 * - Duration: 1.0 - 1.5 seconds with cubic ease-out.
 * - Formats numbers with Indian currency standards (en-IN).
 * - Avoids re-render flicker and respects reduced-motion settings.
 */
export default function AnimatedCounter({
  value = 0,
  duration = 1200,
  prefix = '',
  suffix = '',
  decimals = 0,
  className = '',
  style = {}
}) {
  const targetVal = Number(value) || 0;
  const [displayVal, setDisplayVal] = useState(0);
  const prevValRef = useRef(0);
  const animFrameRef = useRef(null);

  useEffect(() => {
    // Check if user prefers reduced motion
    const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      setDisplayVal(targetVal);
      prevValRef.current = targetVal;
      return;
    }

    const startVal = prevValRef.current;
    const diff = targetVal - startVal;
    if (diff === 0) return;

    let startTime = null;

    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const elapsed = timestamp - startTime;
      const progress = Math.min(1.0, elapsed / duration);

      // Cubic ease-out: 1 - (1 - progress)^3
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = startVal + diff * easeOut;

      setDisplayVal(current);

      if (progress < 1.0) {
        animFrameRef.current = requestAnimationFrame(animate);
      } else {
        setDisplayVal(targetVal);
        prevValRef.current = targetVal;
      }
    };

    animFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
      }
    };
  }, [targetVal, duration]);

  const formattedNum = displayVal.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return (
    <span className={className} style={{ display: 'inline-block', fontVariantNumeric: 'tabular-nums', ...style }}>
      {prefix}{formattedNum}{suffix}
    </span>
  );
}
