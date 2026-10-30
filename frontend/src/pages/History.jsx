import React, { useEffect, useState, useMemo } from 'react'
import { Table, Button, Card, message, Empty, Row, Col, Statistic, Select, Tag, Space } from 'antd'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import { getHistory, getHistoryBatches, exportHistory, fmtBeijing } from '../api'

const GRADE_COLORS = {
  low: '#FF3B30',
  medium: '#FF9500',
  high: '#34C759',
}

const GRADE_LABELS = {
  low: '低品质',
  medium: '一般',
  high: '高品质',
}

export default function History() {
  const [data, setData] = useState([])
  const [batches, setBatches] = useState([])
  const [batchFilter, setBatchFilter] = useState(null)
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const [r, b] = await Promise.all([getHistory(), getHistoryBatches()])
      setData(r.data)
      setBatches(b.data)
    } catch (e) {
      message.error('加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const onExport = async () => {
    try {
      const r = await exportHistory(batchFilter || undefined)
      const url = window.URL.createObjectURL(new Blob([r.data], { type: 'text/csv' }))
      const a = document.createElement('a')
      a.href = url
      const safe = batchFilter ? batchFilter.replace(/^b:|^t:/, '').replace(/[^\w-]/g, '') : ''
      a.download = safe ? `grade_history_${safe}.csv` : 'grade_history.csv'
      a.click()
      window.URL.revokeObjectURL(url)
      message.success(batchFilter ? '已导出所选批次' : '已导出全部历史')
    } catch (e) {
      message.error('导出失败')
    }
  }

  // 按批次筛选（批次分组键由后端写入 batch_key）
  const filtered = useMemo(
    () => (batchFilter ? data.filter((r) => r.batch_key === batchFilter) : data),
    [data, batchFilter]
  )

  // 品质波动分析
  const distribution = useMemo(() => {
    const counts = { low: 0, medium: 0, high: 0 }
    data.forEach((r) => {
      if (counts[r.predicted_grade] !== undefined) {
        counts[r.predicted_grade] += 1
      }
    })
    return [
      { grade: '低品质', key: 'low', count: counts.low, color: GRADE_COLORS.low },
      { grade: '一般', key: 'medium', count: counts.medium, color: GRADE_COLORS.medium },
      { grade: '高品质', key: 'high', count: counts.high, color: GRADE_COLORS.high },
    ]
  }, [data])

  const advice = useMemo(() => {
    const total = data.length
    if (total === 0) return null
    const lowRatio = distribution.find((d) => d.key === 'low').count / total
    const highRatio = distribution.find((d) => d.key === 'high').count / total
    if (lowRatio > 0.4) {
      return {
        type: 'warning',
        text: `近期低品质样本占比 ${(lowRatio * 100).toFixed(1)}%，建议加强奶源检测与供应商沟通。`,
      }
    }
    if (highRatio > 0.5) {
      return {
        type: 'success',
        text: `近期高品质样本占比 ${(highRatio * 100).toFixed(1)}%，奶源质量稳定向好。`,
      }
    }
    return {
      type: 'info',
      text: '近期奶源品质分布较为均衡，建议继续保持常规检测频率。',
    }
  }, [data, distribution])

  const columns = [
    { title: 'ID', dataIndex: 'id' },
    { title: 'pH', dataIndex: 'ph' },
    { title: '温度', dataIndex: 'temperature' },
    { title: '口感', dataIndex: 'taste' },
    { title: '气味', dataIndex: 'odor' },
    { title: '脂肪', dataIndex: 'fat' },
    { title: '浑浊度', dataIndex: 'turbidity' },
    { title: '颜色', dataIndex: 'colour' },
    { title: '来源', dataIndex: 'source_name', render: (v) => v || '—' },
    { title: '批次号', dataIndex: 'batch_no', render: (v) => v || '—' },
    {
      title: '等级',
      dataIndex: 'predicted_grade',
      render: (v) => (
        <span style={{ color: GRADE_COLORS[v] || '#1D1D1F', fontWeight: 600 }}>
          {GRADE_LABELS[v] || v}
        </span>
      ),
    },
    { title: '置信度', dataIndex: 'confidence', render: (v) => `${(v * 100).toFixed(2)}%` },
    {
      title: '建议价(元/kg)', dataIndex: 'suggested_price',
      render: (v) => (v ? `¥${v.toFixed(2)}` : '—'),
    },
    {
      title: '时间', dataIndex: 'created_at',
      render: (v) => fmtBeijing(v),
    },
  ]

  return (
    <div>
      {data.length > 0 && (
        <Card title="品质波动分析" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={distribution} barCategoryGap="30%">
                  <XAxis dataKey="grade" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                  <Tooltip formatter={(value) => [`${value} 条`, '数量']} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {distribution.map((entry, index) => (
                      <Cell key={index} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Col>
            <Col xs={24} md={16}>
              <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={8}>
                  <Statistic
                    title="低品质"
                    value={distribution.find((d) => d.key === 'low').count}
                    valueStyle={{ color: GRADE_COLORS.low }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="一般"
                    value={distribution.find((d) => d.key === 'medium').count}
                    valueStyle={{ color: GRADE_COLORS.medium }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="高品质"
                    value={distribution.find((d) => d.key === 'high').count}
                    valueStyle={{ color: GRADE_COLORS.high }}
                  />
                </Col>
              </Row>
              {advice && (
                <div
                  style={{
                    padding: '12px 16px',
                    borderRadius: 8,
                    background:
                      advice.type === 'warning'
                        ? '#FFF2F0'
                        : advice.type === 'success'
                        ? '#F6FFED'
                        : '#F0F5FF',
                    border: `1px solid ${
                      advice.type === 'warning'
                        ? '#FFCCC7'
                        : advice.type === 'success'
                        ? '#B7EB8F'
                        : '#BAE0FF'
                    }`,
                    color:
                      advice.type === 'warning'
                        ? '#CF1322'
                        : advice.type === 'success'
                        ? '#389E0D'
                        : '#0958D9',
                    fontSize: 14,
                  }}
                >
                  <strong>分析建议：</strong>
                  {advice.text}
                </div>
              )}
            </Col>
          </Row>
        </Card>
      )}

      <Card
        title="分级历史记录"
        extra={
          <Space>
            <Select
              style={{ minWidth: 240 }}
              placeholder="按批次筛选（全部）"
              allowClear
              value={batchFilter}
              onChange={(v) => setBatchFilter(v || null)}
              options={batches.map((b) => ({
                value: b.key,
                label: `${b.label}（${b.count} 条）`,
              }))}
            />
            <Button type="primary" onClick={onExport}>
              {batchFilter ? '导出本批次 CSV' : '导出 CSV'}
            </Button>
          </Space>
        }
      >
        {data.length === 0 && !loading ? (
          <Empty description="暂无分级记录，请先进行品质分级预测" />
        ) : (
          <>
            {batchFilter && (
              <div style={{ marginBottom: 12 }}>
                <Tag color="blue">
                  当前批次：{(batches.find((b) => b.key === batchFilter) || {}).label || batchFilter}
                  ，共 {filtered.length} 条
                </Tag>
              </div>
            )}
            <Table
              rowKey="id"
              dataSource={filtered}
              columns={columns}
              loading={loading}
              pagination={{ pageSize: 10, showTotal: (t) => `共 ${t} 条` }}
              size="small"
            />
          </>
        )}
      </Card>
    </div>
  )
}
