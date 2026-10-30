import React, { useState } from 'react'
import { Card, Form, Input, Button, message, Typography } from 'antd'
import { useNavigate, Link } from 'react-router-dom'
import { login as apiLogin } from '../api'
import { setToken, setUsername } from '../auth'

export default function Login() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const onFinish = async (v) => {
    setLoading(true)
    try {
      const { data } = await apiLogin(v)
      setToken(data.access_token)
      setUsername(v.username)
      message.success('登录成功')
      navigate('/predict')
    } catch (e) {
      message.error(e.response?.data?.detail || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f0f2f5' }}>
      <Card title="牛奶品质分级系统 · 登录" style={{ width: 360 }}>
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input placeholder="用户名" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password placeholder="密码" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={loading}>登录</Button>
        </Form>
        <div style={{ marginTop: 12, textAlign: 'right' }}>
          还没有账号？<Link to="/register">去注册</Link>
        </div>
      </Card>
    </div>
  )
}
