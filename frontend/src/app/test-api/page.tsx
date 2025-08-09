'use client'

import { useState, useEffect } from 'react'
import { listPipelines, getPipelineStatistics } from '@/lib/api'

export default function TestApiPage() {
  const [pipelines, setPipelines] = useState<any[]>([])
  const [statistics, setStatistics] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    testApiConnection()
  }, [])

  const testApiConnection = async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('Testing API connection...')
      
      // Test pipeline listing
      const pipelinesResponse = await listPipelines({ limit: 10 })
      console.log('Pipelines response:', pipelinesResponse)
      setPipelines(pipelinesResponse || [])
      
      // Test statistics
      const statsResponse = await getPipelineStatistics()
      console.log('Statistics response:', statsResponse)
      setStatistics(statsResponse?.data || null)
      
    } catch (err) {
      console.error('API test failed:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">API Connection Test</h1>
      
      <button
        onClick={testApiConnection}
        disabled={loading}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300"
      >
        {loading ? 'Testing...' : 'Test API Connection'}
      </button>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-4">
          <h2 className="font-semibold text-red-800">Error:</h2>
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {statistics && (
        <div className="bg-green-50 border border-green-200 rounded p-4">
          <h2 className="font-semibold text-green-800">Statistics:</h2>
          <pre className="text-sm text-green-700 mt-2">
            {JSON.stringify(statistics, null, 2)}
          </pre>
        </div>
      )}

      {pipelines.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded p-4">
          <h2 className="font-semibold text-blue-800">Pipelines ({pipelines.length}):</h2>
          <div className="mt-2 space-y-2">
            {pipelines.map((pipeline, index) => (
              <div key={index} className="text-sm text-blue-700">
                <strong>ID:</strong> {pipeline.pipeline_id} | 
                <strong>Status:</strong> {pipeline.status} | 
                <strong>Query:</strong> {pipeline.data?.query || 'N/A'}
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && !error && pipelines.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
          <p className="text-yellow-800">No pipelines found</p>
        </div>
      )}
    </div>
  )
} 