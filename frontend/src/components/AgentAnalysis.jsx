import React, { useState } from 'react'
import {
  Card, Button, Spin, Tag, List, Timeline, Alert, Collapse,
  message, Empty, Statistic, Row, Col,
} from 'antd'
import {
  RobotOutlined, WarningOutlined, CheckCircleOutlined,
  FileTextOutlined, BulbOutlined, FireOutlined,
} from '@ant-design/icons'
import { agentAnalyze } from '../api'

const { Panel } = Collapse

export default function AgentAnalysis({ inputData, onReport }) {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)

  const runAnalysis = async () => {
    if (!inputData) return
    setLoading(true)
    try {
      const { data } = await agentAnalyze(inputData)
      setAnalysis(data)
      if (onReport) onReport(data.report)
    } catch (e) {
      message.error('智能分析失败')
    } finally {
      setLoading(false)
    }
  }

  if (!inputData) return null

  const gradeColor = { high: 'green', medium: 'orange', low: 'red' }
  const gradeText = { high: '优', medium: '中', low: '差' }
  const alertColor = { normal: 'green', warning: 'orange', critical: 'red' }
  const alertText = { normal: '正常', warning: '预警', critical: '严重' }

  return (
    <div>
      <Button
        type="primary"
        icon={<RobotOutlined />}
        onClick={runAnalysis}
        loading={loading}
        block
        style={{ marginBottom: 16 }}
      >
        {analysis ? '重新分析' : '智能分析'}
      </Button>

      {loading && (
        <Card>
          <div style={{ textAlign: 'center', padding: 24 }}>
            <Spin size="large" />
            <p style={{ marginTop: 12, color: '#888' }}>Agent 正在分析中...（根因分析 → 异常检测 → 改进建议 → 报告生成）</p>
          </div>
        </Card>
      )}

      {analysis && !loading && (
        <>
          {/* 分析概览 */}
          <Card title="分析概览" size="small" style={{ marginBottom: 12 }}>
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="品质等级"
                  value={gradeText[analysis.prediction.grade]}
                  valueStyle={{ color: gradeColor[analysis.prediction.grade] === 'green' ? '#52c41a' : gradeColor[analysis.prediction.grade] === 'orange' ? '#faad14' : '#f5222d' }}
                />
              </Col>
              <Col span={8}>
                <Statistic title="置信度" value={(analysis.prediction.confidence * 100).toFixed(1)} suffix="%" />
              </Col>
              <Col span={8}>
                <Statistic
                  title="预警级别"
                  value={alertText[analysis.anomaly.alert_level]}
                  valueStyle={{ color: alertColor[analysis.anomaly.alert_level] === 'green' ? '#52c41a' : alertColor[analysis.anomaly.alert_level] === 'orange' ? '#faad14' : '#f5222d' }}
                />
              </Col>
            </Row>
          </Card>

          {/* 推理链 */}
          <Card title="Agent 思考过程" size="small" style={{ marginBottom: 12 }}>
            <Timeline>
              {analysis.thinking_chain.map((step) => (
                <Timeline.Item key={step.step} color="green">
                  <b>{step.action}</b>：{step.result}
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>

          <Collapse defaultActiveKey={['root_cause', 'anomaly']}>
            {/* 根因分析 */}
            <Panel header={<span><FireOutlined style={{ marginRight: 8 }} />根因分析</span>} key="root_cause">
              <p>{analysis.root_cause.summary}</p>
              {analysis.root_cause.issues.length > 0 ? (
                <List
                  size="small"
                  dataSource={analysis.root_cause.issues}
                  renderItem={(item) => (
                    <List.Item>
                      <Tag color={item.severity === '严重' ? 'red' : 'orange'}>{item.severity}</Tag>
                      <b>{item.feature}</b>：当前 {item.value}，理想 {item.ideal_range}
                      <span style={{ color: '#888', marginLeft: 8 }}>贡献度 {(item.importance * 100).toFixed(1)}%</span>
                    </List.Item>
                  )}
                />
              ) : (
                <Alert message="所有指标均在理想范围内" type="success" showIcon />
              )}
            </Panel>

            {/* 异常检测 */}
            <Panel header={<span><WarningOutlined style={{ marginRight: 8 }} />异常检测</span>} key="anomaly">
              {analysis.anomaly.alert_level !== 'normal' ? (
                <>
                  {analysis.anomaly.criticals.length > 0 && (
                    <Alert
                      message={`严重异常 ${analysis.anomaly.criticals.length} 项`}
                      description={
                        <ul style={{ margin: 0, paddingLeft: 16 }}>
                          {analysis.anomaly.criticals.map((c, i) => (
                            <li key={i}>{c.feature}：{c.reason}（值：{c.value}）</li>
                          ))}
                        </ul>
                      }
                      type="error"
                      showIcon
                      style={{ marginBottom: 8 }}
                    />
                  )}
                  {analysis.anomaly.warnings.length > 0 && (
                    <Alert
                      message={`一般预警 ${analysis.anomaly.warnings.length} 项`}
                      description={
                        <ul style={{ margin: 0, paddingLeft: 16 }}>
                          {analysis.anomaly.warnings.map((w, i) => (
                            <li key={i}>{w.feature}：{w.reason}（值：{w.value}）</li>
                          ))}
                        </ul>
                      }
                      type="warning"
                      showIcon
                    />
                  )}
                </>
              ) : (
                <Alert message="无异常，所有指标正常" type="success" showIcon />
              )}
            </Panel>

            {/* 改进建议 */}
            <Panel header={<span><BulbOutlined style={{ marginRight: 8 }} />改进建议（{analysis.suggestions.total_suggestions} 条）</span>} key="suggestions">
              <List
                size="small"
                dataSource={analysis.suggestions.action_plan}
                renderItem={(item, idx) => (
                  <List.Item>
                    <span style={{ marginRight: 8 }}>{idx + 1}.</span>
                    <Tag color={item.priority === '严重' ? 'red' : item.priority === '轻微' ? 'orange' : 'blue'}>{item.priority}</Tag>
                    {item.action}
                  </List.Item>
                )}
              />
            </Panel>

            {/* 个性化洞察 */}
            {analysis.personalized?.has_history && (
              <Panel header={<span><CheckCircleOutlined style={{ marginRight: 8 }} />个性化洞察</span>} key="personalized">
                <p>{analysis.personalized.personalized_tip}</p>
                {analysis.personalized.top_issues.length > 0 && (
                  <p>历史中最常出现的问题指标：{analysis.personalized.top_issues.map(([k, v]) => `${k}(${v}次)`).join('、')}</p>
                )}
              </Panel>
            )}
          </Collapse>
        </>
      )}
    </div>
  )
}
