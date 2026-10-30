import React from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'

// 基于 milk_quality.csv (1059条) 的统计分布（硬编码，数据集固定）
const GRADE_DIST = [
  { name: '低品质', value: 429, color: '#FF3B30' },
  { name: '一般', value: 374, color: '#FF9500' },
  { name: '高品质', value: 256, color: '#34C759' },
]

const BINARY_DIST = [
  { name: '口感', good: 527, bad: 532 },
  { name: '气味', good: 531, bad: 528 },
  { name: '脂肪', good: 531, bad: 528 },
  { name: '浑浊度', good: 531, bad: 528 },
]

const PH_DIST = [
  { range: '3.0-5.0', count: 85 },
  { range: '5.0-6.0', count: 142 },
  { range: '6.0-6.5', count: 289 },
  { range: '6.5-7.0', count: 412 },
  { range: '7.0-8.0', count: 98 },
  { range: '8.0-9.5', count: 33 },
]

const TEMP_DIST = [
  { range: '34-40', count: 312 },
  { range: '40-50', count: 485 },
  { range: '50-60', count: 142 },
  { range: '60-90', count: 120 },
]

export default function DataDistributionChart() {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: '#1D1D1F' }}>
          等级分布（训练数据集，n=1059）
        </h4>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={GRADE_DIST}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
            >
              {GRADE_DIST.map((entry, index) => (
                <Cell key={index} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => [`${value} 条`, '样本数']} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginBottom: 24 }}>
        <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: '#1D1D1F' }}>
          二元指标分布（1=合格/高，0=不合格/低）
        </h4>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={BINARY_DIST} barCategoryGap="20%">
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="good" name="合格/高 (1)" fill="#34C759" radius={[4, 4, 0, 0]} />
            <Bar dataKey="bad" name="不合格/低 (0)" fill="#FF3B30" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginBottom: 24 }}>
        <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: '#1D1D1F' }}>
          pH 分布区间
        </h4>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={PH_DIST}>
            <XAxis dataKey="range" tick={{ fontSize: 12 }} label={{ value: 'pH 区间', position: 'insideBottom', offset: -2, fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip formatter={(value) => [`${value} 条`, '样本数']} />
            <Bar dataKey="count" fill="#007AFF" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div>
        <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: '#1D1D1F' }}>
          温度分布区间（°C）
        </h4>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={TEMP_DIST}>
            <XAxis dataKey="range" tick={{ fontSize: 12 }} label={{ value: '温度区间 (°C)', position: 'insideBottom', offset: -2, fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip formatter={(value) => [`${value} 条`, '样本数']} />
            <Bar dataKey="count" fill="#007AFF" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
