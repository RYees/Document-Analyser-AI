'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { 
  Play, 
  Loader2, 
  ArrowLeft,
  Settings,
  CheckCircle
} from 'lucide-react'
import Link from 'next/link'
import { createPipeline } from '@/lib/api'
import type { PipelineRequest } from '@/types/api'

export default function CreatePipelinePage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch
  } = useForm<PipelineRequest>({
    defaultValues: {
      query: 'transparency in blockchain technology',
      research_domain: 'Blockchain Technology',
      max_results: 10,
      year_from: 2020,
      year_to: 2024,
      quality_threshold: 0.7,
      pipeline_config: {
        enable_supervisor: true,
        auto_retry_failed_steps: true,
        save_intermediate_results: true
      }
    }
  })

  const onSubmit = async (data: PipelineRequest) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await createPipeline(data)
      if (response.success) {
        // Redirect to pipeline details page
        router.push(`/pipelines/${response.pipeline_id}`)
      } else {
        setError('Failed to create pipeline')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
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
            <h1 className="text-2xl font-bold text-gray-900">Create New Pipeline</h1>
            <p className="text-gray-600 mt-1">
              Start a complete research pipeline with all agents
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pipeline Form */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Pipeline Configuration</h2>
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Basic Configuration */}
              <div className="space-y-4">
                <h3 className="text-md font-medium text-gray-900">Basic Configuration</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Research Query *
                  </label>
                  <input
                    {...register('query', { required: 'Research query is required' })}
                    type="text"
                    placeholder="Enter your research query..."
                    className="w-full px-3 py-2 text-black border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  {errors.query && (
                    <p className="text-red-500 text-sm mt-1">{errors.query.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Research Domain *
                  </label>
                  <input
                    {...register('research_domain', { required: 'Research domain is required' })}
                    type="text"
                    placeholder="Enter research domain..."
                    className="w-full px-3 py-2 text-black border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  {errors.research_domain && (
                    <p className="text-red-500 text-sm mt-1">{errors.research_domain.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Results
                    </label>
                    <input
                      {...register('max_results', { 
                        valueAsNumber: true,
                        min: { value: 1, message: 'Minimum 1' },
                        max: { value: 50, message: 'Maximum 50' }
                      })}
                      type="number"
                      min="1"
                      max="50"
                      className="w-full px-3 py-2 text-black border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    {errors.max_results && (
                      <p className="text-red-500 text-sm mt-1">{errors.max_results.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm text-black font-medium text-gray-700 mb-2">
                      Year From
                    </label>
                    <input
                      {...register('year_from', { valueAsNumber: true })}
                      type="number"
                      min="1900"
                      max="2030"
                      className="w-full px-3 py-2 text-black border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Year To
                    </label>
                    <input
                      {...register('year_to', { valueAsNumber: true })}
                      type="number"
                      min="1900"
                      max="2030"
                      className="w-full px-3 py-2 text-black border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quality Threshold
                  </label>
                  <input
                    {...register('quality_threshold', { 
                      valueAsNumber: true,
                      min: { value: 0, message: 'Minimum 0' },
                      max: { value: 1, message: 'Maximum 1' }
                    })}
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    className="w-full px-3 py-2 text-black border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  {errors.quality_threshold && (
                    <p className="text-red-500 text-sm mt-1">{errors.quality_threshold.message}</p>
                  )}
                </div>
              </div>

              {/* Advanced Configuration */}
              <div className="space-y-4">
                <h3 className="text-md font-medium text-gray-900">Advanced Configuration</h3>
                
                <div className="space-y-3">
                  <label className="flex items-center space-x-3">
                    <input
                      {...register('pipeline_config.enable_supervisor')}
                      type="checkbox"
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Enable Supervisor Agent</span>
                  </label>
                  
                  <label className="flex items-center space-x-3">
                    <input
                      {...register('pipeline_config.auto_retry_failed_steps')}
                      type="checkbox"
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Auto-retry Failed Steps</span>
                  </label>
                  
                  <label className="flex items-center space-x-3">
                    <input
                      {...register('pipeline_config.save_intermediate_results')}
                      type="checkbox"
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Save Intermediate Results</span>
                  </label>
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex items-center space-x-3 pt-4">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  ) : (
                    <Play className="w-5 h-5 mr-2" />
                  )}
                  {isLoading ? 'Creating Pipeline...' : 'Start Pipeline'}
                </button>
                
                <Link
                  href="/pipelines"
                  className="px-6 py-3 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </Link>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <p className="text-red-700">{error}</p>
                </div>
              )}
            </form>
          </div>
        </div>

        {/* Pipeline Overview */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Pipeline Overview</h3>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 font-medium">1</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Data Extraction</p>
                  <p className="text-sm text-gray-500">Fetch academic papers</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                  <span className="text-purple-600 font-medium">2</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Literature Review</p>
                  <p className="text-sm text-gray-500">Generate comprehensive review</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                  <span className="text-orange-600 font-medium">3</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Initial Coding</p>
                  <p className="text-sm text-gray-500">Perform open coding</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                  <span className="text-indigo-600 font-medium">4</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Thematic Grouping</p>
                  <p className="text-sm text-gray-500">Group codes into themes</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-pink-100 rounded-full flex items-center justify-center">
                  <span className="text-pink-600 font-medium">5</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Theme Refinement</p>
                  <p className="text-sm text-gray-500">Polish and refine themes</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center">
                  <span className="text-teal-600 font-medium">6</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Report Generation</p>
                  <p className="text-sm text-gray-500">Generate final report</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2">What happens next?</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Pipeline will start automatically</li>
              <li>• Each agent runs sequentially</li>
              <li>• Progress is tracked in real-time</li>
              <li>• Results are saved at each step</li>
              <li>• Final report is generated</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
} 