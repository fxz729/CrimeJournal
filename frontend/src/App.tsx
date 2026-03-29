import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './lib/auth'
import Home from './pages/Home'
import LandingV2 from './pages/LandingV2'
import Login from './pages/Login'
import Register from './pages/Register'
import Search from './pages/Search'
import CaseDetail from './pages/CaseDetail'
import Favorites from './pages/Favorites'
import Account from './pages/Account'
import Upgrade from './pages/Upgrade'
import Docs from './pages/Docs'
import About from './pages/About'
import NotFound from './pages/NotFound'
import SharedCase from './pages/SharedCase'
import CaseDetailBySlug from './pages/CaseDetailBySlug'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 dark:border-primary-400"></div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingV2 />} />
      <Route path="/home" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/search" element={<Search />} />
      <Route path="/docs" element={<Docs />} />
      <Route path="/about" element={<About />} />
      <Route path="/favorites" element={
        <ProtectedRoute>
          <Favorites />
        </ProtectedRoute>
      } />
      <Route path="/account" element={
        <ProtectedRoute>
          <Account />
        </ProtectedRoute>
      } />
      <Route path="/upgrade" element={<Upgrade />} />
      {/* Case detail pages - publicly accessible (API supports optional auth) */}
      <Route path="/cases/:country/:type/:slug" element={<CaseDetailBySlug />} />
      <Route path="/cases/:id" element={<CaseDetail />} />
      <Route path="/shared/:token" element={<SharedCase />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default App
