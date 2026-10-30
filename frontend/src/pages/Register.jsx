import React, { useState } from 'react'
import { Card, Form, Input, Button, message, Typography } from 'antd'
import { useNavigate, Link } from 'react-router-dom'
import { register as apiRegister } from '../api'

export default function Register() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const onFinish = async (v) => {
    setLoading(true)
    try {
      await apiRegister(v)
      message.success('注册成功，请登录')
      navigate('/login')
    } catch (e) {
      message.error(e.response?.data?.detail || '注册失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f0f2f5' }}>
      <Card title="牛奶品质分级系统 · 注册" style={{ width: 360 }}>
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true, min: 3, message: '至少 3 个字符' }]}>
            <Input placeholder="用户名" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, min: 6, message: '至少 6 位' }]}>
            <Input.Password placeholder="密码" />
          </Form.Item>
          <Form.Item name="email" label="邮箱（选填）">
            <Input placeholder="邮箱" />
          </Form.Item>
          <Form.Item name="full_name" label="姓名（选填）">
            <Input placeholder="姓名" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={loading}>注册</Button>
        </Form>
        <div style={{ marginTop: 12, textAlign: 'right' }}>
          已有账号？<Link to="/login">去登录</Link>
        </div>
      </Card>
    </div>
  )
}
