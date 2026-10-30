import React from 'react'
import { Progress } from 'antd'

const CONFIG = {
  low: { label: '低', color: '#cf1322' },
  medium: { label: '中', color: '#faad14' },
  high: { label: '高', color: '#52c41a' },
}
const ORDER = ['low', 'medium', 'high']

export default function ProbBars({ probabilities }) {
  return (
    <div>
      {ORDER.map((k) => (
        <Progress
          key={k}
          percent={Math.round((probabilities[k] || 0) * 100)}
          strokeColor={CONFIG[k].color}
          format={(p) => `${CONFIG[k].label} ${p}%`}
        />
      ))}
    </div>
  )
}
