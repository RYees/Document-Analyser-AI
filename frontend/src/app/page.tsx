'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  BarChart3, 
  Play, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp,
  FileText,
  TestTube,
  GitBranch,
  Activity,
  Trash2
} from 'lucide-react'
import { getPipelineStatistics, listPipelines, deletePipeline } from '@/lib/api'
import type { PipelineStatistics, PipelineResponse } from '@/types/api'

export default function DashboardPage() {
  const [statistics, setStatistics] = useState<PipelineStatistics | null>(null)
  const [recentPipelines, setRecentPipelines] = useState<PipelineResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [deletingPipeline, setDeletingPipeline] = useState<string | null>(null)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsResponse, pipelinesResponse] = await Promise.all([
          getPipelineStatistics(),
          listPipelines({ limit: 5 })
        ])

        if (statsResponse.success && statsResponse.data) {
          setStatistics(statsResponse.data)
        }

        setRecentPipelines(pipelinesResponse || [])
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Clock className="w-4 h-4 text-blue-600" />
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-600" />
      default:
        return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-blue-50 text-blue-700 border-blue-200'
      case 'completed':
        return 'bg-green-50 text-green-700 border-green-200'
      case 'failed':
        return 'bg-red-50 text-red-700 border-red-200'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200'
    }
  }

  const handleDeletePipeline = async (pipelineId: string, e: React.MouseEvent) => {
    e.preventDefault() // Prevent navigation when clicking delete
    e.stopPropagation() // Prevent event bubbling
    
    if (!confirm('Are you sure you want to delete this pipeline? This action cannot be undone.')) {
      return
    }

    try {
      setDeletingPipeline(pipelineId)
      const response = await deletePipeline(pipelineId)
      if (response.success) {
        // Remove the deleted pipeline from the list
        setRecentPipelines(recentPipelines.filter(p => p.pipeline_id !== pipelineId))
      } else {
        alert('Failed to delete pipeline: ' + (response.error || 'Unknown error'))
      }
    } catch (error) {
      console.error('Failed to delete pipeline:', error)
      alert('Failed to delete pipeline: ' + (error instanceof Error ? error.message : 'Unknown error'))
    } finally {
      setDeletingPipeline(null)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Activity className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Research Pipeline Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Monitor your research pipelines and agent performance
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            href="/pipelines/create"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Play className="w-4 h-4 mr-2" />
            Start New Pipeline
          </Link>
          <Link
            href="/agents"
            className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <TestTube className="w-4 h-4 mr-2" />
            Test Agents
          </Link>
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Pipelines</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.total_pipelines}</p>
              </div>
              <div className="p-2 bg-blue-50 rounded-lg">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-green-600">{statistics.completed}</p>
              </div>
              <div className="p-2 bg-green-50 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Running</p>
                <p className="text-2xl font-bold text-blue-600">{statistics.running}</p>
              </div>
              <div className="p-2 bg-blue-50 rounded-lg">
                <Clock className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-purple-600">
                  {statistics.success_rate.toFixed(1)}%
                </p>
              </div>
              <div className="p-2 bg-purple-50 rounded-lg">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          href="/agents/data-extractor"
          className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-all duration-200"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="text-2xl">📄</div>
            <div>
              <h3 className="font-semibold text-gray-900">Data Extractor</h3>
              <p className="text-sm text-gray-600">Extract academic papers</p>
            </div>
          </div>
          <p className="text-sm text-gray-500">
            Fetch and extract academic papers from external sources
          </p>
        </Link>

        <Link
          href="/agents/literature-review"
          className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-all duration-200"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="text-2xl">📚</div>
            <div>
              <h3 className="font-semibold text-gray-900">Literature Review</h3>
              <p className="text-sm text-gray-600">Generate reviews</p>
            </div>
          </div>
          <p className="text-sm text-gray-500">
            Generate comprehensive literature reviews from documents
          </p>
        </Link>

        <Link
          href="/workflow"
          className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-all duration-200"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="text-2xl">🔬</div>
            <div>
              <h3 className="font-semibold text-gray-900">Workflow Builder</h3>
              <p className="text-sm text-gray-600">Build custom workflows</p>
            </div>
          </div>
          <p className="text-sm text-gray-500">
            Create custom research workflows with multiple agents
          </p>
        </Link>
      </div>

      {/* Recent Pipelines */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Recent Pipelines</h2>
            <Link
              href="/pipelines"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              View all
            </Link>
          </div>
        </div>
        <div className="p-6">
          {recentPipelines.length > 0 ? (
            <div className="space-y-4">
              {recentPipelines.map((pipeline) => (
                <div
                  key={pipeline.pipeline_id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <Link
                    href={`/pipelines/${pipeline.pipeline_id}`}
                    className="flex items-center space-x-4 flex-1 cursor-pointer"
                  >
                    {getStatusIcon(pipeline.status)}
                    <div>
                      <h3 className="font-medium text-gray-900">
                        {pipeline.data?.query || 'Untitled Pipeline'}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {pipeline.data?.research_domain || 'No domain specified'}
                      </p>
                    </div>
                  </Link>
                  <div className="flex items-center space-x-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(pipeline.status)}`}>
                      {pipeline.status}
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(pipeline.timestamp).toLocaleDateString()}
                    </span>
                    <button
                      onClick={(e) => handleDeletePipeline(pipeline.pipeline_id, e)}
                      disabled={deletingPipeline === pipeline.pipeline_id}
                      className={`p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors ${
                        deletingPipeline === pipeline.pipeline_id ? 'opacity-50 cursor-not-allowed' : ''
                      }`}
                      title="Delete pipeline"
                    >
                      {deletingPipeline === pipeline.pipeline_id ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No pipelines yet</p>
              <Link
                href="/pipelines/create"
                className="inline-flex items-center mt-2 text-blue-600 hover:text-blue-700 font-medium"
              >
                <Play className="w-4 h-4 mr-1" />
                Start your first pipeline
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
