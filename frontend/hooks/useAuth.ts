'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'

interface User {
  id: number
  email: string
  username: string
  is_active: boolean
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          // Fetch current user from API
          const response = await apiClient.get('/api/auth/me')
          setUser(response)
        } catch (error) {
          // Token invalid, clear it
          localStorage.removeItem('access_token')
          setUser(null)
        }
      } else {
        setUser(null)
      }
      setIsLoading(false)
    }
    loadUser()
  }, [])

  const login = async (username: string, password: string) => {
    try {
      // FastAPI OAuth2PasswordRequestForm expects form data
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      })

      if (!response.ok) {
        const error = await response.json()
        return { success: false, error: error.detail || 'Login failed' }
      }

      const data = await response.json()
      const { access_token, user: userData } = data
      localStorage.setItem('access_token', access_token)
      // Set user state immediately
      setUser(userData)
      setIsLoading(false)
      return { success: true }
    } catch (error: any) {
      return { success: false, error: error.message || 'Network error' }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  return {
    user,
    isLoading,
    login,
    logout,
  }
}

