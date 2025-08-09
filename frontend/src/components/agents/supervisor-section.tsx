'use client'

import { useState } from 'react'
import { 
  CheckCircle, 
  AlertCircle, 
  RefreshCw, 
  Eye, 
  EyeOff,
  ChevronDown,
  ChevronRight,
  Star,
  Target,
  TrendingUp,
  FileText,
  Lightbulb,
  ArrowRight
} from 'lucide-react'
import { cn } from '@/lib/utils'
import type { SupervisorResult, RetryAgentRequest } from '@/types/api'

interface SupervisorSectionProps {
  supervisorResult: SupervisorResult
  agentType: string
  originalInput: any
  onRetry: (data: RetryAgentRequest) => Promise<any>
  onContinue: () => void
}

export function SupervisorSection({
  supervisorResult,
  agentType,
  originalInput,
  onRetry,
  onContinue
}: SupervisorSectionProps) {
  const [isRetrying, setIsRetrying] = useState(false)
  const [userContext, setUserContext] = useState('')
  const [expandedSections, setExpandedSections] = useState<string[]>(['assessment'])
  const [retryResult, setRetryResult] = useState<any>(null)

  const assessment = supervisorResult.initial_assessment
  const isApproved = assessment.status === 'APPROVED'
  const needsRetry = assessment.status === 'REVISE'
  const isHalted = assessment.status === 'HALT'

  const toggleSection = (section: string) => {
    setExpandedSections(prev => 
      prev.includes(section) 
        ? prev.filter(s => s !== section)
        : [...prev, section]
    )
  }

  const handleRetry = async () => {
    if (!assessment.enhanced_context_prompt) {
      alert('No enhanced context available for retry')
      return
    }

    setIsRetrying(true)
    try {
      const retryData: RetryAgentRequest = {
        agent_type: agentType,
        original_agent_input: originalInput,
        enhanced_context: assessment.enhanced_context_prompt,
        user_context: userContext || undefined
      }
      
      const result = await onRetry(retryData)
      setRetryResult(result)
    } catch (error) {
      console.error('Retry failed:', error)
      alert('Retry failed. Please try again.')
    } finally {
      setIsRetrying(false)
    }
  }

  const getStatusIcon = () => {
    if (isApproved) return <CheckCircle className="w-5 h-5 text-green-600" />
    if (needsRetry) return <RefreshCw className="w-5 h-5 text-yellow-600" />
    if (isHalted) return <AlertCircle className="w-5 h-5 text-red-600" />
    return <AlertCircle className="w-5 h-5 text-gray-600" />
  }

  const getStatusColor = () => {
    if (isApproved) return 'text-green-600 bg-green-50 border-green-200'
    if (needsRetry) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    if (isHalted) return 'text-red-600 bg-red-50 border-red-200'
    return 'text-gray-600 bg-gray-50 border-gray-200'
  }

  const getStatusText = () => {
    if (isApproved) return 'Quality Approved'
    if (needsRetry) return 'Needs Improvement'
    if (isHalted) return 'Quality Issues - Halted'
    return 'Under Review'
  }

  return (
    <div className="space-y-4">
      {/* Supervisor Header */}
      <div className={cn(
        "border rounded-lg p-4",
        getStatusColor()
      )}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getStatusIcon()}
            <div>
              <h3 className="font-semibold">Supervisor Quality Assessment</h3>
              <p className="text-sm opacity-80">{getStatusText()}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-1">
              <Star className="w-4 h-4 text-yellow-500" />
              <span className="font-medium">{assessment.quality_score.toFixed(1)}/10</span>
            </div>
            <p className="text-xs opacity-70">Quality Score</p>
          </div>
        </div>
      </div>

      {/* Assessment Details */}
      <div className="border border-gray-200 rounded-lg">
        <button
          onClick={() => toggleSection('assessment')}
          className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <span className="font-medium text-gray-900">Assessment Details</span>
          {expandedSections.includes('assessment') ? (
            <ChevronDown className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-500" />
          )}
        </button>
        
        {expandedSections.includes('assessment') && (
          <div className="p-4 space-y-4">
            {/* Quality Score */}
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <Star className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <div className="font-bold text-2xl text-blue-900">{assessment.quality_score.toFixed(1)}/10</div>
              <div className="text-sm text-blue-700">Overall Quality Score</div>
              <div className="text-xs text-blue-600 mt-1">Confidence: {(assessment.confidence * 100).toFixed(0)}%</div>
            </div>

            {/* Issues Found */}
            {assessment.issues_found.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Issues Found:</h4>
                <ul className="space-y-1">
                  {assessment.issues_found.map((issue, index) => (
                    <li key={index} className="flex items-start space-x-2 text-sm text-red-700">
                      <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>{issue}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Improvement Suggestions */}
            {assessment.improvement_suggestions.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Improvement Suggestions:</h4>
                <ul className="space-y-1">
                  {assessment.improvement_suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start space-x-2 text-sm text-blue-700">
                      <Lightbulb className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Assessment Reasoning */}
            {assessment.assessment_reasoning && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Assessment Reasoning:</h4>
                <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                  {assessment.assessment_reasoning}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center space-x-3">
        {isApproved && (
          <button
            onClick={onContinue}
            className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          >
            <ArrowRight className="w-4 h-4 mr-2" />
            Continue to Next Agent
          </button>
        )}

        {needsRetry && (
          <>
            <button
              onClick={handleRetry}
              disabled={isRetrying || !assessment.enhanced_context_prompt}
              className={cn(
                "inline-flex items-center px-4 py-2 rounded-md transition-colors",
                isRetrying || !assessment.enhanced_context_prompt
                  ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                  : "bg-yellow-600 text-white hover:bg-yellow-700"
              )}
            >
              <RefreshCw className={cn("w-4 h-4 mr-2", isRetrying && "animate-spin")} />
              {isRetrying ? 'Retrying...' : 'Retry with Enhanced Context'}
            </button>

            <button
              onClick={onContinue}
              className="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              <ArrowRight className="w-4 h-4 mr-2" />
              Continue Anyway
            </button>
          </>
        )}

        {isHalted && (
          <div className="text-red-600 font-medium">
            This agent output has been halted due to quality issues. Please review and try again.
          </div>
        )}
      </div>

      {/* User Context Input for Retry */}
      {needsRetry && (
        <div className="border border-gray-200 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-2">Additional Context (Optional):</h4>
          <textarea
            value={userContext}
            onChange={(e) => setUserContext(e.target.value)}
            placeholder="Provide additional context or specific requirements for the retry..."
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
            rows={3}
          />
          <p className="text-sm text-gray-600 mt-1">
            This will be combined with the supervisor's enhanced context for the retry.
          </p>
        </div>
      )}

      {/* Retry Results */}
      {retryResult && (
        <div className="border border-green-200 rounded-lg p-4 bg-green-50">
          <div className="flex items-center space-x-2 mb-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <h4 className="font-medium text-green-900">Retry Completed Successfully</h4>
          </div>
          <p className="text-sm text-green-700 mb-3">
            The agent has been retried with enhanced context. Review the new results below.
          </p>
          <button
            onClick={() => setRetryResult(null)}
            className="text-sm text-green-600 hover:text-green-700 underline"
          >
            View New Results
          </button>
        </div>
      )}
    </div>
  )
} 