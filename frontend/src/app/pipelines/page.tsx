'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  Plus, 
  Search, 
  Filter, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Eye,
  Trash2,
  RefreshCw
} from 'lucide-react'
import { listPipelines, deletePipeline } from '@/lib/api'
import type { PipelineResponse } from '@/types/api'

export default function PipelinesPage() {
  const [pipelines, setPipelines] = useState<PipelineResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [deletingPipeline, setDeletingPipeline] = useState<string | null>(null)

  useEffect(() => {
    fetchPipelines()
  }, [])

  const fetchPipelines = async () => {
    try {
      setIsLoading(true)
      const response = await listPipelines({ limit: 50 })
      setPipelines(response || [])
    } catch (error) {
      console.error('Failed to fetch pipelines:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeletePipeline = async (pipelineId: string) => {
    if (!confirm('Are you sure you want to delete this pipeline? This action cannot be undone.')) {
      return
    }

    try {
      setDeletingPipeline(pipelineId)
      const response = await deletePipeline(pipelineId)
      if (response.success) {
        // Remove the deleted pipeline from the list
        setPipelines(pipelines.filter(p => p.pipeline_id !== pipelineId))
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

  const filteredPipelines = pipelines.filter(pipeline => {
    const matchesSearch = pipeline.data?.query?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         pipeline.data?.research_domain?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || pipeline.status === statusFilter
    return matchesSearch && matchesStatus
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Pipeline Management</h1>
          <p className="text-gray-600 mt-1">
            Monitor and manage your research pipelines
          </p>
        </div>
        <Link
          href="/pipelines/create"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Pipeline
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search pipelines..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="halted">Halted</option>
            </select>
          </div>
          <button
            onClick={fetchPipelines}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Pipelines List */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Pipelines ({filteredPipelines.length})
          </h2>
        </div>
        
        {isLoading ? (
          <div className="p-6 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-2">Loading pipelines...</p>
          </div>
        ) : filteredPipelines.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {filteredPipelines.map((pipeline) => (
              <div key={pipeline.pipeline_id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(pipeline.status)}
                    <div>
                      <h3 className="font-medium text-gray-900">
                        {pipeline.data?.query || 'Untitled Pipeline'}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {pipeline.data?.research_domain || 'No domain specified'}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        Started: {new Date(pipeline.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(pipeline.status)}`}>
                      {pipeline.status}
                    </span>
                    
                    <div className="flex items-center space-x-2">
                      <Link
                        href={`/pipelines/${pipeline.pipeline_id}`}
                        className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                        title="View details"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>
                      
                      <button
                        onClick={() => handleDeletePipeline(pipeline.pipeline_id)}
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
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 text-center">
            <p className="text-gray-500">No pipelines found</p>
            <Link
              href="/pipelines/create"
              className="inline-flex items-center mt-2 text-blue-600 hover:text-blue-700 font-medium"
            >
              <Plus className="w-4 h-4 mr-1" />
              Create your first pipeline
            </Link>
          </div>
        )}
      </div>
    </div>
  )
} 