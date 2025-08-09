'use client'

import { useState, useEffect } from 'react'
import { EnhancedAgentForm } from '@/components/agents/enhanced-agent-form'
import { testInitialCoding, checkQuality, retryAgent } from '@/lib/api'
import { AGENT_TYPES } from '@/lib/utils'
import type { InitialCodingRequest, RetryAgentRequest } from '@/types/api'

export default function InitialCodingPage() {
  const agent = AGENT_TYPES.initialCoding

  // Try to load data from previous agents (literature-review or retriever)
  const getDefaultValues = () => {
    try {
      console.log('🎯 [INITIAL CODING] Attempting to load data from localStorage...')
      
      // First try to get data from Literature Review
      let data = localStorage.getItem('agent_data_literature-review')
      let source = 'Literature Review'
      
      // If no Literature Review data, try Retriever data
      if (!data) {
        data = localStorage.getItem('agent_data_retriever')
        source = 'Retriever'
      }
      
      console.log('🎯 [INITIAL CODING] Raw localStorage data:', data)
      console.log('🎯 [INITIAL CODING] Data source:', source)
      
      if (data) {
        const parsed = JSON.parse(data)
        console.log('🎯 [INITIAL CODING] Parsed data:', parsed)
        console.log('🎯 [INITIAL CODING] Has documents?', !!parsed.documents)
        console.log('🎯 [INITIAL CODING] Documents is array?', Array.isArray(parsed.documents))
        
        // If we have documents, use them
        if (parsed.documents && Array.isArray(parsed.documents)) {
          console.log('🎯 [INITIAL CODING] Loaded documents from previous agent:', parsed.documents.length, 'documents')
          console.log('🎯 [INITIAL CODING] Source:', source)
          console.log('🎯 [INITIAL CODING] First document sample:', parsed.documents[0])
          return {
            research_domain: parsed.research_domain || '',
            documents: JSON.stringify(parsed.documents, null, 2)
          }
        } else {
          console.log('🎯 [INITIAL CODING] No valid documents found in parsed data')
        }
      } else {
        console.log('🎯 [INITIAL CODING] No data found in localStorage for any previous agent')
      }
    } catch (error) {
      console.log('🎯 [INITIAL CODING] Error loading previous agent data:', error)
    }
    
    // Return empty values when no previous data exists
    console.log('🎯 [INITIAL CODING] Returning empty default values')
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
      name: 'coding_approach',
      label: 'Coding Approach',
      type: 'select' as const,
      required: false,
      options: [
        { value: 'open_coding', label: 'Open Coding' },
        { value: 'axial_coding', label: 'Axial Coding' },
        { value: 'selective_coding', label: 'Selective Coding' }
      ],
      helpText: 'The coding methodology to use'
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
      helpText: 'JSON array of documents to code. Each document should have title, content, and metadata.'
    }
  ]

  const nextAgents = [
    {
      name: 'Thematic Grouping',
      href: '/agents/thematic-grouping',
      description: 'Group coded units into themes',
      icon: '🔗'
    }
  ]

  const defaultValues = getDefaultValues()
  const [hasPreviousData, setHasPreviousData] = useState(false)

  // Check for previous data on client side
  useEffect(() => {
    const previousData = localStorage.getItem('agent_data_initial-coding')
    setHasPreviousData(previousData !== null)
  }, [])

  const handleSubmit = async (data: InitialCodingRequest) => {
    // Parse JSON documents if they're provided as a string
    if (typeof data.documents === 'string') {
      data.documents = JSON.parse(data.documents)
    }
    
    const result = await testInitialCoding(data)
    
    // Store the result for the next agent (Thematic Grouping)
    if (result.success && result.data) {
      localStorage.setItem('agent_data_thematic-grouping', JSON.stringify({
        coded_units: result.data.coded_units,
        research_domain: data.research_domain,
        coding_approach: data.coding_approach
      }))
    }
    
    return result
  }

  const handleSupervisorCheck = async (data: any) => {
    console.log('🔍 Initial Coding supervisor check called with:', data)
    return await checkQuality({
      agent_output: data,
      agent_type: 'initial-coding',
      original_agent_input: data
    })
  }

  const handleRetryAgent = async (retryData: RetryAgentRequest) => {
    console.log('🔄 Initial Coding retry called with:', retryData)
    return await retryAgent(retryData)
  }

  return (
    <div>
      {hasPreviousData && (
        <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <div className="text-green-600">✅</div>
            <div>
              <h3 className="text-sm font-medium text-green-800">Data Loaded from Previous Agent</h3>
              <p className="text-sm text-green-700">Documents from the Retriever or Literature Review agent have been automatically loaded.</p>
            </div>
          </div>
        </div>
      )}
      <EnhancedAgentForm
        agentType="initial-coding"
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