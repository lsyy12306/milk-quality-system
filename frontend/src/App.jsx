import React from 'react'
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Button, message } from 'antd'
import {
  ExperimentOutlined, HistoryOutlined, InfoCircleOutlined,
  LogoutOutlined, RobotOutlined, DashboardOutlined, UserOutlined, ShopOutlined,
} from '@ant-design/icons'
import { isAuth, clearToken, clearUsername, getUsername } from './auth'
import Predict from './pages/Predict'
import History from './pages/History'
import Indicators from './pages/Indicators'
import AgentChat from './pages/AgentChat'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import SourceManager from './pages/SourceManager'
import Login from './pages/Login'
import Register from './pages/Register'

const { Header, Content, Sider } = Layout

function RequireAuth({ children }) {
  const location = useLocation()
  if (!isAuth()) return <Navigate to="/login" state={{ from: location }} replace />
  return children
}

export default function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const username = getUsername()

  const handleLogout = () => {
    clearToken(); clearUsername()
    message.success('已退出登录')
    navigate('/login')
  }

  const menuItems = [
    { key: '/predict', icon: <ExperimentOutlined />, label: '品质分级' },
    { key: '/dashboard', icon: <DashboardOutlined />, label: '分析仪表盘' },
    { key: '/agent', icon: <RobotOutlined />, label: '智能助手' },
    { key: '/history', icon: <HistoryOutlined />, label: '历史记录' },
    { key: '/sources', icon: <ShopOutlined />, label: '来源管理' },
    { key: '/indicators', icon: <InfoCircleOutlined />, label: '指标说明' },
    { key: '/profile', icon: <UserOutlined />, label: '个人中心' },
  ]

  if (!isAuth()) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0" theme="dark">
        <div style={{ color: '#fff', fontWeight: 600, padding: 16, fontSize: 16 }}>
          牛奶品质分级
        </div>
        <Menu
          theme="dark" mode="inline" selectedKeys={[location.pathname]}
          items={menuItems} onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingInline: 24 }}>
          <span style={{ fontWeight: 600 }}>牛奶品质分级系统</span>
          <span>
            <span style={{ marginRight: 16 }}>你好，{username || '用户'}</span>
            <Button icon={<LogoutOutlined />} onClick={handleLogout}>退出</Button>
          </span>
        </Header>
        <Content style={{ margin: 24 }}>
          <Routes>
            <Route path="/predict" element={<RequireAuth><Predict /></RequireAuth>} />
            <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
            <Route path="/agent" element={<RequireAuth><AgentChat /></RequireAuth>} />
            <Route path="/history" element={<RequireAuth><History /></RequireAuth>} />
            <Route path="/sources" element={<RequireAuth><SourceManager /></RequireAuth>} />
            <Route path="/indicators" element={<RequireAuth><Indicators /></RequireAuth>} />
            <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
            <Route path="*" element={<Navigate to="/predict" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}
