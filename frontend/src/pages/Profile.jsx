import React, { useEffect, useState } from 'react'
import { Card, Form, Input, Button, message, Descriptions, Spin } from 'antd'
import { getMe, updateMe, updatePassword, fmtBeijing } from '../api'
import { getUsername } from '../auth'

export default function Profile() {
  const [me, setMe] = useState(null)
  const [loading, setLoading] = useState(true)
  const [savingProfile, setSavingProfile] = useState(false)
  const [savingPwd, setSavingPwd] = useState(false)
  const [profileForm] = Form.useForm()
  const [pwdForm] = Form.useForm()

  const loadMe = () => {
    setLoading(true)
    getMe()
      .then((r) => {
        setMe(r.data)
        profileForm.setFieldsValue({
          email: r.data.email || '',
          full_name: r.data.full_name || '',
        })
      })
      .catch(() => message.error('加载用户信息失败'))
      .finally(() => setLoading(false))
  }

  useEffect(loadMe, [])

  const onSaveProfile = async (v) => {
    setSavingProfile(true)
    try {
      const { data } = await updateMe(v)
      setMe(data)
      message.success('资料已更新')
    } catch (e) {
      message.error(e.response?.data?.detail || '更新失败')
    } finally {
      setSavingProfile(false)
    }
  }

  const onChangePassword = async (v) => {
    setSavingPwd(true)
    try {
      await updatePassword({ old_password: v.old_password, new_password: v.new_password })
      message.success('密码已修改，请牢记新密码')
      pwdForm.resetFields()
    } catch (e) {
      message.error(e.response?.data?.detail || '修改失败')
    } finally {
      setSavingPwd(false)
    }
  }

  if (loading) {
    return <Card><Spin spinning /></Card>
  }

  return (
    <div style={{ maxWidth: 720 }}>
      <Card title="账号信息" style={{ marginBottom: 24 }}>
        <Descriptions column={2} size="small">
          <Descriptions.Item label="用户名">{me?.username || getUsername()}</Descriptions.Item>
          <Descriptions.Item label="用户 ID">{me?.id}</Descriptions.Item>
          <Descriptions.Item label="注册时间">
            {me?.created_at ? fmtBeijing(me.created_at) : '—'}
          </Descriptions.Item>
          <Descriptions.Item label="姓名">{me?.full_name || '未填写'}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="编辑资料" style={{ marginBottom: 24 }}>
        <Form form={profileForm} layout="vertical" onFinish={onSaveProfile} style={{ maxWidth: 480 }}>
          <Form.Item name="full_name" label="姓名">
            <Input placeholder="请输入姓名" />
          </Form.Item>
          <Form.Item
            name="email"
            label="邮箱"
            rules={[{ type: 'email', message: '邮箱格式不正确' }]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={savingProfile}>保存资料</Button>
        </Form>
      </Card>

      <Card title="修改密码">
        <Form form={pwdForm} layout="vertical" onFinish={onChangePassword} style={{ maxWidth: 480 }}>
          <Form.Item
            name="old_password"
            label="原密码"
            rules={[{ required: true, message: '请输入原密码' }]}
          >
            <Input.Password placeholder="请输入当前密码" />
          </Form.Item>
          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '新密码至少 6 位' },
            ]}
          >
            <Input.Password placeholder="至少 6 位" />
          </Form.Item>
          <Form.Item
            name="confirm_password"
            label="确认新密码"
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请再次输入新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve()
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'))
                },
              }),
            ]}
          >
            <Input.Password placeholder="再次输入新密码" />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={savingPwd}>修改密码</Button>
        </Form>
      </Card>
    </div>
  )
}
