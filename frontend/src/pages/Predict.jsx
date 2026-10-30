import React, { useEffect, useState } from 'react'
import {
  Form, InputNumber, Select, Button, Card, Upload, Table, Tabs, message, Spin,
  Row, Col, Statistic, Empty, Alert, Space, Tag, Modal, Input,
} from 'antd'
import { UploadOutlined, EyeOutlined } from '@ant-design/icons'
import {
  predict, predictCsv, getModelInfo, getSources, createSource,
} from '../api'
import GradeResult from '../components/GradeResult'
import ProbBars from '../components/ProbBars'
import FeatureImportanceChart from '../components/FeatureImportanceChart'
import DataDistributionChart from '../components/DataDistributionChart'
import AgentAnalysis from '../components/AgentAnalysis'
import PricingCard from '../components/PricingCard'
import CorrelationHeatmap from '../components/CorrelationHeatmap'

const BinarySelect = () => (
  <Select
    style={{ width: '100%' }}
    options={[{ value: 1, label: '1（合格）' }, { value: 0, label: '0（不合格）' }]}
  />
)

// CSV 预览列（上传后先预览，确认后再预测）
const previewColumns = [
  { title: '行号', dataIndex: 'row' },
  { title: 'pH', dataIndex: 'pH' },
  { title: '温度', dataIndex: 'Temperature' },
  { title: '口感', dataIndex: 'Taste' },
  { title: '气味', dataIndex: 'Odor' },
  { title: '脂肪', dataIndex: 'Fat' },
  { title: '浑浊度', dataIndex: 'Turbidity' },
  { title: '颜色', dataIndex: 'Colour' },
  { title: '批次号', dataIndex: 'Batch', render: (v) => v || '—' },
]

const resultColumns = [
  { title: '行号', dataIndex: 'row' },
  { title: '批次号', dataIndex: 'batch_no', render: (v) => v || '—' },
  {
    title: '等级', dataIndex: 'grade',
    render: (v) => (
      <Tag color={v === 'high' ? 'green' : v === 'medium' ? 'orange' : 'red'}>
        {v === 'high' ? '优' : v === 'medium' ? '中' : '差'}
      </Tag>
    ),
  },
  { title: '置信度', dataIndex: 'confidence', render: (v) => `${(v * 100).toFixed(2)}%` },
  {
    title: '建议价(元/kg)', dataIndex: 'pricing',
    render: (p) => p ? `¥${p.suggested_price.toFixed(2)}` : '—',
  },
]

export default function Predict() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [inputData, setInputData] = useState(null)
  const [csvLoading, setCsvLoading] = useState(false)
  const [csvRes, setCsvRes] = useState(null)
  const [model, setModel] = useState(null)
  const [modelLoading, setModelLoading] = useState(true)
  // 企业功能：来源档案 + 批次号
  const [sources, setSources] = useState([])
  const [sourceId, setSourceId] = useState(null)
  const [batchNo, setBatchNo] = useState('')
  // CSV 预览两步走
  const [preview, setPreview] = useState(null)   // { rows, fileName }
  const [sourceModal, setSourceModal] = useState(false)
  const [sourceForm] = Form.useForm()

  useEffect(() => {
    getModelInfo()
      .then((r) => setModel(r.data))
      .catch(() => {})
      .finally(() => setModelLoading(false))
    getSources()
      .then((r) => setSources(r.data || []))
      .catch(() => {})
  }, [])

  const onPredict = async (v) => {
    setLoading(true)
    try {
      const { data } = await predict({
        ph: v.ph, temperature: v.temperature, taste: v.taste, odor: v.odor,
        fat: v.fat, turbidity: v.turbidity, colour: v.colour,
        source_id: sourceId, batch_no: batchNo || null,
      })
      setResult(data)
      setInputData({
        ph: v.ph, temperature: v.temperature, taste: v.taste, odor: v.odor,
        fat: v.fat, turbidity: v.turbidity, colour: v.colour,
      })
    } catch (e) {
      message.error(e.response?.data?.detail || '预测失败')
    } finally {
      setLoading(false)
    }
  }

  // 第一步：上传后仅解析预览，不预测
  const onCsvPreview = async (file) => {
    setCsvLoading(true)
    try {
      const text = await file.text()
      const lines = text.split(/\r?\n/).filter((l) => l.trim())
      if (lines.length < 2) {
        message.warning('CSV 文件为空或只有表头')
        return false
      }
      const header = lines[0].split(',').map((h) => h.trim())
      const rename = { temprature: 'Temperature', Temprature: 'Temperature', temperature: 'Temperature', ph: 'pH', taste: 'Taste', odor: 'Odor', fat: 'Fat', turbidity: 'Turbidity', colour: 'Colour' }
      const norm = header.map((h) => rename[h] || h)
      const required = ['pH', 'Temperature', 'Taste', 'Odor', 'Fat', 'Turbidity', 'Colour']
      const lowerNorm = norm.map((h) => h.toLowerCase())
      const missing = required.filter((c) => !lowerNorm.includes(c.toLowerCase()))

      const rows = lines.slice(1, 6).map((line, i) => {  // 最多预览 5 行
        const cells = line.split(',')
        const obj = { row: i + 2 }
        norm.forEach((h, j) => { obj[h] = cells[j]?.trim() })
        return obj
      })

      setPreview({
        file,
        rows,
        fileName: file.name,
        totalRows: lines.length - 1,
        missing,
        header: norm,
      })
      if (missing.length) {
        message.warning(`缺少必需列：${missing.join(', ')}`)
      } else {
        message.success(`已解析 ${lines.length - 1} 行数据，请确认后执行预测`)
      }
    } catch (e) {
      message.error('CSV 解析失败：' + e.message)
    } finally {
      setCsvLoading(false)
    }
    return false // 阻止 antd 自动上传
  }

  // 第二步：确认后执行预测
  const onCsvConfirm = async () => {
    if (!preview || !preview.file) return
    setCsvLoading(true)
    try {
      const { data } = await predictCsv(preview.file, sourceId)
      setCsvRes(data)
      message.success(`批量预测完成：${data.count} 条`)
      setPreview(null)
    } catch (e) {
      message.error(e.response?.data?.detail || '批量预测失败')
    } finally {
      setCsvLoading(false)
    }
  }

  const onCreateSource = async (v) => {
    try {
      const { data } = await createSource(v)
      setSources([...sources, data])
      setSourceId(data.id)
      setSourceModal(false)
      sourceForm.resetFields()
      message.success(`来源「${data.name}」已创建`)
    } catch (e) {
      message.error(e.response?.data?.detail || '创建失败')
    }
  }

  const csvColumns = resultColumns

  const modelInfoTab = (
    <Card title="模型性能、特征重要性与相关性分析">
      {modelLoading || !model ? (
        <Spin spinning={modelLoading} />
      ) : (
        <>
          <Row gutter={16}>
            <Col span={8}><Card><Statistic title="测试集准确率" value={(model.test_accuracy * 100).toFixed(1)} suffix="%" /></Card></Col>
            <Col span={8}><Card><Statistic title="宏平均 F1" value={model.test_macro_f1.toFixed(3)} /></Card></Col>
            <Col span={8}><Card><Statistic title="训练样本量" value={model.n_samples} /></Card></Col>
          </Row>

          {/* 基线模型对比（任务书 2.2.3） */}
          {model.baseline_comparison && (
            <Card title="基线模型对比（同一测试集）" size="small" style={{ marginTop: 16 }}>
              <Table
                size="small"
                pagination={false}
                dataSource={model.baseline_comparison.results.map((r, i) => ({ ...r, key: i }))}
                columns={[
                  {
                    title: '模型', dataIndex: 'model',
                    render: (v) => v.includes('XGBoost')
                      ? <span style={{ color: '#34C759', fontWeight: 600 }}>{v} ★</span>
                      : v,
                  },
                  { title: '准确率', dataIndex: 'accuracy', render: (v) => `${(v * 100).toFixed(2)}%` },
                  { title: '宏平均 F1', dataIndex: 'macro_f1', render: (v) => v.toFixed(4) },
                ]}
              />
              <div style={{ fontSize: 12, color: '#888', marginTop: 8 }}>
                {model.baseline_comparison.note} · XGBoost 优于决策树与随机森林，选为生产模型
              </div>
            </Card>
          )}

          <Card title="特征重要性排序" size="small" style={{ marginTop: 16 }}>
            <FeatureImportanceChart data={model.feature_importance} />
          </Card>

          {/* 相关性热力图（任务书 2.2.2） */}
          {model.correlation && (
            <Card title="指标相关性分析（Pearson）" size="small" style={{ marginTop: 16 }}>
              <CorrelationHeatmap data={model.correlation} />
              <div style={{ fontSize: 12, color: '#888', marginTop: 8 }}>
                解读：Temperature 与 Grade 呈最强负相关（-0.42）——温度越高品质越差；
                Taste/Odor/Fat 与 Grade 正相关， Turbidity 负相关，与特征重要性结论互相印证。
              </div>
            </Card>
          )}

          <Card title="训练数据集分布" size="small" style={{ marginTop: 16 }}>
            <DataDistributionChart />
          </Card>
        </>
      )}
    </Card>
  )

  return (
    <>
      <Tabs defaultActiveKey="single" items={[
      {
        key: 'single', label: '单条录入', children: (
          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Card title="录入 7 项理化指标">
                {/* 企业信息：来源 + 批次号 */}
                <Row gutter={12} style={{ marginBottom: 16 }}>
                  <Col span={16}>
                    <label style={{ fontSize: 13, color: '#666', display: 'block', marginBottom: 4 }}>
                      奶源来源（奶站/牧场）
                    </label>
                    <Space.Compact style={{ width: '100%' }}>
                      <Select
                        allowClear
                        placeholder="选择来源（可选）"
                        value={sourceId}
                        onChange={setSourceId}
                        options={sources.map((s) => ({
                          value: s.id,
                          label: `${s.name}（${s.source_type}${s.region ? ' · ' + s.region : ''}）`,
                        }))}
                      />
                      <Button onClick={() => setSourceModal(true)}>+ 新建</Button>
                    </Space.Compact>
                  </Col>
                  <Col span={8}>
                    <label style={{ fontSize: 13, color: '#666', display: 'block', marginBottom: 4 }}>批次号</label>
                    <Input
                      placeholder="如 B20261021-01"
                      value={batchNo}
                      onChange={(e) => setBatchNo(e.target.value)}
                    />
                  </Col>
                </Row>

                <Form
                  form={form} layout="vertical" onFinish={onPredict}
                  initialValues={{ ph: 6.6, temperature: 40, taste: 1, odor: 1, fat: 1, turbidity: 1, colour: 255 }}
                >
                  <Form.Item name="ph" label="pH" rules={[{ required: true }]}>
                    <InputNumber min={0} max={14} step={0.01} style={{ width: '100%' }} />
                  </Form.Item>
                  <Form.Item name="temperature" label="温度 (°C)" rules={[{ required: true }]}>
                    <InputNumber min={0} max={100} step={0.1} style={{ width: '100%' }} />
                  </Form.Item>
                  <Form.Item name="taste" label="口感 (0/1)" rules={[{ required: true }]}>{BinarySelect()}</Form.Item>
                  <Form.Item name="odor" label="气味 (0/1)" rules={[{ required: true }]}>{BinarySelect()}</Form.Item>
                  <Form.Item name="fat" label="脂肪 (0/1)" rules={[{ required: true }]}>{BinarySelect()}</Form.Item>
                  <Form.Item name="turbidity" label="浑浊度 (0/1)" rules={[{ required: true }]}>{BinarySelect()}</Form.Item>
                  <Form.Item name="colour" label="颜色 (0-255)" rules={[{ required: true }]}>
                    <InputNumber min={0} max={255} style={{ width: '100%' }} />
                  </Form.Item>
                  <Button type="primary" htmlType="submit" block loading={loading}>预测分级</Button>
                </Form>
              </Card>
            </Col>
            <Col xs={24} md={12}>
              {result ? (
                <>
                  <GradeResult grade={result.grade} confidence={result.confidence} />
                  <Card title="各等级概率" style={{ marginTop: 24 }}>
                    <ProbBars probabilities={result.probabilities} />
                  </Card>
                  <PricingCard pricing={result.pricing} grade={result.grade} />
                  <Card title="Agent 智能分析" style={{ marginTop: 24 }}>
                    <AgentAnalysis inputData={inputData} />
                  </Card>
                </>
              ) : (
                <Card><Empty description="填写左侧指标并点击「预测分级」" /></Card>
              )}
            </Col>
          </Row>
        ),
      },
      {
        key: 'csv', label: 'CSV 批量', children: (
          <Card title="上传 CSV 批量预测">
            <Row gutter={12} style={{ marginBottom: 12 }}>
              <Col span={12}>
                <label style={{ fontSize: 13, color: '#666', display: 'block', marginBottom: 4 }}>
                  关联来源（本批所有记录）
                </label>
                <Select
                  allowClear
                  placeholder="选择来源（可选）"
                  value={sourceId}
                  onChange={setSourceId}
                  style={{ width: '100%' }}
                  options={sources.map((s) => ({ value: s.id, label: `${s.name}（${s.source_type}）` }))}
                />
              </Col>
            </Row>

            <Upload beforeUpload={onCsvPreview} maxCount={1} accept=".csv" showUploadList={false}>
              <Button icon={<UploadOutlined />} loading={csvLoading}>选择 CSV 文件</Button>
            </Upload>
            <div style={{ marginTop: 8, color: '#888', fontSize: 13 }}>
              CSV 需含表头列：pH, Temperature, Taste, Odor, Fat, Turbidity, Colour（可选 Batch 批次号列）。
              列名大小写/拼写容错（temprature/Temprature 自动纠正）。
            </div>

            {/* 预览确认区（任务书 2.2.1：数据预览功能） */}
            {preview && (
              <div style={{ marginTop: 16 }}>
                <Alert
                  type={preview.missing.length ? 'warning' : 'info'}
                  showIcon
                  style={{ marginBottom: 12 }}
                  message={
                    preview.missing.length
                      ? `缺少必需列：${preview.missing.join(', ')}，请修正后重新上传`
                      : `已解析「${preview.fileName}」共 ${preview.totalRows} 行，以下为前 ${preview.rows.length} 行预览`
                  }
                />
                {!preview.missing.length && (
                  <>
                    <Table
                      size="small"
                      pagination={false}
                      dataSource={preview.rows}
                      columns={previewColumns}
                      rowKey="row"
                      scroll={{ x: 'max-content' }}
                    />
                    <Button
                      type="primary"
                      style={{ marginTop: 12 }}
                      loading={csvLoading}
                      onClick={onCsvConfirm}
                    >
                      确认无误，执行批量预测（{preview.totalRows} 条）
                    </Button>
                  </>
                )}
              </div>
            )}

            {csvRes && (
              <>
                <div style={{ marginTop: 16, marginBottom: 8, fontWeight: 600 }}>
                  预测结果（{csvRes.count} 条）
                  {csvRes.errors?.length > 0 && (
                    <span style={{ color: '#FF3B30', fontWeight: 400, marginLeft: 8 }}>
                      {csvRes.errors.length} 行失败
                    </span>
                  )}
                </div>
                <Table
                  rowKey="row" dataSource={csvRes.results}
                  columns={csvColumns} pagination={{ pageSize: 8 }} size="small" scroll={{ y: 320 }}
                />
              </>
            )}
          </Card>
        ),
      },
      { key: 'model', label: '模型与特征', children: modelInfoTab },
    ]} />

      {/* 新建来源弹窗 */}
      <Modal
        title="新建奶源来源"
        open={sourceModal}
        onCancel={() => setSourceModal(false)}
        onOk={() => sourceForm.submit()}
        okText="创建"
      >
        <Form form={sourceForm} layout="vertical" onFinish={onCreateSource}
              initialValues={{ source_type: '奶站' }}>
          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入来源名称' }]}>
            <Input placeholder="如：第三奶站" />
          </Form.Item>
          <Form.Item name="source_type" label="类型">
            <Select options={[
              { value: '奶站', label: '奶站' },
              { value: '牧场', label: '牧场' },
              { value: '合作社', label: '合作社' },
            ]} />
          </Form.Item>
          <Form.Item name="contact" label="联系人">
            <Input placeholder="如：张站长 138****0001" />
          </Form.Item>
          <Form.Item name="region" label="地区">
            <Input placeholder="如：城东区" />
          </Form.Item>
          <Form.Item name="note" label="备注">
            <Input.TextArea rows={2} placeholder="合作情况、质量特点等" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}
