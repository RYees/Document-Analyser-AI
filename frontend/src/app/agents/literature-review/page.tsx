'use client'

import { useState, useEffect } from 'react'
import { EnhancedAgentForm } from '@/components/agents/enhanced-agent-form'
import { testLiteratureReview, checkQuality, retryAgent } from '@/lib/api'
import { AGENT_TYPES } from '@/lib/utils'
import type { LiteratureReviewRequest, SupervisorRequest, RetryAgentRequest } from '@/types/api'

export default function LiteratureReviewPage() {
  const agent = AGENT_TYPES.literatureReview

  // Try to load data from previous agent (retriever)
  const getDefaultValues = () => {
    try {
      const retrieverData = localStorage.getItem('agent_data_retriever')
      if (retrieverData) {
        const parsed = JSON.parse(retrieverData)
        // If we have documents from retriever, use them
        if (parsed.documents && Array.isArray(parsed.documents)) {
          return {
            research_domain: parsed.research_domain || '',
            documents: JSON.stringify(parsed.documents, null, 2)
          }
        }
      }
    } catch (error) {
      console.log('No previous agent data found')
    }
    
    // Return empty values when no previous data exists
    return {
      research_domain: '',
      documents: ''
    }
  }

  const fields = [
    {
      name: 'research_domain',
      label: 'Research Domain',
      type: 'text' as const,
      required: true,
      placeholder: 'Enter research domain (e.g., "Blockchain Technology")',
      helpText: 'The specific research area for context'
    },
    {
      name: 'review_type',
      label: 'Review Type',
      type: 'select' as const,
      required: false,
      options: [
        { value: 'thematic', label: 'Thematic Review' },
        { value: 'systematic', label: 'Systematic Review' },
        { value: 'narrative', label: 'Narrative Review' }
      ],
      helpText: 'Type of literature review to generate'
    },
    {
      name: 'documents',
      label: 'Documents (JSON)',
      type: 'documents' as const,
      required: true,
      placeholder: `[
  {
    "title": "Document Title",
    "authors": "Author Name",
    "content": "Document content...",
    "year": 2024,
    "doi": "10.1234/example",
    "research_domain": "Blockchain Technology"
  }
]`,
      helpText: 'JSON array of documents to review. Each document should have title, content, and metadata.'
    }
  ]

  const nextAgents = [
    {
      name: 'Initial Coding',
      href: '/agents/initial-coding',
      description: 'Perform coding analysis on documents',
      icon: '🎯'
    }
  ]

  const defaultValues = getDefaultValues()
  const [hasPreviousData, setHasPreviousData] = useState(false)

  // Check for previous data on client side
  useEffect(() => {
    const previousData = localStorage.getItem('agent_data_literature-review')
    setHasPreviousData(previousData !== null)
  }, [])

  const handleSubmit = async (data: LiteratureReviewRequest) => {
    // Parse JSON documents if they're provided as a string
    if (typeof data.documents === 'string') {
      data.documents = JSON.parse(data.documents)
    }
    
    const result = await testLiteratureReview(data)
    
    // Store the result for the next agent (Initial Coding)
    if (result.success && result.data) {
      console.log('📚 [LITERATURE REVIEW] Processing result for next agent...')
      console.log('📚 [LITERATURE REVIEW] Current form documents count:', data.documents.length)
      
      // Always store literature review data for Initial Coding
      const dataToStore = {
        documents: data.documents,
        research_domain: data.research_domain,
        review_type: data.review_type,
        literature_review_output: result.data
      }
      
      console.log('📚 [LITERATURE REVIEW] Storing data for Initial Coding:', dataToStore)
      localStorage.setItem('agent_data_literature-review', JSON.stringify(dataToStore))
      console.log('📚 [LITERATURE REVIEW] Data stored successfully for Initial Coding')
    }
    
    return result
  }

  const handleSupervisorCheck = async (data: SupervisorRequest) => {
    return await checkQuality(data)
  }

  const handleRetryAgent = async (data: RetryAgentRequest) => {
    return await retryAgent(data)
  }

  return (
    <div>
      {hasPreviousData && (
        <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <div className="text-green-600">✅</div>
            <div>
              <h3 className="text-sm font-medium text-green-800">Data Loaded from Previous Agent</h3>
              <p className="text-sm text-green-700">Documents from the Retriever agent have been automatically loaded.</p>
            </div>
          </div>
        </div>
      )}
      <EnhancedAgentForm
        agentType="literature-review"
        agentName={agent.name}
        description={agent.description}
        icon={agent.icon}
        color={agent.color}
        onSubmit={handleSubmit}
        onSupervisorCheck={handleSupervisorCheck}
        onRetryAgent={handleRetryAgent}
        defaultValues={defaultValues}
        fields={fields}
        nextAgents={nextAgents}
      />
    </div>
  )
} 