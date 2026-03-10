'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'

export function useAuth() {
  const router = useRouter()
  const pathname = usePathname()
  const { user, isAuthenticated, isLoading, checkAuth, logout } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const requireAuth = () => {
    if (!isAuthenticated && !isLoading) {
      router.push(`/auth/login?redirect=${pathname}`)
    }
  }

  const requireAgent = () => {
    if (!isAuthenticated && !isLoading) {
      router.push(`/auth/login?redirect=${pathname}`)
    } else if (user && !user.is_agent) {
      router.push('/dashboard')
    }
  }

  const requireAdmin = () => {
    if (!isAuthenticated && !isLoading) {
      router.push(`/auth/login?redirect=${pathname}`)
    } else if (user && !user.is_admin) {
      router.push('/dashboard')
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    logout,
    requireAuth,
    requireAgent,
    requireAdmin,
  }
}
