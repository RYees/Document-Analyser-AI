'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  TestTube,
  GitBranch,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  FlaskConical,
  Search,
  BookOpen,
  Target,
  Link as LinkIcon,
  Sparkles,
  FileCheck
} from 'lucide-react'

const navigation = [
  {
    name: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
    description: 'Overview and statistics'
  },
  {
    name: 'Agent Testing',
    href: '/agents',
    icon: TestTube,
    description: 'Test individual agents'
  },
  {
    name: 'Pipeline Management',
    href: '/pipelines',
    icon: GitBranch,
    description: 'Manage research pipelines'
  },
  {
    name: 'Workflow Builder',
    href: '/workflow',
    icon: FlaskConical,
    description: 'Build agent workflows'
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: FileText,
    description: 'Generated reports'
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'System configuration'
  }
]

const agentQuickLinks = [
  {
    name: 'Data Extractor',
    href: '/agents/data-extractor',
    icon: Search,
    color: 'text-blue-600'
  },
  {
    name: 'Retriever',
    href: '/agents/retriever',
    icon: Search,
    color: 'text-green-600'
  },
  {
    name: 'Literature Review',
    href: '/agents/literature-review',
    icon: BookOpen,
    color: 'text-purple-600'
  },
  {
    name: 'Initial Coding',
    href: '/agents/initial-coding',
    icon: Target,
    color: 'text-orange-600'
  },
  {
    name: 'Thematic Grouping',
    href: '/agents/thematic-grouping',
    icon: LinkIcon,
    color: 'text-indigo-600'
  },
  {
    name: 'Theme Refiner',
    href: '/agents/theme-refiner',
    icon: Sparkles,
    color: 'text-pink-600'
  },
  {
    name: 'Report Generator',
    href: '/agents/report-generator',
    icon: FileCheck,
    color: 'text-teal-600'
  }
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

  return (
    <div className={cn(
      "flex flex-col bg-white border-r border-gray-200 transition-all duration-300",
      collapsed ? "w-16" : "w-64"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {!collapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <TestTube className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Research AI</h1>
              <p className="text-xs text-gray-500">Pipeline Lab</p>
            </div>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded-md hover:bg-gray-100 transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4 text-gray-600" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-gray-600" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-50 text-blue-700 border border-blue-200"
                  : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && (
                <div className="flex-1">
                  <div>{item.name}</div>
                  <div className="text-xs text-gray-500 font-normal">
                    {item.description}
                  </div>
                </div>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Agent Quick Links */}
      {!collapsed && (
        <div className="p-4 border-t border-gray-200">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Quick Agent Access
          </h3>
          <div className="space-y-1">
            {agentQuickLinks.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center space-x-2 px-2 py-1.5 rounded text-xs font-medium transition-colors",
                    isActive
                      ? "bg-gray-100 text-gray-900"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  )}
                >
                  <item.icon className={cn("w-4 h-4", item.color)} />
                  <span>{item.name}</span>
                </Link>
              )
            })}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        {!collapsed && (
          <div className="text-xs text-gray-500">
            <div className="font-medium">Research Pipeline API</div>
            <div>v1.0.0</div>
          </div>
        )}
      </div>
    </div>
  )
} 