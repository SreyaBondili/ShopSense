import React from 'react';

/**
 * AnimatedCounter: Formats financial and metric numbers statically without counting animation.
 * - Formats numbers with Indian currency standards (en-IN).
 * - Instant display without delay or counting animation.
 */
export default function AnimatedCounter({
  value = 0,
  prefix = '',
  suffix = '',
  decimals = 0,
  className = '',
  style = {}
}) {
  const targetVal = Number(value) || 0;
  const formattedNum = targetVal.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return (
    <span className={className} style={{ display: 'inline-block', fontVariantNumeric: 'tabular-nums', ...style }}>
      {prefix}{formattedNum}{suffix}
    </span>
  );
}

