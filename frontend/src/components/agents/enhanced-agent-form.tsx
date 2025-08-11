'use client'

import { useState, useEffect, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { useRouter } from 'next/navigation'
import { 
  Play, 
  Loader2, 
  CheckCircle, 
  AlertCircle, 
  Copy, 
  Download,
  ArrowRight,
  ChevronDown,
  ChevronRight,
  FileText,
  Code,
  BookOpen,
  Target,
  Link as LinkIcon,
  Sparkles,
  FileCheck,
  Shield,
  Eye,
  X
} from 'lucide-react'
import { cn } from '@/lib/utils'
import type { AgentResponse, SupervisorResult, RetryAgentRequest } from '@/types/api'
import { SupervisorSection } from './supervisor-section'

interface EnhancedAgentFormProps {
  agentType: string
  agentName: string
  description: string
  icon: string
  color: string
  onSubmit: (data: any) => Promise<AgentResponse>
  onSupervisorCheck?: (data: any) => Promise<AgentResponse>
  onRetryAgent?: (data: RetryAgentRequest) => Promise<AgentResponse>
  defaultValues?: any
  fields: Array<{
    name: string
    label: string
    type: 'text' | 'textarea' | 'number' | 'select' | 'multiselect' | 'chips' | 'json' | 'documents' | 'coded_units' | 'themes'
    required?: boolean
    placeholder?: string
    options?: Array<{ value: string; label: string }>
    defaultValue?: any
    helpText?: string
  }>
  nextAgents?: Array<{
    name: string
    href: string
    description: string
    icon: string
  }>
}

export function EnhancedAgentForm({
  agentType,
  agentName,
  description,
  icon,
  color,
  onSubmit,
  onSupervisorCheck,
  onRetryAgent,
  defaultValues = {},
  fields,
  nextAgents = []
}: EnhancedAgentFormProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<AgentResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [expandedSections, setExpandedSections] = useState<string[]>([])
  const [supervisorResult, setSupervisorResult] = useState<SupervisorResult | null>(null)
  const [isSupervisorLoading, setIsSupervisorLoading] = useState(false)
  const [showSupervisor, setShowSupervisor] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState<Record<string, boolean>>({})
  const [docPreview, setDocPreview] = useState<any | null>(null)
  const [cardPreview, setCardPreview] = useState<{ title: string; content: string } | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch
  } = useForm({
    defaultValues
  })

  const [originalInput, setOriginalInput] = useState<any>(null)
  const previousValuesRef = useRef<string>('')

  // Watch form values in real-time to debug
  const watchedValues = watch()
  
  // Update originalInput whenever form values change
  useEffect(() => {
    if (watchedValues && Object.keys(watchedValues).length > 0) {
      // Filter out undefined values to avoid sending them to the backend
      const cleanValues = Object.fromEntries(
        Object.entries(watchedValues).filter(([_, value]) => value !== undefined && value !== null && value !== '')
      )
      
      // Only update if the values have actually changed to prevent infinite loops
      const currentValuesString = JSON.stringify(cleanValues)
      
      if (currentValuesString !== previousValuesRef.current) {
        previousValuesRef.current = currentValuesString
        setOriginalInput(cleanValues)
      }
    }
  }, [watchedValues])

  const handleFormSubmit = async (data: any) => {   
    setIsLoading(true)
    setError(null)
    setResult(null)
    setSupervisorResult(null)
    setShowSupervisor(false)
    setOriginalInput(data)

    try {
      console.log('Calling onSubmit function...')
      const response = await onSubmit(data)
      console.log('Response received:', response)
      setResult(response)
    } catch (err) {
      console.error('Error in form submission:', err)
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSupervisorCheck = async () => {
    if (!result || !onSupervisorCheck || !originalInput) return
    setIsSupervisorLoading(true)
    setError(null)

    try {
      const supervisorData = {
        agent_type: agentType,
        agent_output: result.data,
        original_agent_input: originalInput
      }

      console.log('🔍 [SUPERVISOR DEBUG] Supervisor data being sent:', JSON.stringify(supervisorData, null, 2))
      const response = await onSupervisorCheck(supervisorData)
      console.log('Supervisor response:', response)
      
      if (response.success && response.data) {
        setSupervisorResult(response.data)
        setShowSupervisor(true)
      } else {
        setError('Supervisor check failed')
      }
    } catch (err) {
      console.error('Error in supervisor check:', err)
      setError(err instanceof Error ? err.message : 'Supervisor check failed')
    } finally {
      setIsSupervisorLoading(false)
    }
  }

  const handleRetryAgent = async (retryData: RetryAgentRequest) => {
    if (!onRetryAgent || !originalInput) {
      throw new Error('Retry functionality not available')
    }

    console.log('🔄 [RETRY DEBUG] About to call retry with original input:', JSON.stringify(originalInput, null, 2))
    console.log('🔄 [RETRY DEBUG] max_results in original input:', originalInput.max_results)
    console.log('🔄 [RETRY DEBUG] year_from in original input:', originalInput.year_from)
    console.log('🔄 [RETRY DEBUG] year_to in original input:', originalInput.year_to)

    // Update the retry data to use the correct original input
    const updatedRetryData = {
      ...retryData,
      original_agent_input: originalInput
    }

    console.log('🔄 [RETRY DEBUG] Retry data being sent:', JSON.stringify(updatedRetryData, null, 2))
    const response = await onRetryAgent(updatedRetryData)
    if (response.success) {
      setResult(response)
      setSupervisorResult(null)
      setShowSupervisor(false)
      return response
    } else {
      throw new Error('Retry failed')
    }
  }

  const handleContinueToNext = () => {
    // This will be handled by the parent component
    // For now, we'll just hide the supervisor section
    setShowSupervisor(false)
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

  const copyToNextAgent = (data: any, agentName: string, href: string) => {
    // Store in localStorage for the next agent
    localStorage.setItem(`agent_data_${agentName}`, JSON.stringify(data))
    // Navigate to the next agent page
    router.push(href)
  }

  const toggleSection = (section: string) => {
    setExpandedSections(prev => 
      prev.includes(section) 
        ? prev.filter(s => s !== section)
        : [...prev, section]
    )
  }

  const renderField = (field: any) => {
    const { name, label, type, required, placeholder, options, helpText } = field
    const mode = watch('mode')

    switch (type) {
      case 'textarea':
        return (
          <div>
            <textarea
              {...register(name, { required: required && `${label} is required` })}
              placeholder={placeholder}
              rows={4}
              className="w-full px-3 py-2 border border-gray-400 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 placeholder-gray-500"
            />
            {helpText && <p className="text-sm text-gray-500 mt-1">{helpText}</p>}
          </div>
        )
      
      case 'number':
        return (
          <div>
            <input
              {...register(name, { 
                required: required && `${label} is required`,
                valueAsNumber: true,
                setValueAs: (value) => {
                  if (value === '' || value === null || value === undefined) {
                    return undefined
                  }
                  const num = Number(value)
                  return isNaN(num) ? undefined : num
                }
              })}
              type="number"
              placeholder={placeholder}
              className="w-full px-3 py-2 border border-gray-400 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 placeholder-gray-500"
            />
            {helpText && <p className="text-sm text-gray-500 mt-1">{helpText}</p>}
          </div>
        )
      
      case 'select':
        return (
          <div>
            <select
              {...register(name, { required: required && `${label} is required` })}
              className="w-full px-3 py-2 border border-gray-400 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
            >
              {options?.map((option: any) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {helpText && <p className="text-sm text-gray-500 mt-1">{helpText}</p>}
          </div>
        )
      
      case 'chips': {
        const disabled = mode === 'auto'
        const selected: string[] = Array.isArray(watch(name)) ? watch(name) : []
        const open = !!dropdownOpen[name]
        const available = (options || []).filter((o: { value: string; label: string }) => !selected.includes(o.value))

        const addValue = (val: string) => {
          if (!val || selected.includes(val)) return
          const next = [...selected, val]
          setValue(name, next, { shouldDirty: true, shouldValidate: true })
        }
        const removeValue = (val: string) => {
          const next = selected.filter(v => v !== val)
          setValue(name, next, { shouldDirty: true, shouldValidate: true })
        }
        const toggleOpen = () => {
          if (disabled) return
          setDropdownOpen(prev => ({ ...prev, [name]: !prev[name] }))
        }
        return (
          <div className="relative">
            {/* Selected tags */}
            {selected.length > 0 && (
              <div className="mb-2 flex flex-wrap gap-2">
                {selected.map((val) => (
                  <span key={val} className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-800 border border-gray-300">
                    {options?.find((o: { value: string; label: string }) => o.value === val)?.label || val}
                    <button type="button" className="text-gray-500 hover:text-gray-700" onClick={() => removeValue(val)} disabled={disabled}>
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}

            {/* Toggle button */}
            <button
              type="button"
              onClick={toggleOpen}
              disabled={disabled}
              className={cn(
                "w-full flex items-center justify-between px-3 py-2 border border-gray-400 rounded-md bg-white",
                disabled ? "opacity-50 cursor-not-allowed" : "hover:border-gray-500"
              )}
            >
              <span className="text-gray-700">{open ? 'Select source…' : 'Add source'}</span>
              <span className="text-gray-500">{open ? '▴' : '▾'}</span>
            </button>

            {/* Dropdown menu */}
            {open && !disabled && (
              <div className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-md shadow">
                {available.length === 0 ? (
                  <div className="px-3 py-2 text-sm text-gray-500">No more sources</div>
                ) : (
                  <ul className="max-h-60 overflow-auto">
                    {available.map((opt: { value: string; label: string }) => (
                      <li key={opt.value}>
                        <button
                          type="button"
                          className="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm text-gray-800"
                          onClick={() => addValue(opt.value)}
                        >
                          {opt.label}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {/* Hidden field to ensure value presence if needed */}
            <input type="hidden" value={JSON.stringify(selected)} {...register(name)} />
            {disabled && <p className="text-xs text-gray-500 mt-1">Disabled in auto mode</p>}
            {helpText && <p className="text-sm text-gray-500 mt-1">{helpText}</p>}
          </div>
        )
      }

      case 'multiselect':
        return (
          <div>
            <select
              multiple
              className="w-full px-3 py-2 border border-gray-400 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
              onChange={(e) => {
                const selected = Array.from(e.currentTarget.selectedOptions).map(o => o.value)
                setValue(name, selected, { shouldValidate: true, shouldDirty: true })
              }}
            >
              {options?.map((option: any) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {helpText && <p className="text-sm text-gray-500 mt-1">{helpText}</p>}
          </div>
        )
      
      case 'json':
      case 'documents':
      case 'coded_units':
      case 'themes':
        return (
          <div>
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
              rows={8}
              className="w-full px-3 py-2 border border-gray-400 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 placeholder-gray-500 font-mono text-sm"
            />
            {helpText && <p className="text-sm text-gray-500 mt-1">{helpText}</p>}
          </div>
        )
      
      default:
        return (
          <div>
            <input
              {...register(name, { required: required && `${label} is required` })}
              type="text"
              placeholder={placeholder}
              className="w-full px-3 py-2 border border-gray-400 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 placeholder-gray-500"
            />
            {helpText && <p className="text-sm text-gray-500 mt-1">{helpText}</p>}
          </div>
        )
    }
  }

  const renderResultSection = (title: string, data: any, sectionKey: string) => {
    const isExpanded = expandedSections.includes(sectionKey)
    
    return (
      <div className="border border-gray-200 rounded-lg">
        <button
          onClick={() => toggleSection(sectionKey)}
          className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <span className="font-medium text-gray-900">{title}</span>
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-500" />
          )}
        </button>
        {isExpanded && (
          <div className="p-4">
            {typeof data === 'string' ? (
              <div className="bg-gray-50 rounded-md p-3">
                <pre className="text-sm text-gray-800 whitespace-pre-wrap overflow-auto max-h-96">{data}</pre>
              </div>
            ) : Array.isArray(data) ? (
              <div className="space-y-3">
                {data.map((item, index) => (
                  <div key={index} className="bg-gray-50 rounded-md p-3">
                    {typeof item === 'string' ? (
                      <div className="text-sm text-gray-800 whitespace-pre-wrap">{item}</div>
                    ) : (
                      <pre className="text-sm text-gray-800 overflow-auto max-h-96">{JSON.stringify(item, null, 2)}</pre>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-gray-50 rounded-md p-3">
                <pre className="text-sm text-gray-800 overflow-auto max-h-96">{JSON.stringify(data, null, 2)}</pre>
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  const renderRichResult = () => {
    if (!result?.data) return null

    const data = result.data

    return (
      <div className="space-y-4">
        {/* Success Header */}
        <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-green-800 font-medium">Completed Successfully</span>
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

        {/* Agent-specific result rendering */}
        {agentType === 'data-extractor' && data.documents && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Extracted Documents</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.documents.slice(0, 4).map((doc: any, index: number) => (
                <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">{doc.title}</h4>
                  <p className="text-sm text-gray-600 mb-2">{doc.authors}</p>
                  <p className="text-sm text-gray-500">{doc.year}</p>
                  <p className="text-xs text-gray-400 mt-2 line-clamp-3">{doc.content}</p>
                </div>
              ))}
            </div>
            {data.documents.length > 4 && (
              <p className="text-sm text-gray-500 text-center">
                +{data.documents.length - 4} more documents
              </p>
            )}
          </div>
        )}

        {agentType === 'multi-source-extractor' && (
          <div className="space-y-6">
            {/* Summary */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <button
                type="button"
                className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-left hover:border-gray-300"
                onClick={() => setCardPreview({ title: 'Total Found', content: String(data.total_found ?? (data.documents?.length || 0)) })}
              >
                <div className="text-xs text-gray-600">Total Found</div>
                <div className="text-lg font-semibold text-gray-900">{data.total_found ?? (data.documents?.length || 0)}</div>
              </button>
              <button
                type="button"
                className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-left hover:border-gray-300"
                onClick={() => setCardPreview({ title: 'Stored', content: String(data.stored ?? 0) })}
              >
                <div className="text-xs text-gray-600">Stored</div>
                <div className="text-lg font-semibold text-gray-900">{data.stored ?? 0}</div>
              </button>
              <button
                type="button"
                className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-left hover:border-gray-300"
                onClick={() => setCardPreview({ title: 'Collection', content: String(data.collection_name || '—') })}
              >
                <div className="text-xs text-gray-600">Collection</div>
                <div className="text-sm font-medium text-gray-900 truncate">{data.collection_name || '—'}</div>
              </button>
              <button
                type="button"
                className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-left hover:border-gray-300"
                onClick={() => setCardPreview({ title: 'Research Domain', content: String(data.research_domain || '—') })}
              >
                <div className="text-xs text-gray-600">Domain</div>
                <div className="text-sm font-medium text-gray-900 truncate">{data.research_domain || '—'}</div>
              </button>
            </div>
            {cardPreview && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
                <div className="w-full max-w-md bg-white rounded-lg shadow-lg border border-gray-200">
                  <div className="flex items-center justify-between px-4 py-3 border-b">
                    <h4 className="text-base font-semibold text-gray-900">{cardPreview.title}</h4>
                    <button className="p-1 text-gray-600 hover:text-gray-900" onClick={() => setCardPreview(null)} aria-label="Close">
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="px-4 py-3 text-sm text-gray-800 break-words whitespace-pre-wrap">
                    {cardPreview.content}
                  </div>
                </div>
              </div>
            )}

            {/* Source Stats */}
            {Array.isArray(data.source_stats) && data.source_stats.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Source Stats</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {data.source_stats.map((s: any, i: number) => (
                    <div key={i} className="border border-gray-200 rounded-lg p-3 bg-white">
                      <div className="flex items-center justify-between">
                        <div className="text-sm font-medium text-gray-900">{s.name}</div>
                        <div className="text-xs text-gray-500">{s.errors || 0} errors</div>
                      </div>
                      <div className="text-sm text-gray-700 mt-1">Fetched: <span className="font-medium">{s.fetched || 0}</span></div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Enrichment Stats */}
            {Array.isArray(data.enrichment_stats) && data.enrichment_stats.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Enrichment Stats</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {data.enrichment_stats.map((s: any, i: number) => (
                    <div key={i} className="border border-gray-200 rounded-lg p-3 bg-white">
                      <div className="flex items-center justify-between">
                        <div className="text-sm font-medium text-gray-900">{s.name}</div>
                        <div className="text-xs text-gray-500">{s.errors || 0} errors</div>
                      </div>
                      <div className="text-sm text-gray-700 mt-1">Processed: <span className="font-medium">{s.fetched || 0}</span></div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Documents */}
            {Array.isArray(data.documents) && data.documents.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Documents</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {data.documents.slice(0, 6).map((doc: any, index: number) => (
                    <div
                      key={index}
                      className="bg-white border border-gray-200 rounded-lg p-4 cursor-pointer hover:shadow"
                      onClick={() => setDocPreview(doc)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') setDocPreview(doc) }}
                    >
                      <h4 className="font-medium text-gray-900 mb-1 truncate" title={doc.title}>{doc.title || 'Untitled'}</h4>
                      <div className="text-xs text-gray-600 mb-2 flex gap-2">
                        <span>{doc.year || '—'}</span>
                        <span className="text-gray-400">•</span>
                        <span className="truncate" title={doc.source}>{doc.source || '—'}</span>
                      </div>
                      {doc.authors && (
                        <div className="text-xs text-gray-500 mb-2 truncate" title={doc.authors}>{doc.authors}</div>
                      )}
                      {doc.doi && (
                        <div className="text-xs text-gray-500 mb-2 truncate" title={doc.doi}>DOI: {doc.doi}</div>
                      )}
                      <p className="text-xs text-gray-700 line-clamp-4">{doc.abstract || doc.content || ''}</p>
                    </div>
                  ))}
                </div>
                {data.documents.length > 6 && (
                  <p className="text-sm text-gray-500 text-center mt-2">+{data.documents.length - 6} more documents</p>
                )}
              </div>
            )}

            {/* Document Preview Modal */}
            {docPreview && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
                <div className="w-full max-w-3xl bg-white rounded-lg shadow-lg border border-gray-200">
                  <div className="flex items-center justify-between px-4 py-3 border-b">
                    <h4 className="text-base font-semibold text-gray-900 truncate" title={docPreview.title}>{docPreview.title || 'Untitled'}</h4>
                    <button
                      className="p-1 text-gray-600 hover:text-gray-900"
                      onClick={() => setDocPreview(null)}
                      aria-label="Close preview"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="px-4 py-3 space-y-2 text-sm">
                    <div className="flex flex-wrap items-center gap-2 text-gray-600">
                      {docPreview.year && <span>{docPreview.year}</span>}
                      {docPreview.source && <span className="text-gray-400">•</span>}
                      {docPreview.source && <span>{docPreview.source}</span>}
                      {docPreview.doi && (
                        <>
                          <span className="text-gray-400">•</span>
                          <span className="truncate" title={docPreview.doi}>DOI: {docPreview.doi}</span>
                        </>
                      )}
                    </div>
                    {docPreview.authors && (
                      <div className="text-xs text-gray-500">{docPreview.authors}</div>
                    )}
                    <div className="mt-2 max-h-[70vh] overflow-y-auto">
                      <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                        {docPreview.abstract || docPreview.content || 'No preview available'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {agentType === 'literature-review' && (
          <div className="space-y-4">
            {data.summary && renderResultSection('Summary', data.summary, 'summary')}
            {data.key_findings && renderResultSection('Key Findings', data.key_findings, 'findings')}
            {data.research_gaps && renderResultSection('Research Gaps', data.research_gaps, 'gaps')}
            {data.full_literature_review && renderResultSection('Full Literature Review', data.full_literature_review, 'full-review')}
          </div>
        )}

        {agentType === 'initial-coding' && data.coded_units && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Coded Units</h3>
            <div className="space-y-3">
              {data.coded_units.slice(0, 5).map((unit: any, index: number) => (
                <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900">Unit {index + 1}</span>
                    <span className="text-xs text-gray-500">Confidence: {unit.confidence?.toFixed(2) || 'N/A'}</span>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{unit.content}</p>
                  <div className="space-y-2">
                    <div className="flex flex-wrap gap-1">
                      {unit.codes?.map((code: any, codeIndex: number) => (
                        <span key={codeIndex} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                          {typeof code === 'string' ? code : code.name || 'Unknown Code'}
                        </span>
                      ))}
                    </div>
                    {unit.codes?.some((code: any) => typeof code === 'object' && code.definition) && (
                      <div className="text-xs text-gray-600 space-y-1">
                        {unit.codes?.map((code: any, codeIndex: number) => 
                          typeof code === 'object' && code.definition ? (
                            <div key={codeIndex} className="ml-2">
                              <strong>{code.name}:</strong> {code.definition}
                              {code.confidence && (
                                <span className="ml-1 text-gray-500">({(code.confidence * 100).toFixed(0)}%)</span>
                              )}
                            </div>
                          ) : null
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
            {data.coded_units.length > 5 && (
              <p className="text-sm text-gray-500 text-center">
                +{data.coded_units.length - 5} more units
              </p>
            )}
          </div>
        )}

        {agentType === 'thematic-grouping' && data.themes && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Generated Themes</h3>
            
            {/* Thematic Summary */}
            {data.thematic_summary && (
              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-4">
                <h4 className="text-sm font-medium text-indigo-900 mb-3">Thematic Summary</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                  <div>
                    <span className="text-indigo-700 font-medium">Total Themes:</span>
                    <div className="text-indigo-900">{data.thematic_summary.total_themes_generated}</div>
                  </div>
                  <div>
                    <span className="text-indigo-700 font-medium">Codes Analyzed:</span>
                    <div className="text-indigo-900">{data.thematic_summary.total_codes_analyzed}</div>
                  </div>
                  <div>
                    <span className="text-indigo-700 font-medium">Unique Codes:</span>
                    <div className="text-indigo-900">{data.thematic_summary.unique_codes_clustered}</div>
                  </div>
                  <div>
                    <span className="text-indigo-700 font-medium">Avg Codes/Theme:</span>
                    <div className="text-indigo-900">{data.thematic_summary.average_codes_per_theme}</div>
                  </div>
                </div>
                
                {/* Theme Sizes */}
                {data.thematic_summary.theme_sizes && (
                  <div className="mt-3">
                    <h5 className="text-xs font-medium text-indigo-700 mb-2">Theme Sizes</h5>
                    <div className="space-y-1">
                      {Object.entries(data.thematic_summary.theme_sizes).map(([themeName, size]: [string, any]) => (
                        <div key={themeName} className="flex justify-between text-xs">
                          <span className="text-indigo-800 truncate">{themeName}</span>
                          <span className="text-indigo-600 font-medium">{size} codes</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Individual Themes */}
            <div className="space-y-4">
              {data.themes.slice(0, 5).map((theme: any, index: number) => (
                <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                  {/* Theme Header */}
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-lg font-semibold text-gray-900">{theme.theme_name}</h4>
                    <span className="text-xs bg-indigo-100 text-indigo-800 px-2 py-1 rounded font-medium">
                      {theme.codes?.length || 0} codes
                    </span>
                  </div>

                  {/* Theme Description */}
                  {theme.description && (
                    <div className="mb-3">
                      <p className="text-sm text-gray-700">{theme.description}</p>
                    </div>
                  )}

                  {/* Codes Section */}
                  {theme.codes && theme.codes.length > 0 && (
                    <div className="mb-4">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Codes ({theme.codes.length})</h5>
                      <div className="space-y-2">
                        {theme.codes.map((code: any, codeIndex: number) => (
                          <div key={codeIndex} className="bg-gray-50 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm font-medium text-gray-900">{code.name}</span>
                              <div className="flex items-center space-x-2">
                                <span className={`text-xs px-2 py-1 rounded ${
                                  code.category === 'primary' 
                                    ? 'bg-blue-100 text-blue-800' 
                                    : 'bg-green-100 text-green-800'
                                }`}>
                                  {code.category}
                                </span>
                                <span className="text-xs text-gray-500">
                                  {(code.confidence * 100).toFixed(0)}%
                                </span>
                              </div>
                            </div>
                            {code.definition && (
                              <p className="text-xs text-gray-600 mt-1">{code.definition}</p>
                            )}
                            {code.frequency && (
                              <span className="text-xs text_gray-500">Frequency: {code.frequency}</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Illustrative Quotes */}
                  {theme.illustrative_quotes && theme.illustrative_quotes.length > 0 && (
                    <div className="mb-4">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Illustrative Quotes</h5>
                      <div className="space-y-2">
                        {theme.illustrative_quotes.map((quote: string, quoteIndex: number) => (
                          <div key={quoteIndex} className="bg-blue-50 border-l-4 border-blue-200 p-3">
                            <p className="text-sm text-gray-700 italic">"{quote}"</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Cross-cutting Ideas */}
                  {theme.cross_cutting_ideas && theme.cross_cutting_ideas.length > 0 && (
                    <div className="mb-4">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Cross-cutting Ideas</h5>
                      <div className="space-y-1">
                        {theme.cross_cutting_ideas.map((idea: string, ideaIndex: number) => (
                          <div key={ideaIndex} className="text-sm text-gray-600">
                            • {idea}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Academic Reasoning */}
                  {theme.academic_reasoning && (
                    <div className="mb-3">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Academic Reasoning</h5>
                      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
                        <p className="text-sm text-gray-700">{theme.academic_reasoning}</p>
                      </div>
                    </div>
                  )}

                  {/* Justification */}
                  {theme.justification && (
                    <div className="mb-3">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Justification</h5>
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                        <p className="text-sm text-gray-700">{theme.justification}</p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            {data.themes.length > 5 && (
              <p className="text-sm text-gray-500 text-center">
                +{data.themes.length - 5} more themes
              </p>
            )}

            {/* Additional Info */}
            {data.coded_units_analyzed && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                <div className="flex items-center justify_between text-sm">
                  <span className="text-gray-700">Coded Units Analyzed:</span>
                  <span className="font-medium text-gray-900">{data.coded_units_analyzed}</span>
                </div>
                {data.research_domain && (
                  <div className="flex items-center justify_between text-sm mt-1">
                    <span className="text-gray-700">Research Domain:</span>
                    <span className="font-medium text-gray-900">{data.research_domain}</span>
                  </div>
                )}
                {data.generated_at && (
                  <div className="flex items-center justify_between text-sm mt-1">
                    <span className="text-gray-700">Generated:</span>
                    <span className="font-medium text-gray-900">{new Date(data.generated_at).toLocaleString()}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {agentType === 'theme-refiner' && data.refined_themes && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Refined Themes</h3>
            
            {/* Refinement Summary */}
            {data.refinement_summary && (
              <div className="bg-pink-50 border border-pink-200 rounded-lg p-4 mb-4">
                <h4 className="text-sm font-medium text-pink-900 mb-3">Refinement Summary</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                  <div>
                    <span className="text-pink-700 font-medium">Themes Refined:</span>
                    <div className="text-pink-900">{data.refinement_summary.total_themes_refined}</div>
                  </div>
                  <div>
                    <span className="text-pink-700 font-medium">Academic Quotes:</span>
                    <div className="text-pink-900">{data.refinement_summary.total_academic_quotes}</div>
                  </div>
                  <div>
                    <span className="text-pink-700 font-medium">Key Concepts:</span>
                    <div className="text-pink-900">{data.refinement_summary.total_key_concepts}</div>
                  </div>
                  <div>
                    <span className="text-pink-700 font-medium">Avg Quotes/Theme:</span>
                    <div className="text-pink-900">{data.refinement_summary.average_quotes_per_theme}</div>
                  </div>
                </div>
                
                {/* Additional Summary Info */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-3 text-xs">
                  <div>
                    <span className="text-pink-700 font-medium">Avg Concepts/Theme:</span>
                    <div className="text-pink-900">{data.refinement_summary.average_concepts_per_theme}</div>
                  </div>
                  <div>
                    <span className="text-pink-700 font-medium">With Framework:</span>
                    <div className="text-pink-900">{data.refinement_summary.themes_with_framework}</div>
                  </div>
                  <div>
                    <span className="text-pink-700 font-medium">With Implications:</span>
                    <div className="text-pink-900">{data.refinement_summary.themes_with_implications}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Individual Refined Themes */}
            <div className="space-y-4">
              {data.refined_themes.slice(0, 5).map((theme: any, index: number) => (
                <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                  {/* Theme Header */}
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900">{theme.refined_name}</h4>
                      {theme.original_name && theme.original_name !== theme.refined_name && (
                        <p className="text-sm text-gray-500">Originally: {theme.original_name}</p>
                      )}
                    </div>
                    <span className="text-xs bg-pink-100 text-pink-800 px-2 py-1 rounded font-medium">Refined</span>
                  </div>

                  {/* Precise Definition */}
                  {theme.precise_definition && (
                    <div className="mb-4">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Precise Definition</h5>
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <p className="text_sm text-gray-700">{theme.precise_definition}</p>
                      </div>
                    </div>
                  )}

                  {/* Scope Boundaries */}
                  {theme.scope_boundaries && (
                    <div className="mb-4">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Scope Boundaries</h5>
                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <p className="text_sm text-gray-700">{theme.scope_boundaries}</p>
                      </div>
                    </div>
                  )}

                  {/* Academic Quotes */}
                  {theme.academic_quotes && theme.academic_quotes.length > 0 && (
                    <div className="mb-4">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Academic Quotes ({theme.academic_quotes.length})</h5>
                      <div className="space-y-3">
                        {theme.academic_quotes.map((quoteObj: any, quoteIndex: number) => (
                          <div key={quoteIndex} className="bg-blue-50 border-l-4 border-blue-200 p-3">
                            <p className="text-sm text-gray-700 italic mb-2">"{quoteObj.quote}"</p>
                            {quoteObj.citation && (
                              <p className="text-xs text-blue-600 font-medium">— {quoteObj.citation}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Key Concepts */}
                  {theme.key_concepts && theme.key_concepts.length > 0 && (
                    <div className="mb-4">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Key Concepts ({theme.key_concepts.length})</h5>
                      <div className="space-y-1">
                        {theme.key_concepts.map((concept: string, conceptIndex: number) => (
                          <div key={conceptIndex} className="text-sm text-gray-600">
                            • {concept}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Theoretical Framework */}
                  {theme.theoretical_framework && (
                    <div className="mb-4">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Theoretical Framework</h5>
                      <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                        <p className="text-sm text-gray-700">{theme.theoretical_framework}</p>
                      </div>
                    </div>
                  )}

                  {/* Research Implications */}
                  {theme.research_implications && (
                    <div className="mb-3">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Research Implications</h5>
                      <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                        <p className="text-sm text_gray-700">{theme.research_implications}</p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            {data.refined_themes.length > 5 && (
              <p className="text-sm text-gray-500 text-center">
                +{data.refined_themes.length - 5} more refined themes
              </p>
            )}

            {/* Additional Info */}
            {data.themes_refined && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                <div className="flex items-center justify_between text-sm">
                  <span className="text-gray-700">Themes Refined:</span>
                  <span className="font-medium text-gray-900">{data.themes_refined}</span>
                </div>
                {data.research_domain && (
                  <div className="flex items-center justify_between text-sm mt-1">
                    <span className="text-gray-700">Research Domain:</span>
                    <span className="font-medium text-gray-900">{data.research_domain}</span>
                  </div>
                )}
                {data.generated_at && (
                  <div className="flex items_center justify_between text-sm mt-1">
                    <span className="text-gray-700">Generated:</span>
                    <span className="font-medium text-gray-900">{new Date(data.generated_at).toLocaleString()}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {agentType === 'report-generator' && data.report_content && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Generated Report</h3>
            
            {/* Report Summary */}
            {data.report_summary && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <h4 className="text-sm font-medium text-blue-900 mb-2">Report Summary</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                  <div>
                    <span className="text-blue-700 font-medium">Word Count:</span>
                    <div className="text-blue-900">{data.report_summary.word_count}</div>
                  </div>
                  <div>
                    <span className="text-blue-700 font-medium">Report Length:</span>
                    <div className="text-blue-900">{data.report_summary.report_length} chars</div>
                  </div>
                  <div>
                    <span className="text-blue-700 font-medium">References:</span>
                    <div className="text-blue-900">{data.report_summary.total_references}</div>
                  </div>
                  <div>
                    <span className="text-blue-700 font-medium">Generated:</span>
                    <div className="text-blue-900">{new Date(data.report_summary.generated_at).toLocaleString()}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Report Content */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-medium text-gray-900">Report Content</h4>
                <button
                  onClick={() => copyToClipboard(data.report_content)}
                  className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
                  title="Copy report content"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
              <div className="max_h-96 overflow-y-auto">
                <div className="prose prose-sm max-w-none">
                  <div className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed">
                    {data.report_content}
                  </div>
                </div>
              </div>
            </div>

            {/* References */}
            {data.references && data.references.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-900 mb-3">References</h4>
                <div className="space-y-2">
                  {data.references.map((ref: any, index: number) => (
                    <div key={index} className="text-sm text-gray-700 p-2 bg-gray-50 rounded">
                      <div className="font-medium">{ref.author} ({ref.year})</div>
                      <div className="text-gray-600">{ref.title}</div>
                      <div className="text-xs text-gray-500">{ref.source}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* File Information */}
            {data.file_path && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4 text-green-600" />
                  <div>
                    <div className="text-sm font-medium text-green-800">Report Saved</div>
                    <div className="text-xs text-green-700">{data.file_path}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Next Agent Suggestions */}
        {nextAgents.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">Continue with Next Agent</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {nextAgents.map((agent) => (
                <div key={agent.name} className="bg-white border border-blue-200 rounded-lg p-3">
                  <div className="flex items-center space-x-3">
                    <div className="text-xl">{agent.icon}</div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{agent.name}</h4>
                      <p className="text-sm text-gray-600">{agent.description}</p>
                    </div>
                    <button
                      onClick={() => copyToNextAgent(result.data, agent.name.toLowerCase().replace(' ', '-'), agent.href)}
                      className="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-md transition-colors"
                      title="Copy data for next agent"
                    >
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Raw JSON (collapsible) */}
        <div className="border border-gray-200 rounded-lg">
          <button
            onClick={() => toggleSection('raw-json')}
            className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            <span className="font-medium text-gray-900">Raw JSON Response</span>
            {expandedSections.includes('raw-json') ? (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-500" />
            )}
          </button>
          {expandedSections.includes('raw-json') && (
            <div className="p-4">
              <pre className="text-sm text-gray-800 overflow-auto max-h-96 bg-gray-50 rounded-md p-3">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    )
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
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuration</h2>
          
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
                {isLoading ? 'Processing...' : 'Process'}
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
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Results</h2>
          
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
                <p className="text-gray-600">Agent is processing...</p>
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
              {/* Supervisor Check Button */}
              {onSupervisorCheck && !showSupervisor && (
                <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Shield className="w-5 h-5 text-blue-600" />
                      <div>
                        <h3 className="font-medium text-blue-900">Quality Assurance</h3>
                        <p className="text-sm text-blue-700">Review this output with the Supervisor Agent</p>
                      </div>
                    </div>
                    <button
                      onClick={handleSupervisorCheck}
                      disabled={isSupervisorLoading}
                      className={cn(
                        "inline-flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors",
                        isSupervisorLoading
                          ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                          : "bg-blue-600 text-white hover:bg-blue-700"
                      )}
                    >
                      {isSupervisorLoading ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Eye className="w-4 h-4 mr-2" />
                      )}
                      {isSupervisorLoading ? 'Checking...' : 'Review with Supervisor'}
                    </button>
                  </div>
                </div>
              )}

              {/* Supervisor Results */}
              {showSupervisor && supervisorResult && (
                <SupervisorSection
                  supervisorResult={supervisorResult}
                  agentType={agentType}
                  originalInput={result.data}
                  onRetry={handleRetryAgent}
                  onContinue={handleContinueToNext}
                />
              )}

              {/* Agent Results */}
              {!showSupervisor && renderRichResult()}
            </div>
          )}

          {!isLoading && !error && !result && (
            <div className="text-center py-8 text-gray-500">
              <p>Run a process to see results here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 