'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft, 
  Play, 
  Pause, 
  RefreshCw, 
  Trash2, 
  Download,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  FileText,
  BarChart3,
  Settings
} from 'lucide-react'
import { 
  getPipelineProgress, 
  getPipelineResults,
  deletePipeline,
  retryPipelineStep,
  haltPipeline,
  downloadPipelineReport
} from '@/lib/api'
import type { PipelineProgress, PipelineResults } from '@/types/api'

export default function PipelineDetailPage() {
  const params = useParams()
  const router = useRouter()
  const pipelineId = params.id as string
  
  const [progress, setProgress] = useState<PipelineProgress | null>(null)
  const [results, setResults] = useState<PipelineResults | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isRetrying, setIsRetrying] = useState(false)
  const [isHalting, setIsHalting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const [expandedSteps, setExpandedSteps] = useState<Record<string, boolean>>({})
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastRefreshTime, setLastRefreshTime] = useState<Date | null>(null)

  useEffect(() => {
    if (pipelineId) {
      fetchPipelineData()
      
      // Smart polling strategy based on pipeline status
      const getPollingInterval = () => {
        if (!progress) return 5000 // Initial load
        switch (progress.status) {
          case 'running':
            return 3000 // More frequent for running pipelines
          case 'failed':
            return 10000 // Less frequent for failed pipelines
          case 'completed':
            return null // No polling for completed pipelines
          default:
            return 5000
        }
      }
      
      const interval = getPollingInterval()
      if (interval) {
        const timer = setInterval(() => {
          fetchPipelineData()
        }, interval)
        
        return () => clearInterval(timer)
      }
    }
  }, [pipelineId, progress?.status]) // Only re-run when pipelineId or status changes

  const fetchPipelineData = async () => {
    try {
      console.log('🔍 Fetching pipeline data for ID:', pipelineId)
      
      // Don't set loading state if we already have data (prevents unnecessary re-renders)
      if (!progress && !results) {
        setIsLoading(true)
      }
      
      const [progressData, resultsData] = await Promise.all([
        getPipelineProgress(pipelineId),
        getPipelineResults(pipelineId)
      ])
      
      console.log('📊 Progress data:', progressData)
      console.log('📊 Results data:', resultsData)
      
      // Only update state if data has actually changed
      if (progressData.success && progressData.data) {
        const newProgress = progressData.data
        const hasProgressChanged = !progress || 
          progress.status !== newProgress.status ||
          progress.current_step !== newProgress.current_step
        
        if (hasProgressChanged) {
          console.log('✅ Setting progress data:', newProgress)
          setProgress(newProgress)
        }
      } else {
        console.log('❌ Progress data not successful:', progressData)
      }
      
      if (resultsData.success && resultsData.data) {
        const newResults = resultsData.data
        const hasResultsChanged = !results || 
          JSON.stringify(results) !== JSON.stringify(newResults)
        
        if (hasResultsChanged) {
          console.log('✅ Setting results data:', newResults)
          console.log('🔍 Results data structure:', {
            hasResults: !!(newResults as any).results,
            resultsKeys: newResults ? Object.keys(newResults) : [],
            resultsStructure: newResults ? Object.keys((newResults as any).results || {}) : []
          })
          setResults(newResults)
        }
      } else {
        console.log('❌ Results data not successful:', resultsData)
      }
    } catch (err) {
      console.error('❌ Error fetching pipeline data:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch pipeline data')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRetryStep = async (stepName: string) => {
    try {
      setIsRetrying(true)
      const response = await retryPipelineStep(pipelineId, stepName)
      if (response.success) {
        await fetchPipelineData()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to retry step')
    } finally {
      setIsRetrying(false)
    }
  }

  const handleHaltPipeline = async () => {
    try {
      setIsHalting(true)
      const response = await haltPipeline(pipelineId, 'User requested halt')
      if (response.success) {
        await fetchPipelineData()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to halt pipeline')
    } finally {
      setIsHalting(false)
    }
  }

  const handleDeletePipeline = async () => {
    if (confirm('Are you sure you want to delete this pipeline? This action cannot be undone.')) {
      try {
        const response = await deletePipeline(pipelineId)
        if (response.success) {
          router.push('/pipelines')
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete pipeline')
      }
    }
  }

  const handleDownloadReport = async (format: string = 'pdf') => {
    if (!results || !(results as any)?.results?.report_generation?.data?.file_path) {
      alert('No report available for download. Please ensure the pipeline has completed successfully.')
      return
    }
    
    setIsDownloading(true)
    try {
      const blob = await downloadPipelineReport(pipelineId, format)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `pipeline_report_${pipelineId}.${format === 'pdf' ? 'pdf' : format === 'markdown' ? 'md' : 'txt'}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      console.log('✅ Report downloaded successfully')
    } catch (error) {
      console.error('Failed to download report:', error)
      alert('Failed to download report. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  const handleManualRefresh = async () => {
    setIsRefreshing(true)
    setLastRefreshTime(new Date())
    await fetchPipelineData()
    setIsRefreshing(false)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Clock className="w-5 h-5 text-blue-600" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'halted':
        return <XCircle className="w-5 h-5 text-orange-600" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
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
      case 'halted':
        return 'bg-orange-50 text-orange-700 border-orange-200'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200'
    }
  }

  const getStepStatus = (stepName: string) => {
    if (!progress?.steps) return 'pending'
    
    // Handle object format where steps are keyed by step number
    const step = (progress.steps as any)[stepName]
    if (step) {
      // If the step status is pending but we have results, it's actually completed
      if (step.status === 'pending' && results && (results as any).results) {
        const resultsData = (results as any).results
        if (resultsData) {
          const resultKeys = Object.keys(resultsData)
          const stepNumber = parseInt(stepName)
          const stepResultKeys: Record<number, string> = {
            1: 'documents',
            2: 'literature_review', 
            3: 'initial_coding',
            4: 'thematic_grouping',
            5: 'theme_refinement',
            6: 'report_generation'
          }
          const expectedResultKey = stepResultKeys[stepNumber]
          if (expectedResultKey && resultKeys.includes(expectedResultKey)) {
            return 'completed'
          }
        }
      }
      return step.status
    }
    
    return 'pending'
  }

  const getStepProgress = (stepName: string) => {
    if (!progress?.steps) return 0
    // Handle both array and object formats
    if (Array.isArray(progress.steps)) {
      const step = progress.steps.find((s: any) => s.name === stepName)
      return step?.progress || 0
    } else {
      // Handle object format where steps are keyed by step number
      const step = (progress.steps as any)[stepName] || (progress.steps as any)[stepName.toLowerCase()]
      return step?.progress || 0
    }
  }

  const renderStep = (stepName: string, title: string, description: string) => {
    const status = getStepStatus(stepName)
    const progress = getStepProgress(stepName)
    const isExpanded = expandedSteps[stepName] || false
    
    // Get step results if available
    const getStepResults = () => {
      if (!results || !(results as any).results) {
        console.log('❌ No results or results.results found:', { results })
        return null
      }
      
      const stepResultKeys: Record<string, string> = {
        '1': 'documents',
        '2': 'literature_review', 
        '3': 'initial_coding',
        '4': 'thematic_grouping',
        '5': 'theme_refinement',
        '6': 'report_generation'
      }
      
      const resultKey = stepResultKeys[stepName]
      const stepResult = resultKey ? (results as any).results[resultKey] : null
      
      console.log(`🔍 Step ${stepName} (${resultKey}) result:`, stepResult)
      return stepResult
    }
    
    const stepResults = getStepResults()
    
    const toggleExpanded = () => {
      setExpandedSteps(prev => ({
        ...prev,
        [stepName]: !prev[stepName]
      }))
    }
    
    return (
      <div key={stepName} className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            {getStatusIcon(status)}
            <div>
              <h3 className="font-medium text-gray-900">{title}</h3>
              <p className="text-sm text-gray-500">{description}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(status)}`}>
              {status}
            </span>
            {status === 'failed' && (
              <button
                onClick={() => handleRetryStep(stepName)}
                disabled={isRetrying}
                className="p-1 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                title="Retry step"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            )}
            {status === 'completed' && (
              <button
                onClick={toggleExpanded}
                className="p-1 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                title={isExpanded ? "Hide results" : "Show results"}
              >
                <div className="flex items-center space-x-1">
                  {stepResults ? (
                    <span className="text-xs bg-green-100 text-green-800 px-1 py-0.5 rounded">
                      Results
                    </span>
                  ) : (
                    <span className="text-xs bg-gray-100 text-gray-600 px-1 py-0.5 rounded">
                      No Data
                    </span>
                  )}
                  {isExpanded ? (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  )}
                </div>
              </button>
            )}
          </div>
        </div>
        
        {status === 'running' && (
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
        
        {/* Step Results Display */}
        {status === 'completed' && isExpanded && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
            <h4 className="font-medium text-gray-900 mb-3">Step Results</h4>
            
            {stepResults ? (
              <>
                {/* Document Retrieval Results */}
                {stepName === '1' && stepResults.data?.documents && (
                  <div className="space-y-3">
                    <div className="text-sm">
                      <span className="font-medium">Documents Retrieved:</span> {stepResults.data.documents.length}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Query:</span> {stepResults.data.query}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Quality Score:</span> {(stepResults.data.quality_metrics?.overall_score * 100).toFixed(1)}%
                    </div>
                    <div className="max-h-32 overflow-y-auto">
                      <div className="text-xs text-gray-600">
                        <strong>Sample Documents:</strong>
                        {stepResults.data.documents.slice(0, 2).map((doc: any, idx: number) => (
                          <div key={idx} className="mt-2 p-2 bg-white rounded border">
                            <div className="font-medium">{doc.title}</div>
                            <div className="text-gray-500">{doc.authors} ({doc.year})</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Literature Review Results */}
                {stepName === '2' && stepResults.data?.summary && (
                  <div className="space-y-3">
                    <div className="text-sm">
                      <span className="font-medium">Documents Analyzed:</span> {stepResults.data.documents_analyzed}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Summary:</span>
                      <div className="mt-1 p-2 bg-white rounded border max-h-32 overflow-y-auto">
                        <div className="text-xs text-gray-600 whitespace-pre-wrap">
                          {stepResults.data.summary.substring(0, 300)}...
                        </div>
                      </div>
                    </div>
                    {stepResults.data.key_findings && (
                      <div className="text-sm">
                        <span className="font-medium">Key Findings:</span>
                        <ul className="mt-1 ml-4 list-disc text-xs text-gray-600">
                          {stepResults.data.key_findings.slice(0, 3).map((finding: string, idx: number) => (
                            <li key={idx}>{finding.substring(0, 100)}...</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Initial Coding Results */}
                {stepName === '3' && stepResults.data?.coding_summary && (
                  <div className="space-y-3">
                    <div className="text-sm">
                      <span className="font-medium">Units Coded:</span> {stepResults.data.coding_summary.total_units_coded}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Unique Codes:</span> {stepResults.data.coding_summary.unique_codes_generated}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Average Confidence:</span> {(stepResults.data.coding_summary.average_confidence * 100).toFixed(1)}%
                    </div>
                    <div className="max-h-32 overflow-y-auto">
                      <div className="text-xs text-gray-600">
                        <strong>Primary Codes:</strong>
                        <div className="mt-1 space-y-1">
                          {stepResults.data.coding_summary.primary_codes.slice(0, 3).map((code: string, idx: number) => (
                            <div key={idx} className="p-1 bg-white rounded border text-xs">
                              {code}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Thematic Grouping Results */}
                {stepName === '4' && stepResults.data?.thematic_summary && (
                  <div className="space-y-3">
                    <div className="text-sm">
                      <span className="font-medium">Themes Generated:</span> {stepResults.data.thematic_summary.total_themes_generated}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Codes Analyzed:</span> {stepResults.data.thematic_summary.total_codes_analyzed}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Average Codes per Theme:</span> {stepResults.data.thematic_summary.average_codes_per_theme}
                    </div>
                    {stepResults.data.themes && (
                      <div className="max-h-32 overflow-y-auto">
                        <div className="text-xs text-gray-600">
                          <strong>Themes:</strong>
                          <div className="mt-1 space-y-1">
                            {stepResults.data.themes.slice(0, 2).map((theme: any, idx: number) => (
                              <div key={idx} className="p-2 bg-white rounded border">
                                <div className="font-medium">{theme.theme_name}</div>
                                <div className="text-gray-500">Codes: {theme.codes?.length || 0}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Theme Refinement Results */}
                {stepName === '5' && stepResults.data?.refinement_summary && (
                  <div className="space-y-3">
                    <div className="text-sm">
                      <span className="font-medium">Themes Refined:</span> {stepResults.data.refinement_summary.total_themes_refined}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Academic Quotes:</span> {stepResults.data.refinement_summary.total_academic_quotes}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Average Quotes per Theme:</span> {stepResults.data.refinement_summary.average_quotes_per_theme}
                    </div>
                    {stepResults.data.refined_themes && (
                      <div className="max-h-32 overflow-y-auto">
                        <div className="text-xs text-gray-600">
                          <strong>Refined Themes:</strong>
                          <div className="mt-1 space-y-1">
                            {stepResults.data.refined_themes.slice(0, 2).map((theme: any, idx: number) => (
                              <div key={idx} className="p-2 bg-white rounded border">
                                <div className="font-medium">{theme.refined_name}</div>
                                <div className="text-gray-500">Quotes: {theme.academic_quotes?.length || 0}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Report Generation Results */}
                {stepName === '6' && stepResults.data?.report_summary && (
                  <div className="space-y-3">
                    <div className="text-sm">
                      <span className="font-medium">Word Count:</span> {stepResults.data.report_summary.word_count}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Report Length:</span> {stepResults.data.report_summary.report_length} characters
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Sections:</span> {Object.keys(stepResults.data.report_summary.sections_included).filter(k => stepResults.data.report_summary.sections_included[k]).length}
                    </div>
                    {stepResults.data.report_content && (
                      <div className="text-sm">
                        <span className="font-medium">Content Preview:</span>
                        <div className="mt-1 p-2 bg-white rounded border max-h-32 overflow-y-auto">
                          <div className="text-xs text-gray-600 whitespace-pre-wrap">
                            {stepResults.data.report_content.substring(0, 300)}...
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </>
            ) : (
              <div className="text-sm text-gray-500">
                {stepResults?.data?.error ? (
                  <div className="text-red-600">
                    <strong>Error:</strong> {stepResults.data.error}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <div className="text-gray-400 mb-2">
                      <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <p>No results data available for this step.</p>
                    <p className="text-xs text-gray-400 mt-1">The step completed but no output was generated.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <span className="text-gray-600">Loading pipeline...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-700">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            href="/pipelines"
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Pipeline: {pipelineId}
            </h1>
            <p className="text-gray-600 mt-1">
              {progress?.query || 'Research Pipeline'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={handleManualRefresh}
            disabled={isRefreshing}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
          
          {progress?.status === 'running' && (
            <button
              onClick={handleHaltPipeline}
              disabled={isHalting}
              className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-300 transition-colors"
            >
              <Pause className="w-4 h-4 mr-2" />
              {isHalting ? 'Halting...' : 'Halt Pipeline'}
            </button>
          )}
          
          <button
            onClick={handleDeletePipeline}
            className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete
          </button>
        </div>
      </div>

      {/* Pipeline Status */}
      {progress && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Pipeline Status</h2>
              {lastRefreshTime && (
                <p className="text-sm text-gray-500 mt-1">
                  Last updated: {lastRefreshTime.toLocaleTimeString()}
                </p>
              )}
            </div>
            <div className="flex items-center space-x-3">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(progress.status)}`}>
                {progress.status}
              </span>
              {progress.status === 'completed' && (
                <button
                  onClick={handleManualRefresh}
                  disabled={isRefreshing}
                  className="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
                  title="Refresh data"
                >
                  <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                </button>
              )}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">{progress.current_step || 0}</div>
              <div className="text-sm text-gray-600">Current Step</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">{progress.total_steps || 6}</div>
              <div className="text-sm text-gray-600">Total Steps</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">
                {progress.created_at ? new Date(progress.created_at).toLocaleDateString() : 'N/A'}
              </div>
              <div className="text-sm text-gray-600">Created</div>
            </div>
          </div>
          
          {progress.status === 'running' && (
            <div className="space-y-3">
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${((progress.current_step || 0) / (progress.total_steps || 6)) * 100}%` }}
                />
              </div>
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>Step {progress.current_step || 0} of {progress.total_steps || 6}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>Live monitoring</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Pipeline Summary */}
      {results && (results as any).results && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Pipeline Summary</h2>
          

          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-blue-900">
                {(results as any)?.results?.documents?.data?.documents?.length || 
                 (results as any)?.results?.data_extraction?.data?.documents_processed || 0}
              </div>
              <div className="text-sm text-blue-700">Documents Processed</div>
            </div>
            
            <div className="bg-green-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-green-900">
                {(results as any)?.results?.thematic_grouping?.data?.thematic_summary?.total_themes_generated || 
                 (results as any)?.results?.theme_refinement?.data?.refinement_summary?.total_themes_refined || 0}
              </div>
              <div className="text-sm text-green-700">Themes Generated</div>
            </div>
            
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-purple-900">
                {(results as any)?.results?.initial_coding?.data?.coding_summary?.total_units_coded || 
                 (results as any)?.results?.initial_coding?.data?.total_codes || 0}
              </div>
              <div className="text-sm text-purple-700">Codes Identified</div>
            </div>
            
            <div className="bg-orange-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-orange-900">
                {(results as any)?.results?.report_generation?.data?.report_summary?.word_count || 0}
              </div>
              <div className="text-sm text-orange-700">Report Words</div>
            </div>
          </div>
        </div>
      )}

      {/* Pipeline Steps */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Pipeline Steps</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {renderStep('1', 'Document Retrieval', 'Fetch academic papers from databases')}
          {renderStep('2', 'Literature Review', 'Generate comprehensive literature review')}
          {renderStep('3', 'Initial Coding', 'Perform open coding on documents')}
          {renderStep('4', 'Thematic Grouping', 'Group codes into themes')}
          {renderStep('5', 'Theme Refinement', 'Polish and refine themes')}
          {renderStep('6', 'Report Generation', 'Generate final research report')}
        </div>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Pipeline Results</h2>
          
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-900">
                  {(results as any)?.results?.documents?.data?.documents?.length || 
                   (results as any)?.results?.data_extraction?.data?.documents_processed || 0}
                </div>
                <div className="text-sm text-blue-700">Documents Processed</div>
              </div>
              
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-900">
                  {(results as any)?.results?.thematic_grouping?.data?.thematic_summary?.total_themes_generated || 
                   (results as any)?.results?.theme_refinement?.data?.refinement_summary?.total_themes_refined || 0}
                </div>
                <div className="text-sm text-green-700">Themes Generated</div>
              </div>
              
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-900">
                  {(results as any)?.results?.initial_coding?.data?.coding_summary?.total_units_coded || 
                   (results as any)?.results?.initial_coding?.data?.total_codes || 0}
                </div>
                <div className="text-sm text-purple-700">Codes Identified</div>
              </div>
              
              <div className="bg-orange-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-orange-900">
                  {(results as any)?.results?.report_generation?.data?.report_summary?.word_count || 0}
                </div>
                <div className="text-sm text-orange-700">Report Words</div>
              </div>
            </div>
            
            {/* Step Results */}
            {(results as any)?.results && (
              <div className="space-y-4">
                <h3 className="font-medium text-gray-900 mb-4">Step Results</h3>
                

                
                {/* Initial Coding Results */}
                {(results as any)?.results?.initial_coding && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">Initial Coding</h4>
                    <div className="text-sm text-gray-700">
                      <p><strong>Total Units:</strong> {(results as any).results.initial_coding.data?.coding_summary?.total_units_coded || 'N/A'}</p>
                      <p><strong>Total Codes:</strong> {(results as any).results.initial_coding.data?.total_codes || 'N/A'}</p>
                    </div>
                  </div>
                )}
                
                {/* Thematic Grouping Results */}
                {(results as any)?.results?.thematic_grouping && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">Thematic Grouping</h4>
                    <div className="text-sm text-gray-700">
                      <p><strong>Total Themes:</strong> {(results as any).results.thematic_grouping.data?.thematic_summary?.total_themes_generated || 'N/A'}</p>
                      <p><strong>Codes Analyzed:</strong> {(results as any).results.thematic_grouping.data?.coded_units_analyzed || 'N/A'}</p>
                    </div>
                  </div>
                )}
                
                {/* Theme Refinement Results */}
                {(results as any)?.results?.theme_refinement && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">Theme Refinement</h4>
                    <div className="text-sm text-gray-700">
                      <p><strong>Themes Refined:</strong> {(results as any).results.theme_refinement.data?.refinement_summary?.total_themes_refined || 'N/A'}</p>
                      <p><strong>Academic Quotes:</strong> {(results as any).results.theme_refinement.data?.refinement_summary?.total_academic_quotes || 'N/A'}</p>
                    </div>
                  </div>
                )}
                
                {/* Report Generation Results */}
                {(results as any)?.results?.report_generation && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">Report Generation</h4>
                    <div className="text-sm text-gray-700">
                      <p><strong>Word Count:</strong> {(results as any).results.report_generation.data?.report_summary?.word_count || 'N/A'}</p>
                      <p><strong>Sections Included:</strong> {(results as any).results.report_generation.data?.report_summary?.sections_included ? 
                        Object.keys((results as any).results.report_generation.data.report_summary.sections_included).join(', ') : 'N/A'}</p>
                      <p><strong>Total References:</strong> {(results as any).results.report_generation.data?.report_summary?.total_references || 'N/A'}</p>
                      <p><strong>Report Length:</strong> {(results as any).results.report_generation.data?.report_summary?.report_length || 'N/A'}</p>
                      <p><strong>File Path:</strong> {(results as any).results.report_generation.data?.file_path || 'N/A'}</p>
                      <p><strong>Generated At:</strong> {(results as any).results.report_generation.data?.generated_at || 'N/A'}</p>
                      {(results as any)?.results?.report_generation?.data?.report_content && (
                        <div className="mt-2">
                          <strong>Report Content Preview:</strong>
                          <div className="bg-white p-2 rounded border mt-1 max-h-32 overflow-y-auto">
                            <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                              {(results as any).results.report_generation.data.report_content.substring(0, 500)}...
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                {/* Literature Review Results */}
                {(results as any)?.results?.literature_review && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">Literature Review</h4>
                    <div className="text-sm text-gray-700">
                      <p><strong>Summary:</strong> {(results as any).results.literature_review.data?.summary || 'N/A'}</p>
                      {(results as any)?.results?.literature_review?.data?.key_findings && (
                        <div className="mt-2">
                          <strong>Key Findings:</strong>
                          <ul className="list-disc list-inside ml-2">
                            {(results as any).results.literature_review.data.key_findings.map((finding: string, index: number) => (
                              <li key={index}>{finding}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {/* Quality Scores */}
            {(results as any)?.quality_scores && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="font-medium text-gray-900 mb-4">Quality Scores</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  {Object.entries((results as any).quality_scores).map(([step, score]: [string, any]) => (
                    <div key={step} className="bg-blue-50 rounded-lg p-3">
                      <div className="text-lg font-bold text-blue-900">
                        {(score as number * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-blue-700 capitalize">
                        {step.replace('_', ' ')}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Download Report */}
            {(results as any)?.results?.report_generation?.data?.file_path && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-5 h-5 text-gray-600" />
                    <div>
                      <h3 className="font-medium text-gray-900">Final Report</h3>
                      <p className="text-sm text-gray-500">Generated research report</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <select 
                      id="download-format"
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      defaultValue="pdf"
                    >
                      <option value="pdf">PDF (.pdf)</option>
                      <option value="markdown">Markdown (.md)</option>
                      <option value="text">Plain Text (.txt)</option>
                    </select>
                    <button 
                      onClick={() => {
                        const format = (document.getElementById('download-format') as HTMLSelectElement)?.value || 'pdf'
                        handleDownloadReport(format)
                      }}
                      disabled={isDownloading}
                      className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      {isDownloading ? 'Downloading...' : 'Download Report'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error Display */}
      {progress?.error_message && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="font-medium text-red-900 mb-2">Pipeline Error</h3>
          <p className="text-red-700">{progress.error_message}</p>
        </div>
      )}
    </div>
  )
} 