'use client'

import { useState, useEffect } from 'react'
import { EnhancedAgentForm } from '@/components/agents/enhanced-agent-form'
import { testThematicGrouping, checkQuality, retryAgent } from '@/lib/api'
import { AGENT_TYPES } from '@/lib/utils'
import type { ThematicGroupingRequest, RetryAgentRequest } from '@/types/api'

export default function ThematicGroupingPage() {
  const agent = AGENT_TYPES.thematicGrouping

  // Try to load data from previous agent (initial-coding)
  const getDefaultValues = () => {
    try {
      const initialCodingData = localStorage.getItem('agent_data_thematic-grouping')
      if (initialCodingData) {
        const parsed = JSON.parse(initialCodingData)
        // If we have coded units from initial coding, use them
        if (parsed.coded_units && Array.isArray(parsed.coded_units)) {
          return {
            research_domain: parsed.research_domain || '',
            coded_units: JSON.stringify(parsed.coded_units, null, 2)
          }
        }
      }
    } catch (error) {
      console.log('No previous agent data found')
    }
    
    // Return empty values when no previous data exists
    return {
      research_domain: '',
      coded_units: ''
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
      name: 'max_themes',
      label: 'Maximum Themes',
      type: 'number' as const,
      required: false,
      placeholder: '5',
      helpText: 'Maximum number of themes to generate (2-10)'
    },
    {
      name: 'min_codes_per_theme',
      label: 'Minimum Codes per Theme',
      type: 'number' as const,
      required: false,
      placeholder: '3',
      helpText: 'Minimum number of codes required per theme'
    },
    {
      name: 'coded_units',
      label: 'Coded Units (JSON)',
      type: 'coded_units' as const,
      required: true,
      placeholder: `[
  {
    "unit_id": "unit_1",
    "content": "Text content from document...",
    "codes": ["code1", "code2"],
    "confidence": 0.85,
    "source_document": "Document Title"
  }
]`,
      helpText: 'JSON array of coded units from Initial Coding Agent. Each unit should have content, codes, and confidence score.'
    }
  ]

  const nextAgents = [
    {
      name: 'Theme Refiner',
      href: '/agents/theme-refiner',
      description: 'Refine themes with academic polish',
      icon: '✨'
    }
  ]

  const defaultValues = getDefaultValues()
  const [hasPreviousData, setHasPreviousData] = useState(false)

  // Check for previous data on client side
  useEffect(() => {
    const previousData = localStorage.getItem('agent_data_thematic-grouping')
    setHasPreviousData(previousData !== null)
  }, [])

  const handleSubmit = async (data: ThematicGroupingRequest) => {
    // Parse JSON coded_units if they're provided as a string
    if (typeof data.coded_units === 'string') {
      data.coded_units = JSON.parse(data.coded_units)
    }
    
    const result = await testThematicGrouping(data)
    
    // Store the result for the next agent (Theme Refiner)
    if (result.success && result.data) {
      localStorage.setItem('agent_data_theme-refiner', JSON.stringify({
        themes: result.data.themes,
        research_domain: data.research_domain,
        max_themes: data.max_themes
      }))
    }
    
    return result
  }

  const handleSupervisorCheck = async (data: any) => {
    console.log('🔍 Thematic Grouping supervisor check called with:', data)
    return await checkQuality({
      agent_output: data,
      agent_type: 'thematic-grouping',
      original_agent_input: data
    })
  }

  const handleRetryAgent = async (retryData: RetryAgentRequest) => {
    console.log('🔄 Thematic Grouping retry called with:', retryData)
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
              <p className="text-sm text-green-700">Coded units from the Initial Coding agent have been automatically loaded.</p>
            </div>
          </div>
        </div>
      )}
      <EnhancedAgentForm
        agentType="thematic-grouping"
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