import { Routes, Route } from 'react-router-dom'
import StudentHome from './pages/StudentHome'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sprout-50 to-sprout-100">
      <Routes>
        <Route path="/" element={<StudentHome />} />
        {/* 未来可以添加更多路由 */}
        {/* <Route path="/parent" element={<ParentDashboard />} /> */}
      </Routes>
    </div>
  )
}

export default App
