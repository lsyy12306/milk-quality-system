import React from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList,
} from 'recharts'

export default function FeatureImportanceChart({ data }) {
  const arr = Object.entries(data || {})
    .map(([name, value]) => ({ name, value: Number(value) }))
    .sort((a, b) => a.value - b.value) // 横向条形从下到上递增
  const max = Math.max(...arr.map((d) => d.value), 0.1)

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={arr} layout="vertical" margin={{ left: 60, right: 30 }}>
        <XAxis type="number" domain={[0, max]} />
        <YAxis type="category" dataKey="name" width={90} />
        <Tooltip formatter={(v) => v.toFixed(4)} />
        <Bar dataKey="value" fill="#4C72B0">
          <LabelList dataKey="value" position="right" formatter={(v) => Number(v).toFixed(3)} />
          {arr.map((_, i) => <Cell key={i} fill="#4C72B0" />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
