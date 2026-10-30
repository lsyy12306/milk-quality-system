import React from 'react'

/**
 * 指标相关性热力图（任务书 2.2.2：指标相关性分析）
 * 纯 CSS grid 实现，无需额外图表库。
 * 颜色：正相关蓝 (#007AFF)，负相关橙红 (#FF3B30)，0 为灰。
 */
export default function CorrelationHeatmap({ data }) {
  if (!data || !data.features || !data.matrix) return null

  const features = data.features            // 含 Grade
  const matrix = data.matrix                // n×n
  const isTarget = (i) => i === features.length - 1

  const colorOf = (v) => {
    if (v === null || v === undefined) return '#F5F5F7'
    const a = Math.min(Math.abs(v), 1)
    if (a < 0.02) return '#F5F5F7'
    // 正相关 → 蓝，负相关 → 橙红，透明度按强度
    const base = v > 0 ? '0,122,255' : '255,59,48'
    return `rgba(${base},${(0.15 + a * 0.85).toFixed(2)})`
  }

  const textColor = (v) => {
    const a = Math.abs(v || 0)
    return a > 0.55 ? '#FFFFFF' : '#1D1D1F'
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: `88px repeat(${features.length}, 64px)`,
        gap: 2,
        minWidth: 88 + features.length * 66,
      }}>
        {/* 表头行 */}
        <div />
        {features.map((f, j) => (
          <div key={`h-${j}`} style={{
            fontSize: 12, color: '#6E6E73', textAlign: 'center', padding: '2px 0',
            fontWeight: isTarget(j) ? 700 : 400,
          }}>{f}</div>
        ))}

        {/* 数据行 */}
        {features.map((f, i) => (
          <React.Fragment key={`r-${i}`}>
            <div style={{
              fontSize: 12, color: '#6E6E73', textAlign: 'right', paddingRight: 8,
              lineHeight: '34px', fontWeight: isTarget(i) ? 700 : 400,
            }}>{f}</div>
            {features.map((_, j) => {
              const v = matrix[i]?.[j]
              return (
                <div key={`c-${i}-${j}`} style={{
                  height: 34,
                  background: colorOf(v),
                  borderRadius: 4,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 12, color: textColor(v),
                  fontWeight: isTarget(i) || isTarget(j) ? 600 : 400,
                }} title={`${features[i]} vs ${features[j]}: ${v ?? '—'}`}>
                  {v === null || v === undefined ? '—' : (v === 1 && i === j ? '1' : v.toFixed(2))}
                </div>
              )
            })}
          </React.Fragment>
        ))}
      </div>

      {/* 图例 + 解读 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 12, flexWrap: 'wrap' }}>
        <span style={{ fontSize: 12, color: '#6E6E73' }}>图例：</span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
          <span style={{ width: 12, height: 12, background: 'rgba(0,122,255,0.85)', borderRadius: 3 }} />
          <span style={{ fontSize: 12, color: '#6E6E73' }}>正相关</span>
        </span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
          <span style={{ width: 12, height: 12, background: '#F5F5F7', borderRadius: 3, border: '1px solid #E5E5EA' }} />
          <span style={{ fontSize: 12, color: '#6E6E73' }}>弱相关</span>
        </span>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
          <span style={{ width: 12, height: 12, background: 'rgba(255,59,48,0.85)', borderRadius: 3 }} />
          <span style={{ fontSize: 12, color: '#6E6E73' }}>负相关</span>
        </span>
      </div>
    </div>
  )
}
