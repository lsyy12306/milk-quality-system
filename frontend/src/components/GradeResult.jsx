import React from 'react'
import { Tag, Statistic, Card } from 'antd'

const MAP = {
  low: { text: 'red', label: '低（差）' },
  medium: { text: 'orange', label: '中（一般）' },
  high: { text: 'green', label: '高（优）' },
}

export default function GradeResult({ grade, confidence }) {
  const m = MAP[grade] || MAP.medium
  return (
    <Card title="分级结果">
      <Tag color={m.text} style={{ fontSize: 18, padding: '4px 12px' }}>{m.label}</Tag>
      <Statistic
        title="置信度" value={(confidence * 100).toFixed(2)} suffix="%"
        style={{ marginTop: 16 }}
      />
    </Card>
  )
}
