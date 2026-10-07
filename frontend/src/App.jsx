import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import LocationPicker from './pages/LocationPicker'
import Parameters from './pages/Parameters'
import Recommendations from './pages/Recommendations'
import CropRotation from './pages/CropRotation'
import Login from './pages/Login'
import Register from './pages/Register'

function Shell() {
  const { pathname } = useLocation()
  return (
      <div className="bg-paper min-h-screen font-sans">
        <Navbar />
        <div key={pathname} className="page-enter max-w-7xl mx-auto p-6">
          <Routes>
            <Route path="/"                index element={<Home />} />
            <Route path="/location"        element={<LocationPicker />} />
            <Route path="/parameters"      element={<Parameters />} />
            <Route path="/recommendations" element={<Recommendations />} />
            <Route path="/rotation"        element={<CropRotation />} />
            <Route path="/login"           element={<Login />} />
            <Route path="/register"        element={<Register />} />
            <Route path="*"               element={<Navigate to="/" />} />
          </Routes>
        </div>
      </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Shell />
    </BrowserRouter>
  )
}
