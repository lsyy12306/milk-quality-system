import React, { useEffect, useState } from 'react'
import { Table, Card, Alert } from 'antd'
import { getIndicators } from '../api'

export default function Indicators() {
  const [data, setData] = useState([])
  useEffect(() => {
    getIndicators().then((r) => setData(r.data)).catch(() => {})
  }, [])

  const columns = [
    { title: '字段', dataIndex: 'key' },
    { title: '名称', dataIndex: 'name' },
    { title: '单位', dataIndex: 'unit' },
    { title: '参考下限', dataIndex: 'min_value' },
    { title: '参考上限', dataIndex: 'max_value' },
    { title: '说明', dataIndex: 'description' },
  ]

  return (
    <Card title="指标字典（7 项理化指标参考范围）">
      <Table rowKey="key" dataSource={data} columns={columns} pagination={false} />
      <Alert
        style={{ marginTop: 16 }}
        type="warning"
        showIcon
        message="免责声明"
        description="本系统分级结果仅供奶源收购与生产环节的品质初筛参考，不构成食品安全检验合格依据；隐性问题（掺假、抗生素残留、微生物超标等）不在检测范围，判定结果需结合实验室检测复核。"
      />
    </Card>
  )
}
