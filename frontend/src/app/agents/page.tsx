'use client'

import { useState } from 'react'
import Link from 'next/link'
import { AGENT_TYPES } from '@/lib/utils'
import { TestTube, Play, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)

  const agentStatus = {
    dataExtractor: 'ready',
    retriever: 'ready',
    literatureReview: 'ready',
    initialCoding: 'ready',
    thematicGrouping: 'ready',
    themeRefiner: 'ready',
    reportGenerator: 'ready'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'running':
        return <Clock className="w-4 h-4 text-blue-600" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-600" />
      default:
        return <CheckCircle className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'bg-green-50 text-green-700 border-green-200'
      case 'running':
        return 'bg-blue-50 text-blue-700 border-blue-200'
      case 'error':
        return 'bg-red-50 text-red-700 border-red-200'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agent Testing Hub</h1>
          <p className="text-gray-600 mt-1">
            Test individual research agents and build custom workflows
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            href="/workflow"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <TestTube className="w-4 h-4 mr-2" />
            Build Workflow
          </Link>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(AGENT_TYPES).map(([key, agent]) => {
          const status = agentStatus[key as keyof typeof agentStatus]
          return (
            <div
              key={key}
              className={cn(
                "bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-all duration-200 cursor-pointer",
                selectedAgent === key && "ring-2 ring-blue-500 ring-offset-2"
              )}
              onClick={() => setSelectedAgent(key)}
            >
              {/* Agent Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="text-2xl">{agent.icon}</div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={cn(
                        "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border",
                        getStatusColor(status)
                      )}>
                        {getStatusIcon(status)}
                        <span className="ml-1 capitalize">{status}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Agent Description */}
              <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                {agent.description}
              </p>

              {/* Agent Actions */}
              <div className="flex items-center justify-between">
                <Link
                  href={`/agents/${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`}
                  className="inline-flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm font-medium"
                >
                  <Play className="w-4 h-4 mr-1" />
                  Test Agent
                </Link>
                <div className="text-xs text-gray-500">
                  Ready to test
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Start Section */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">
          Quick Start Workflows
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <h3 className="font-medium text-gray-900 mb-2">Literature Review</h3>
            <p className="text-sm text-gray-600 mb-3">
              Extract documents and generate literature review
            </p>
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              <span>1. Data Extractor</span>
              <span>→</span>
              <span>2. Literature Review</span>
            </div>
          </div>
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <h3 className="font-medium text-gray-900 mb-2">Thematic Analysis</h3>
            <p className="text-sm text-gray-600 mb-3">
              Code documents and group into themes
            </p>
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              <span>1. Initial Coding</span>
              <span>→</span>
              <span>2. Thematic Grouping</span>
            </div>
          </div>
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <h3 className="font-medium text-gray-900 mb-2">Full Pipeline</h3>
            <p className="text-sm text-gray-600 mb-3">
              Complete research pipeline from start to finish
            </p>
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              <span>All Agents</span>
              <span>→</span>
              <span>Report</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 