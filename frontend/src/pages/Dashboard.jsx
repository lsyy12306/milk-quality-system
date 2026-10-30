import React, { useEffect, useState } from 'react'
import {
  Card, Row, Col, Statistic, Spin, Alert, Tag, Timeline, Empty,
  Button, DatePicker, message, Modal, Table,
} from 'antd'
import {
  ArrowUpOutlined, ArrowDownOutlined, MinusOutlined,
  WarningOutlined, CheckCircleOutlined, FileTextOutlined,
} from '@ant-design/icons'
import { agentTrends, getHistory, agentDailyReport, fmtBeijing } from '../api'
import dayjs from 'dayjs'

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [trend, setTrend] = useState(null)
  const [history, setHistory] = useState([])
  const [days, setDays] = useState(30)
  // 企业日报
  const [reportModal, setReportModal] = useState(false)
  const [reportDate, setReportDate] = useState(null)
  const [reportLoading, setReportLoading] = useState(false)
  const [report, setReport] = useState(null)

  const fetchData = async (d = 30) => {
    setLoading(true)
    try {
      const [tRes, hRes] = await Promise.all([
        agentTrends({ days: d }),
        getHistory(),
      ])
      setTrend(tRes.data)
      setHistory(hRes.data.slice(0, 20))
    } catch (e) {
      message.error('加载数据失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const loadReport = async (dateStr) => {
    setReportLoading(true)
    try {
      const { data } = await agentDailyReport(dateStr ? { date: dateStr } : {})
      setReport(data)
    } catch (e) {
      message.error(e.response?.data?.detail || '日报生成失败')
    } finally {
      setReportLoading(false)
    }
  }

  const gradeColor = { high: 'green', medium: 'orange', low: 'red' }
  const gradeText = { high: '优', medium: '中', low: '差' }

  return (
    <Spin spinning={loading}>
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 style={{ margin: 0 }}>分析仪表盘</h2>
          <Button
            type="primary"
            icon={<FileTextOutlined />}
            onClick={() => { setReportModal(true); setReport(null); loadReport(null) }}
          >
            生成企业日报
          </Button>
        </div>

        {/* 时间范围选择 */}
        <Card size="small" style={{ marginBottom: 16 }}>
          <span style={{ marginRight: 8 }}>统计周期：</span>
          <Button size="small" type={days === 7 ? 'primary' : 'default'} onClick={() => { setDays(7); fetchData(7) }}>近7天</Button>
          <Button size="small" style={{ marginLeft: 8 }} type={days === 30 ? 'primary' : 'default'} onClick={() => { setDays(30); fetchData(30) }}>近30天</Button>
          <Button size="small" style={{ marginLeft: 8 }} type={days === 90 ? 'primary' : 'default'} onClick={() => { setDays(90); fetchData(90) }}>近90天</Button>
        </Card>

        {!trend || trend.error ? (
          <Empty description={trend?.error || '暂无数据'} />
        ) : (
          <>
            {/* 核心指标 */}
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic title="检测总数" value={trend.records_count} />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="品质趋势"
                    value={trend.trend}
                    valueStyle={{ color: trend.trend_direction === 'up' ? '#3f8600' : trend.trend_direction === 'down' ? '#cf1322' : '#666' }}
                    prefix={trend.trend_direction === 'up' ? <ArrowUpOutlined /> : trend.trend_direction === 'down' ? <ArrowDownOutlined /> : <MinusOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="平均置信度"
                    value={(trend.avg_confidence * 100).toFixed(1)}
                    suffix="%"
                    valueStyle={{ color: trend.avg_confidence >= 0.9 ? '#3f8600' : '#cf1322' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="优质率"
                    value={trend.grade_distribution_pct?.high || 0}
                    suffix="%"
                    valueStyle={{ color: '#3f8600' }}
                  />
                </Card>
              </Col>
            </Row>

            {/* 预警区域 */}
            {trend.alerts && trend.alerts.length > 0 && (
              <Alert
                message="品质预警"
                description={
                  <ul style={{ margin: 0, paddingLeft: 16 }}>
                    {trend.alerts.map((a, i) => <li key={i}>{a}</li>)}
                  </ul>
                }
                type="warning"
                showIcon
                icon={<WarningOutlined />}
                style={{ marginBottom: 16 }}
              />
            )}

            {/* 等级分布 */}
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col xs={24} md={12}>
                <Card title="等级分布">
                  <Row gutter={16}>
                    <Col span={8}>
                      <Statistic title="优" value={trend.grade_distribution?.high || 0} suffix="条" />
                      <div style={{ color: '#888', fontSize: 12 }}>{trend.grade_distribution_pct?.high || 0}%</div>
                    </Col>
                    <Col span={8}>
                      <Statistic title="中" value={trend.grade_distribution?.medium || 0} suffix="条" />
                      <div style={{ color: '#888', fontSize: 12 }}>{trend.grade_distribution_pct?.medium || 0}%</div>
                    </Col>
                    <Col span={8}>
                      <Statistic title="差" value={trend.grade_distribution?.low || 0} suffix="条" />
                      <div style={{ color: '#888', fontSize: 12 }}>{trend.grade_distribution_pct?.low || 0}%</div>
                    </Col>
                  </Row>
                  {/* 简易条形图 */}
                  <div style={{ marginTop: 12, display: 'flex', height: 24, borderRadius: 4, overflow: 'hidden' }}>
                    <div style={{ width: `${trend.grade_distribution_pct?.high || 0}%`, background: '#52c41a', transition: 'width 0.5s' }} />
                    <div style={{ width: `${trend.grade_distribution_pct?.medium || 0}%`, background: '#faad14', transition: 'width 0.5s' }} />
                    <div style={{ width: `${trend.grade_distribution_pct?.low || 0}%`, background: '#f5222d', transition: 'width 0.5s' }} />
                  </div>
                  <div style={{ display: 'flex', marginTop: 4, fontSize: 12 }}>
                    <span style={{ width: `${trend.grade_distribution_pct?.high || 0}%`, textAlign: 'center', color: '#52c41a' }}>优</span>
                    <span style={{ width: `${trend.grade_distribution_pct?.medium || 0}%`, textAlign: 'center', color: '#faad14' }}>中</span>
                    <span style={{ width: `${trend.grade_distribution_pct?.low || 0}%`, textAlign: 'center', color: '#f5222d' }}>差</span>
                  </div>
                </Card>
              </Col>
              <Col xs={24} md={12}>
                <Card title="近期检测记录">
                  {history.length === 0 ? (
                    <Empty description="暂无记录" />
                  ) : (
                    <Timeline mode="left" style={{ marginTop: 8 }}>
                      {history.slice(0, 8).map((h) => (
                        <Timeline.Item
                          key={h.id}
                          color={gradeColor[h.predicted_grade]}
                          label={fmtBeijing(h.created_at)}
                        >
                          <Tag color={gradeColor[h.predicted_grade]}>{gradeText[h.predicted_grade]}</Tag>
                          <span style={{ fontSize: 12, color: '#888' }}>置信度 {(h.confidence * 100).toFixed(1)}%</span>
                        </Timeline.Item>
                      ))}
                    </Timeline>
                  )}
                </Card>
              </Col>
            </Row>

            {/* 趋势解读 */}
            <Card title="智能解读" style={{ marginBottom: 16 }}>
              <p><CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                近 {trend.period_days} 天共检测 {trend.records_count} 条记录，品质趋势为「{trend.trend}」。
              </p>
              <p><CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                优质样品占比 {trend.grade_distribution_pct?.high || 0}%，平均置信度 {(trend.avg_confidence * 100).toFixed(1)}%。
              </p>
              {trend.alerts?.length > 0 && (
                <p><WarningOutlined style={{ color: '#faad14', marginRight: 8 }} />
                  检测到 {trend.alerts.length} 条预警，请关注上方预警信息。
                </p>
              )}
            </Card>
          </>
        )}

        {/* 企业质量日报弹窗 */}
        <Modal
          title="企业质量日报"
          open={reportModal}
          onCancel={() => setReportModal(false)}
          width={760}
          footer={[
            <Button key="close" onClick={() => setReportModal(false)}>关闭</Button>,
            <Button
              key="copy"
              type="primary"
              disabled={!report || report.error}
              onClick={() => {
                navigator.clipboard.writeText(report.content)
                message.success('日报已复制到剪贴板')
              }}
            >
              复制 Markdown
            </Button>,
            <Button
              key="download"
              disabled={!report || report.error}
              onClick={() => {
                const blob = new Blob([report.content], { type: 'text/markdown;charset=utf-8' })
                const a = document.createElement('a')
                a.href = URL.createObjectURL(blob)
                a.download = `牛奶收购质量日报_${report.date}.md`
                a.click()
                URL.revokeObjectURL(a.href)
              }}
            >
              下载 .md
            </Button>,
          ]}
        >
          <div style={{ marginBottom: 12 }}>
            <span style={{ marginRight: 8, color: '#666' }}>选择日期：</span>
            <DatePicker
              value={reportDate}
              onChange={(d) => setReportDate(d)}
              disabledDate={(d) => d && d.isAfter(dayjs())}
            />
            <Button
              style={{ marginLeft: 8 }}
              loading={reportLoading}
              onClick={() => loadReport(reportDate ? reportDate.format('YYYY-MM-DD') : null)}
            >
              查询
            </Button>
          </div>
          <Spin spinning={reportLoading}>
            {report && report.error ? (
              <Empty description={report.error} />
            ) : report ? (
              <>
                <Row gutter={12} style={{ marginBottom: 12 }}>
                  <Col span={8}><Statistic title="收购记录" value={report.records_count} suffix="条" /></Col>
                  <Col span={8}><Statistic title="建议收购总额" value={report.suggested_total_price} prefix="¥" precision={2} /></Col>
                  <Col span={8}><Statistic title="需关注" value={report.anomaly_count} suffix="条" /></Col>
                </Row>
                <Table
                  size="small"
                  pagination={false}
                  style={{ marginBottom: 12 }}
                  dataSource={report.source_ranking.map((s, i) => ({ ...s, key: i }))}
                  columns={[
                    { title: '来源', dataIndex: 'source' },
                    { title: '收购数', dataIndex: 'count' },
                    { title: '优质率', dataIndex: 'high_ratio', render: (v) => `${v}%` },
                    { title: '差奶数', dataIndex: 'low_count' },
                    { title: '均价(元/kg)', dataIndex: 'avg_price' },
                  ]}
                />
                <pre style={{
                  background: '#f5f5f5', padding: 12, borderRadius: 8,
                  maxHeight: 300, overflow: 'auto', fontSize: 12, whiteSpace: 'pre-wrap',
                }}>{report.content}</pre>
              </>
            ) : null}
          </Spin>
        </Modal>
      </div>
    </Spin>
  )
}
