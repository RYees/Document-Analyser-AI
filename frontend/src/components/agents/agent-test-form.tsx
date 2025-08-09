'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Play, Loader2, CheckCircle, AlertCircle, Copy, Download } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { AgentResponse } from '@/types/api'

interface AgentTestFormProps {
  agentType: string
  agentName: string
  description: string
  icon: string
  color: string
  onSubmit: (data: any) => Promise<AgentResponse>
  defaultValues?: any
  fields: Array<{
    name: string
    label: string
    type: 'text' | 'textarea' | 'number' | 'select' | 'json'
    required?: boolean
    placeholder?: string
    options?: Array<{ value: string; label: string }>
    defaultValue?: any
  }>
}

export function AgentTestForm({
  agentType,
  agentName,
  description,
  icon,
  color,
  onSubmit,
  defaultValues = {},
  fields
}: AgentTestFormProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<AgentResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm({
    defaultValues
  })

  const handleFormSubmit = async (data: any) => {
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await onSubmit(data)
      setResult(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const downloadResult = () => {
    if (!result) return
    
    const blob = new Blob([JSON.stringify(result, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${agentType}-result.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const renderField = (field: any) => {
    const { name, label, type, required, placeholder, options, defaultValue } = field

    switch (type) {
      case 'textarea':
        return (
          <textarea
            {...register(name, { required: required && `${label} is required` })}
            placeholder={placeholder}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        )
      
      case 'number':
        return (
          <input
            {...register(name, { 
              required: required && `${label} is required`,
              valueAsNumber: true
            })}
            type="number"
            placeholder={placeholder}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        )
      
      case 'select':
        return (
          <select
            {...register(name, { required: required && `${label} is required` })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {options?.map((option: any) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        )
      
      case 'json':
        return (
          <textarea
            {...register(name, { 
              required: required && `${label} is required`,
              validate: (value) => {
                try {
                  JSON.parse(value)
                  return true
                } catch {
                  return 'Invalid JSON format'
                }
              }
            })}
            placeholder={placeholder || 'Enter JSON data...'}
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
          />
        )
      
      default:
        return (
          <input
            {...register(name, { required: required && `${label} is required` })}
            type="text"
            placeholder={placeholder}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        )
    }
  }

  return (
    <div className="space-y-6">
      {/* Agent Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-4">
          <div className="text-3xl">{icon}</div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{agentName}</h1>
            <p className="text-gray-600 mt-1">{description}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Test Configuration</h2>
          
          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
            {fields.map((field) => (
              <div key={field.name}>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {field.label}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
                </label>
                {renderField(field)}
                {errors[field.name] && (
                  <p className="text-red-500 text-sm mt-1">
                    {errors[field.name]?.message as string}
                  </p>
                )}
              </div>
            ))}

            <div className="flex items-center space-x-3 pt-4">
              <button
                type="submit"
                disabled={isLoading}
                className={cn(
                  "inline-flex items-center px-4 py-2 rounded-md font-medium transition-colors",
                  isLoading
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-blue-600 text-white hover:bg-blue-700"
                )}
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Play className="w-4 h-4 mr-2" />
                )}
                {isLoading ? 'Testing...' : 'Test Agent'}
              </button>
              
              <button
                type="button"
                onClick={() => reset()}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                Reset
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Test Results</h2>
          
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
                <p className="text-gray-600">Testing agent...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <h3 className="text-red-800 font-medium">Error</h3>
              </div>
              <p className="text-red-700 mt-2">{error}</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span className="text-green-800 font-medium">Test Completed</span>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => copyToClipboard(JSON.stringify(result, null, 2))}
                    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                    title="Copy to clipboard"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={downloadResult}
                    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                    title="Download result"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-md p-4">
                <pre className="text-sm text-gray-800 overflow-auto max-h-96">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {!isLoading && !error && !result && (
            <div className="text-center py-8 text-gray-500">
              <p>Run a test to see results here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 