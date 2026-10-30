import React, { useState } from 'react';

// 1. High-Performance, Visually Balanced Area / Curve Chart
export const AreaChart = ({ data, height = 240 }) => {
  const [hoveredPoint, setHoveredPoint] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div style={{ color: '#64748B', padding: '40px', textAlign: 'center' }}>
        No sales trend data recorded yet.
      </div>
    );
  }

  const values = data.map(d => Number(d.revenue) || 0);

  // Balanced scaling: Sort values to identify median and 90th percentile
  // This prevents 1 massive single-day outlier from squashing all regular daily peaks to 0
  const sorted = [...values].filter(v => v > 0).sort((a, b) => a - b);
  const p95 = sorted.length > 0 ? sorted[Math.floor(sorted.length * 0.92)] : 5000;
  const effectiveMax = Math.max(p95 * 1.35, 100);

  const paddingLeft = 55;
  const paddingRight = 30;
  const paddingTop = 25;
  const paddingBottom = 35;
  const chartWidth = 620;
  const chartHeight = height;

  const usableWidth = chartWidth - paddingLeft - paddingRight;
  const usableHeight = chartHeight - paddingTop - paddingBottom;

  // Scale function with gentle square-root damping for high outliers
  const getY = (val) => {
    if (val <= 0) return chartHeight - paddingBottom;
    const ratio = Math.min(1.0, val / effectiveMax);
    const scaledRatio = Math.pow(ratio, 0.72);
    return chartHeight - paddingBottom - (scaledRatio * usableHeight);
  };

  const getX = (idx) => {
    return paddingLeft + (idx / Math.max(data.length - 1, 1)) * usableWidth;
  };

  const coords = data.map((d, idx) => ({
    x: getX(idx),
    y: getY(Number(d.revenue) || 0),
    data: d
  }));

  // Build smooth cubic Bézier curve SVG path
  let pathD = `M ${coords[0].x} ${coords[0].y}`;
  for (let i = 0; i < coords.length - 1; i++) {
    const current = coords[i];
    const next = coords[i + 1];
    const cp1x = current.x + (next.x - current.x) * 0.45;
    const cp1y = current.y;
    const cp2x = current.x + (next.x - current.x) * 0.55;
    const cp2y = next.y;
    pathD += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${next.x} ${next.y}`;
  }

  // Area closing path down to baseline
  const baselineY = chartHeight - paddingBottom;
  const areaD = `${pathD} L ${coords[coords.length - 1].x} ${baselineY} L ${coords[0].x} ${baselineY} Z`;

  // Find top 3 peak points to highlight visually
  const peakIndices = [...coords]
    .map((c, idx) => ({ ...c, originalIdx: idx, rev: Number(c.data.revenue) || 0 }))
    .sort((a, b) => b.rev - a.rev)
    .slice(0, 3)
    .map(p => p.originalIdx);

  // Y-axis tick values (4 steps)
  const yTicks = [0, 0.33, 0.66, 1.0].map(pct => {
    const val = Math.round(effectiveMax * Math.pow(pct, 1 / 0.72));
    const y = chartHeight - paddingBottom - pct * usableHeight;
    return { val, y };
  });

  return (
    <div style={{ position: 'relative', width: '100%', overflowX: 'auto' }}>
      <svg
        viewBox={`0 0 ${chartWidth} ${chartHeight}`}
        style={{ width: '100%', height: 'auto', maxHeight: height, display: 'block' }}
      >
        <defs>
          <linearGradient id="curveGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#6366F1" stopOpacity="0.25" />
            <stop offset="60%" stopColor="#E0E7FF" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0.0" />
          </linearGradient>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="2.5" floodColor="#6366F1" floodOpacity="0.25" />
          </filter>
        </defs>

        {/* Horizontal grid lines & Y labels */}
        {yTicks.map((tick, i) => (
          <g key={i}>
            <line
              x1={paddingLeft}
              y1={tick.y}
              x2={chartWidth - paddingRight}
              y2={tick.y}
              stroke="#E9EAF3"
              strokeDasharray={i === 0 ? "none" : "3 3"}
              strokeOpacity={i === 0 ? 1 : 0.8}
            />
            <text
              x={paddingLeft - 10}
              y={tick.y + 4}
              fill="#64748B"
              fontSize="10"
              fontWeight="600"
              textAnchor="end"
            >
              ₹{tick.val >= 1000 ? `${(tick.val / 1000).toFixed(1)}k` : tick.val}
            </text>
          </g>
        ))}

        {/* Gradient Area Fill */}
        <path d={areaD} fill="url(#curveGradient)" />

        {/* Smooth Lavender Line */}
        <path
          d={pathD}
          fill="none"
          stroke="#6366F1"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          filter="url(#glow)"
        />

        {/* Data points & Prominent Peak Markers */}
        {coords.map((c, idx) => {
          const isPeak = peakIndices.includes(idx);
          const isHovered = hoveredPoint && hoveredPoint.idx === idx;
          const rev = Number(c.data.revenue) || 0;

          return (
            <g
              key={idx}
              onMouseEnter={() => setHoveredPoint({ ...c, idx })}
              onMouseLeave={() => setHoveredPoint(null)}
              style={{ cursor: 'pointer' }}
            >
              {/* Peak indicator halo */}
              {isPeak && (
                <circle
                  cx={c.x}
                  cy={c.y}
                  r="7"
                  fill="#6366F1"
                  fillOpacity="0.18"
                />
              )}

              {/* Point circle */}
              <circle
                cx={c.x}
                cy={c.y}
                r={isHovered ? 6 : isPeak ? 4.5 : 3}
                fill={isHovered ? '#059669' : isPeak ? '#6366F1' : '#4F46E5'}
                stroke="#FFFFFF"
                strokeWidth="2"
              />

              {/* Label top peak */}
              {isPeak && !isHovered && (
                <text
                  x={c.x}
                  y={c.y - 10}
                  fill="#4F46E5"
                  fontSize="9"
                  fontWeight="800"
                  textAnchor="middle"
                >
                  ₹{rev >= 1000 ? `${(rev / 1000).toFixed(1)}k` : rev.toFixed(0)}
                </text>
              )}
            </g>
          );
        })}

        {/* X-axis date labels */}
        {data.length > 0 && (
          <>
            <text x={paddingLeft} y={chartHeight - 10} fill="#64748B" fontSize="10" textAnchor="start">
              {data[0].date}
            </text>
            {data.length > 2 && (
              <text x={chartWidth / 2} y={chartHeight - 10} fill="#64748B" fontSize="10" textAnchor="middle">
                {data[Math.floor(data.length / 2)].date}
              </text>
            )}
            <text x={chartWidth - paddingRight} y={chartHeight - 10} fill="#64748B" fontSize="10" textAnchor="end">
              {data[data.length - 1].date}
            </text>
          </>
        )}
      </svg>

      {/* Interactive Tooltip Card */}
      {hoveredPoint && (
        <div style={{
          position: 'absolute',
          top: Math.max(10, hoveredPoint.y - 50),
          left: Math.min(chartWidth - 140, Math.max(20, hoveredPoint.x - 60)),
          background: '#FFFFFF',
          border: '1px solid #E9EAF3',
          borderRadius: '8px',
          padding: '8px 12px',
          color: '#1E293B',
          fontSize: '11px',
          pointerEvents: 'none',
          boxShadow: '0 10px 25px -5px rgba(99, 102, 241, 0.15)',
          zIndex: 10
        }}>
          <div style={{ color: '#64748B', fontSize: '10px', marginBottom: '2px' }}>{hoveredPoint.data.date}</div>
          <div style={{ color: '#059669', fontWeight: '800', fontSize: '13px' }}>
            ₹{Number(hoveredPoint.data.revenue || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ color: '#6366F1', fontSize: '10px', marginTop: '2px', fontWeight: '500' }}>
            {hoveredPoint.data.transactions_count || 1} orders placed
          </div>
        </div>
      )}
    </div>
  );
};

// 2. Category Distribution Donut Chart
export const DonutChart = ({ data, size = 200 }) => {
  if (!data || data.length === 0) {
    return <div style={{ color: '#64748B', padding: '40px', textAlign: 'center' }}>No category data available.</div>;
  }

  const colors = ['#6366F1', '#818CF8', '#059669', '#D97706', '#3B82F6', '#8B5CF6', '#14B8A6', '#EC4899'];
  const total = data.reduce((acc, d) => acc + (Number(d.revenue) || 0), 0) || 1;

  let currentAngle = 0;
  const radius = 65;
  const innerRadius = 40;
  const cx = 100;
  const cy = 100;

  const slices = data.map((d, i) => {
    const val = Number(d.revenue) || 0;
    const sliceAngle = (val / total) * 360;
    const startAngle = currentAngle;
    const endAngle = currentAngle + sliceAngle;
    currentAngle = endAngle;

    const startRad = (startAngle - 90) * (Math.PI / 180);
    const endRad = (endAngle - 90) * (Math.PI / 180);

    const x1 = cx + radius * Math.cos(startRad);
    const y1 = cy + radius * Math.sin(startRad);
    const x2 = cx + radius * Math.cos(endRad);
    const y2 = cy + radius * Math.sin(endRad);

    const ix1 = cx + innerRadius * Math.cos(endRad);
    const iy1 = cy + innerRadius * Math.sin(endRad);
    const ix2 = cx + innerRadius * Math.cos(startRad);
    const iy2 = cy + innerRadius * Math.sin(startRad);

    const largeArc = sliceAngle > 180 ? 1 : 0;
    const pathData = `
      M ${x1} ${y1}
      A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}
      L ${ix1} ${iy1}
      A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${ix2} ${iy2}
      Z
    `;

    return {
      category: d.category,
      revenue: val,
      pct: ((val / total) * 100).toFixed(1),
      path: pathData,
      color: colors[i % colors.length]
    };
  });

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap', justifyContent: 'center' }}>
      <svg width={size} height={size} viewBox="0 0 200 200">
        {slices.map((s, idx) => (
          <path key={idx} d={s.path} fill={s.color}>
            <title>{`${s.category}: ₹${s.revenue.toFixed(2)} (${s.pct}%)`}</title>
          </path>
        ))}
        <text x="100" y="96" textAnchor="middle" fill="#64748B" fontSize="10" fontWeight="600">TOTAL</text>
        <text x="100" y="112" textAnchor="middle" fill="#1E293B" fontSize="13" fontWeight="800">
          ₹{total >= 1000 ? `${(total/1000).toFixed(1)}k` : total.toFixed(0)}
        </text>
      </svg>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '11px', maxHeight: size, overflowY: 'auto' }}>
        {slices.map((s, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '3px', background: s.color, display: 'inline-block' }}></span>
            <span style={{ color: '#1E293B', minWidth: '85px', fontWeight: '500' }}>{s.category}</span>
            <span style={{ color: '#64748B', fontWeight: '600' }}>{s.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// 3. Simple Bar Chart for Vendor Comparison
export const BarChart = ({ data, xKey = 'business_name', yKey = 'total_revenue', height = 200 }) => {
  if (!data || data.length === 0) {
    return <div style={{ color: '#64748B', padding: '40px', textAlign: 'center' }}>No comparison data available.</div>;
  }

  const values = data.map(d => Number(d[yKey]) || 0);
  const maxVal = Math.max(...values, 100);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', paddingTop: '10px' }}>
      {data.slice(0, 7).map((item, idx) => {
        const val = Number(item[yKey]) || 0;
        const pct = Math.min(100, Math.max(5, (val / maxVal) * 100));
        return (
          <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px' }}>
            <span style={{ width: '130px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: '#1E293B', fontWeight: '500' }} title={item[xKey]}>
              {item[xKey]}
            </span>
            <div style={{ flex: 1, background: '#E9EAF3', borderRadius: '4px', height: '18px', overflow: 'hidden' }}>
              <div style={{ width: `${pct}%`, height: '100%', background: 'linear-gradient(90deg, #6366F1, #818CF8)', borderRadius: '4px' }}></div>
            </div>
            <span style={{ minWidth: '70px', textAlign: 'right', fontWeight: '700', color: '#059669' }}>
              ₹{val.toLocaleString('en-IN')}
            </span>
          </div>
        );
      })}
    </div>
  );
};
