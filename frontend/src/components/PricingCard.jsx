import React from 'react'
import { Card, Tag } from 'antd'

/**
 * 收购定价建议卡片（企业落地：优质优价）
 */
export default function PricingCard({ pricing, grade }) {
  if (!pricing) return null

  const gradeText = { high: '优', medium: '中', low: '差' }
  const color = grade === 'high' ? '#34C759' : grade === 'medium' ? '#FF9500' : '#FF3B30'

  return (
    <Card size="small" style={{ marginTop: 16 }} title={
      <span>收购定价建议 <Tag color={color} style={{ marginLeft: 8 }}>{gradeText[grade] || grade}</Tag></span>
    }>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
        <span style={{ fontSize: 32, fontWeight: 700, color }}>¥{pricing.suggested_price?.toFixed(2)}</span>
        <span style={{ fontSize: 13, color: '#6E6E73' }}>/kg（基础价 ¥{pricing.base_price?.toFixed(2)} × {pricing.factor}）</span>
      </div>
      <div style={{ fontSize: 13, color: '#6E6E73', marginTop: 8 }}>
        {pricing.advice}
      </div>
    </Card>
  )
}
