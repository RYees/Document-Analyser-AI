'use client'

import { EnhancedAgentForm } from '@/components/agents/enhanced-agent-form'
import { testDataExtractor, checkQuality, retryAgent } from '@/lib/api'
import { AGENT_TYPES } from '@/lib/utils'
import type { DataExtractorRequest, RetryAgentRequest } from '@/types/api'

export default function DataExtractorPage() {
  const agent = AGENT_TYPES.dataExtractor

  const fields = [
    {
      name: 'query',
      label: 'Search Query',
      type: 'text' as const,
      required: true,
      placeholder: 'Enter your research query (e.g., "transparency in blockchain technology")',
      helpText: 'The main search term to find relevant academic papers'
    },
    {
      name: 'research_domain',
      label: 'Research Domain',
      type: 'text' as const,
      required: true,
      placeholder: 'Enter research domain (e.g., "Blockchain Technology")',
      helpText: 'The specific research area or domain for context'
    },
    {
      name: 'max_results',
      label: 'Maximum Results',
      type: 'number' as const,
      required: false,
      placeholder: '20',
      helpText: 'Maximum number of documents to retrieve (1-50)'
    },
    {
      name: 'year_from',
      label: 'Year From',
      type: 'number' as const,
      required: false,
      placeholder: '2000',
      helpText: 'Start year for document search (optional)'
    },
    {
      name: 'year_to',
      label: 'Year To',
      type: 'number' as const,
      required: false,
      placeholder: '2025',
      helpText: 'End year for document search (optional)'
    }
  ]

  const nextAgents = [
    {
      name: 'Retriever',
      href: '/agents/retriever',
      description: 'Search and retrieve relevant documents from vector store',
      icon: '🔍'
    }
  ]

  const defaultValues = {
    query: '',
    research_domain: ''
  }

  const handleSubmit = async (data: DataExtractorRequest) => {
    console.log('📝 Data Extractor handleSubmit called with:', data)
    return await testDataExtractor(data)
  }

  const handleSupervisorCheck = async (data: any) => {
    console.log('🔍 Data Extractor supervisor check called with:', data)
    return await checkQuality({
      agent_output: data,
      agent_type: 'data-extractor',
      original_agent_input: data
    })
  }

  const handleRetryAgent = async (retryData: RetryAgentRequest) => {
    console.log('🔄 Data Extractor retry called with:', retryData)
    return await retryAgent(retryData)
  }

  return (
    <EnhancedAgentForm
      agentType="data-extractor"
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
  )
} 