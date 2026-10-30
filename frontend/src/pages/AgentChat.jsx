import React, { useState, useRef, useEffect } from 'react'
import {
  Card, Input, Button, List, Avatar, Tag, Spin, Empty,
  Collapse, message,
} from 'antd'
import {
  RobotOutlined, UserOutlined, SendOutlined,
  BulbOutlined, LineChartOutlined, FileTextOutlined,
  ClearOutlined,
} from '@ant-design/icons'
import { agentChat, getAgentTools } from '../api'

const { TextArea } = Input
const { Panel } = Collapse

export default function AgentChat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '你好！我是牛奶品质分级智能助手。\n\n我可以帮你：\n1. **分析样品品质** — 解释预测结果和根因\n2. **查询品质知识** — 关于 pH、温度、储存等专业问题\n3. **查看历史趋势** — 分析你的检测数据变化\n4. **生成分析报告** — 专业的品质诊断文档\n\n请直接输入你想了解的内容！',
      intent: 'greeting',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [tools, setTools] = useState([])
  const listRef = useRef(null)

  useEffect(() => {
    getAgentTools().then((r) => setTools(r.data.tools || [])).catch(() => {})
  }, [])

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight
    }
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim()) return
    const userMsg = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)

    try {
      const { data } = await agentChat({ message: userMsg, session_id: sessionId })
      if (!sessionId) setSessionId(data.session_id)
      setMessages((prev) => [...prev, { role: 'assistant', content: data.reply, intent: data.intent }])
    } catch (e) {
      message.error('发送失败')
    } finally {
      setLoading(false)
    }
  }

  const quickQuestions = [
    '什么是正常的牛奶pH范围？',
    '温度过高会有什么影响？',
    '帮我看看最近30天的趋势',
    '浑浊度异常怎么解决？',
    '如何提高牛奶品质？',
  ]

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 120px)', gap: 16 }}>
      {/* 左侧：对话区 */}
      <Card style={{ flex: 1, display: 'flex', flexDirection: 'column' }} bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0 }}>
        <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontWeight: 600 }}><RobotOutlined style={{ marginRight: 8 }} />智能助手</span>
          <Button size="small" icon={<ClearOutlined />} onClick={() => { setMessages([]); setSessionId(null) }}>清空对话</Button>
        </div>

        <div ref={listRef} style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
          <List
            dataSource={messages}
            renderItem={(msg) => (
              <List.Item style={{ border: 'none', padding: '8px 0' }}>
                <div style={{ display: 'flex', width: '100%', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
                  <Avatar
                    icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{ background: msg.role === 'user' ? '#1890ff' : '#52c41a', flexShrink: 0 }}
                  />
                  <div style={{
                    marginLeft: msg.role === 'user' ? 0 : 12,
                    marginRight: msg.role === 'user' ? 12 : 0,
                    maxWidth: '80%',
                    background: msg.role === 'user' ? '#e6f7ff' : '#f6ffed',
                    padding: '10px 14px',
                    borderRadius: 12,
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.6,
                    fontSize: 14,
                  }}>
                    {msg.content}
                    {msg.intent && msg.role === 'assistant' && (
                      <div style={{ marginTop: 4 }}>
                        <Tag size="small" color="default">意图: {msg.intent}</Tag>
                      </div>
                    )}
                  </div>
                </div>
              </List.Item>
            )}
          />
          {loading && (
            <div style={{ textAlign: 'center', padding: 16 }}>
              <Spin size="small" />
              <span style={{ marginLeft: 8, color: '#888', fontSize: 13 }}>思考中...</span>
            </div>
          )}
        </div>

        <div style={{ padding: 12, borderTop: '1px solid #f0f0f0' }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <TextArea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onPressEnter={(e) => { if (!e.shiftKey) { e.preventDefault(); sendMessage() } }}
              placeholder="输入问题，按 Enter 发送..."
              autoSize={{ minRows: 1, maxRows: 4 }}
              style={{ flex: 1 }}
            />
            <Button type="primary" icon={<SendOutlined />} onClick={sendMessage} loading={loading} />
          </div>
          <div style={{ marginTop: 8 }}>
            {quickQuestions.map((q) => (
              <Tag
                key={q}
                style={{ cursor: 'pointer', marginBottom: 4 }}
                onClick={() => { setInput(q); }}
              >
                {q}
              </Tag>
            ))}
          </div>
        </div>
      </Card>

      {/* 右侧：能力说明 */}
      <Card title="Agent 能力" style={{ width: 280, flexShrink: 0 }}>
        <Collapse ghost defaultActiveKey={['1']}>
          <Panel header={<span><BulbOutlined style={{ marginRight: 8 }} />知识问答</span>} key="1">
            <p style={{ fontSize: 12, color: '#666' }}>回答关于牛奶品质的专业问题，包括 pH、温度、储存、疾病等。</p>
          </Panel>
          <Panel header={<span><LineChartOutlined style={{ marginRight: 8 }} />趋势分析</span>} key="2">
            <p style={{ fontSize: 12, color: '#666' }}>基于历史数据，分析品质变化趋势，自动检测异常并预警。</p>
          </Panel>
          <Panel header={<span><FileTextOutlined style={{ marginRight: 8 }} />报告生成</span>} key="3">
            <p style={{ fontSize: 12, color: '#666' }}>自动生成完整的品质分析报告，包含根因分析和改进建议。</p>
          </Panel>
        </Collapse>

        <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid #f0f0f0' }}>
          <h4 style={{ fontSize: 13, marginBottom: 8 }}>可用工具</h4>
          {tools.length === 0 ? (
            <Spin size="small" />
          ) : (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {tools.map((t) => (
                <Tag key={t.name} size="small" color="blue">{t.name}</Tag>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
