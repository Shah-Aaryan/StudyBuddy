'use client'

import React from 'react'
import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'
import {
  Brain,
  BarChart3,
  BookOpen,
  Target,
  Moon,
  Sun,
  User,
  Wifi,
  WifiOff,
  Circle,
  Clock,
  LogOut,
  Settings
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { useAuth } from '@/lib/contexts/AuthContext'
import { formatTime } from '@/lib/utils'

interface NavbarProps {
  darkMode: boolean
  toggleDarkMode: () => void
  isConnected: boolean
  isRecording: boolean
  sessionTime: number
  onLogout: () => void

}

const Navbar: React.FC<NavbarProps> = ({
  darkMode,
  toggleDarkMode,
  isConnected,
  isRecording,
  sessionTime,
  onLogout
}) => {
  const pathname = usePathname()
  const router = useRouter()
  const { user } = useAuth()

  const navItems = [
    { name: 'Dashboard', path: '/', icon: Brain },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Resources', path: '/resources', icon: BookOpen },
    { name: 'Reports', path: '/reports', icon: Target }
  ]

  const isActive = (path: string) => pathname === path

  const handleLogout = () => {
    onLogout()
    router.push('/login')
  }

  return (
    <nav className="bg-white dark:bg-gray-900 shadow-md border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex justify-between items-center flex-wrap gap-y-3">
          {/* Left - Logo & Nav Links */}
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2">
              <Brain className="h-7 w-7 text-blue-600 dark:text-blue-400" />
              <span className="text-lg font-bold text-gray-900 dark:text-white">AI Coach</span>
            </Link>
            <div className="hidden md:flex items-center space-x-2">
              {navItems.map(({ name, path, icon: Icon }) => (
                <Link
                  key={name}
                  href={path}
                  className={`flex items-center px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive(path)
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-800 dark:text-blue-300'
                      : 'text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-1.5" />
                  {name}
                </Link>
              ))}
            </div>
          </div>

          {/* Right - Controls */}
          <div className="flex items-center space-x-3">
            {/* Connection status */}
            <div
              className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                isConnected
                  ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                  : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
              }`}
            >
              {isConnected ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>

            {/* Recording status */}
            {isRecording && (
              <div className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium dark:bg-red-900 dark:text-red-300 animate-pulse">
                <Circle className="h-2 w-2 fill-current" />
                Recording
              </div>
            )}

            {/* Session timer */}
            {isRecording && (
              <div className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium dark:bg-blue-900 dark:text-blue-300">
                <Clock className="h-3 w-3" />
                {formatTime(new Date(sessionTime * 1000))}
              </div>
            )}

            {/* Dark Mode Toggle */}
            <Button
              variant="ghost"
              size="sm"
              className="rounded-full"
              onClick={toggleDarkMode}
            >
              {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>

            {/* Settings */}
            <Button
              variant="ghost"
              size="sm"
              className="rounded-full"
              onClick={() => router.push('/settings')}
            >
              <Settings className="h-4 w-4" />
            </Button>

            {/* Logout */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="rounded-full"
            >
              <LogOut className="h-4 w-4 text-red-600" />
            </Button>

            {/* Avatar */}
            <div className="flex items-center gap-2">
              <Avatar className="h-8 w-8">
                <AvatarImage src="" alt={user?.username || 'User'} />
                <AvatarFallback className="bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                  <User className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 hidden sm:block">
                {user?.username || 'Guest'}
              </span>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden pt-3 flex flex-wrap gap-2">
          {navItems.map(({ name, path, icon: Icon }) => (
            <Link
              key={name}
              href={path}
              className={`flex items-center px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                isActive(path)
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-800 dark:text-blue-300'
                  : 'text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <Icon className="h-4 w-4 mr-1.5" />
              {name}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}

export default Navbar
