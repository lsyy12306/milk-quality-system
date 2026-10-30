import React, { useEffect, useState } from 'react'
import {
  Card, Table, Button, Modal, Form, Input, Select, message, Popconfirm, Tag, Statistic, Row, Col, Alert,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { getSources, createSource, updateSource, deleteSource, fmtBeijing } from '../api'

const { TextArea } = Input

const TYPE_COLORS = { '奶站': 'blue', '牧场': 'green', '合作社': 'orange' }

export default function SourceManager() {
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()

  const load = async () => {
    setLoading(true)
    try {
      const r = await getSources()
      setSources(r.data || [])
    } catch (e) {
      message.error('加载来源失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ source_type: '奶站' })
    setModalOpen(true)
  }

  const openEdit = (record) => {
    setEditing(record)
    form.setFieldsValue(record)
    setModalOpen(true)
  }

  const onSave = async (v) => {
    setSaving(true)
    try {
      if (editing) {
        await updateSource(editing.id, v)
        message.success(`来源「${v.name}」已更新`)
      } else {
        await createSource(v)
        message.success(`来源「${v.name}」已创建`)
      }
      setModalOpen(false)
      load()
    } catch (e) {
      message.error(e.response?.data?.detail || '保存失败')
    } finally {
      setSaving(false)
    }
  }

  const onDelete = async (record) => {
    try {
      await deleteSource(record.id)
      message.success(`来源「${record.name}」已删除`)
      load()
    } catch (e) {
      message.error('删除失败')
    }
  }

  const typeCount = sources.reduce((acc, s) => {
    acc[s.source_type] = (acc[s.source_type] || 0) + 1
    return acc
  }, {})

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    {
      title: '名称', dataIndex: 'name',
      render: (v) => <span style={{ fontWeight: 600 }}>{v}</span>,
    },
    {
      title: '类型', dataIndex: 'source_type', width: 100,
      render: (v) => <Tag color={TYPE_COLORS[v] || 'default'}>{v}</Tag>,
    },
    { title: '地区', dataIndex: 'region', render: (v) => v || '—' },
    { title: '联系人', dataIndex: 'contact', render: (v) => v || '—' },
    { title: '备注', dataIndex: 'note', render: (v) => v || '—', ellipsis: true },
    {
      title: '建档时间', dataIndex: 'created_at', width: 170,
      render: (v) => fmtBeijing(v),
    },
    {
      title: '操作', key: 'actions', width: 140,
      render: (_, record) => (
        <span>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openEdit(record)}>编辑</Button>
          <Popconfirm
            title={`确定删除「${record.name}」？`}
            description="删除后历史记录中的来源关联将变为未标注"
            onConfirm={() => onDelete(record)}
            okText="删除"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </span>
      ),
    },
  ]

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}><Card><Statistic title="来源总数" value={sources.length} suffix="家" /></Card></Col>
        <Col span={6}><Card><Statistic title="奶站" value={typeCount['奶站'] || 0} suffix="家" /></Card></Col>
        <Col span={6}><Card><Statistic title="牧场" value={typeCount['牧场'] || 0} suffix="家" /></Card></Col>
        <Col span={6}><Card><Statistic title="合作社" value={typeCount['合作社'] || 0} suffix="家" /></Card></Col>
      </Row>

      <Card
        title="奶源来源档案管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>新建来源</Button>
        }
      >
        <Alert
          style={{ marginBottom: 16 }}
          type="info"
          showIcon
          message="来源档案用于收购追溯：预测时选择来源，历史记录可按来源统计质量，企业日报自动生成来源排名。"
        />
        <Table
          rowKey="id"
          dataSource={sources}
          columns={columns}
          loading={loading}
          pagination={false}
          size="small"
        />
      </Card>

      <Modal
        title={editing ? `编辑来源：${editing.name}` : '新建奶源来源'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        okText="保存"
        confirmLoading={saving}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={onSave}>
          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入来源名称' }]}>
            <Input placeholder="如：第三奶站" />
          </Form.Item>
          <Form.Item name="source_type" label="类型" rules={[{ required: true }]}>
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
            <TextArea rows={3} placeholder="合作情况、质量特点等" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
