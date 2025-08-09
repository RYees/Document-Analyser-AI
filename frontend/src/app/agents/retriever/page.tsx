'use client'

import { EnhancedAgentForm } from '@/components/agents/enhanced-agent-form'
import { testRetriever, checkQuality, retryAgent } from '@/lib/api'
import { AGENT_TYPES } from '@/lib/utils'
import type { RetrieverRequest, RetryAgentRequest } from '@/types/api'

export default function RetrieverPage() {
  const agent = AGENT_TYPES.retriever

  const fields = [
    {
      name: 'query',
      label: 'Search Query',
      type: 'text' as const,
      required: true,
      placeholder: 'Enter your search query (e.g., "transparency in blockchain")',
      helpText: 'The search term to find relevant documents'
    },
    {
      name: 'research_domain',
      label: 'Research Domain',
      type: 'text' as const,
      required: true,
      placeholder: 'Enter research domain (e.g., "Blockchain Technology")',
      helpText: 'The specific research area for context'
    },
    {
      name: 'top_k',
      label: 'Top K Results',
      type: 'number' as const,
      required: false,
      placeholder: '10',
      helpText: 'Number of most relevant documents to retrieve (1-50)'
    },
    {
      name: 'collection_name',
      label: 'Collection Name',
      type: 'text' as const,
      required: false,
      placeholder: 'ResearchPaper',
      helpText: 'Name of the vector store collection to search in'
    }
  ]

  const nextAgents = [
    {
      name: 'Literature Review',
      href: '/agents/literature-review',
      description: 'Generate literature review from retrieved documents',
      icon: '📚'
    },
    {
      name: 'Initial Coding',
      href: '/agents/initial-coding',
      description: 'Perform coding analysis on documents',
      icon: '🎯'
    }
  ]

  const defaultValues = {
    query: '',
    research_domain: ''
  }

  const handleSubmit = async (data: RetrieverRequest) => {
    const result = await testRetriever(data)
    
    // Store the result for the next agents (Literature Review and Initial Coding)
    if (result.success && result.data && result.data.documents) {
      console.log('🔍 [RETRIEVER] Storing documents for next agents:', result.data.documents.length, 'documents')
      console.log('🔍 [RETRIEVER] First document sample:', result.data.documents[0])
      
      const retrieverData = {
        documents: result.data.documents,
        research_domain: data.research_domain,
        query: data.query
      }
      
      console.log('🔍 [RETRIEVER] Storing retriever data:', retrieverData)
      localStorage.setItem('agent_data_retriever', JSON.stringify(retrieverData))
      
      console.log('🔍 [RETRIEVER] Data stored for Literature Review and Initial Coding to access')
    }
    
    return result
  }

  const handleSupervisorCheck = async (data: any) => {
    console.log('🔍 Retriever supervisor check called with:', data)
    return await checkQuality({
      agent_output: data,
      agent_type: 'retriever',
      original_agent_input: data
    })
  }

  const handleRetryAgent = async (retryData: RetryAgentRequest) => {
    console.log('🔄 Retriever retry called with:', retryData)
    return await retryAgent(retryData)
  }

  return (
    <EnhancedAgentForm
      agentType="retriever"
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