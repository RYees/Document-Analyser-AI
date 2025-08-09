'use client'

import { useState, useEffect } from 'react'
import { EnhancedAgentForm } from '@/components/agents/enhanced-agent-form'
import { testThemeRefiner, checkQuality, retryAgent } from '@/lib/api'
import { AGENT_TYPES } from '@/lib/utils'
import type { ThemeRefinementRequest, RetryAgentRequest } from '@/types/api'

export default function ThemeRefinerPage() {
  const agent = AGENT_TYPES.themeRefiner

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
      name: 'refinement_level',
      label: 'Refinement Level',
      type: 'select' as const,
      required: false,
      options: [
        { value: 'basic', label: 'Basic Refinement' },
        { value: 'academic', label: 'Academic Polish' },
        { value: 'comprehensive', label: 'Comprehensive Refinement' }
      ],
      helpText: 'Level of refinement to apply to themes'
    },
    {
      name: 'themes',
      label: 'Themes (JSON)',
      type: 'themes' as const,
      required: true,
      placeholder: `[
  {
    "theme_name": "Transparency",
    "codes": ["transparency", "verification", "public"],
    "representative_units": ["Unit content 1", "Unit content 2"],
    "description": "Theme description..."
  }
]`,
      helpText: 'JSON array of themes from Thematic Grouping Agent. Each theme should have name, codes, and representative units.'
    }
  ]

  const getDefaultValues = () => {
    try {
      const thematicData = localStorage.getItem('agent_data_theme-refiner')
      if (thematicData) {
        const parsed = JSON.parse(thematicData)
        if (parsed.themes && Array.isArray(parsed.themes)) {
          return {
            research_domain: parsed.research_domain || '',
            themes: JSON.stringify(parsed.themes, null, 2)
          }
        }
      }
    } catch (error) {
      console.log('No previous agent data found')
    }
    // Return empty values when no previous data exists
    return {
      research_domain: '',
      themes: ''
    }
  }

  const nextAgents = [
    {
      name: 'Report Generator',
      href: '/agents/report-generator',
      description: 'Generate final academic report',
      icon: '📄'
    }
  ]

  const defaultValues = getDefaultValues()
  const [hasPreviousData, setHasPreviousData] = useState(false)

  // Check for previous data on client side
  useEffect(() => {
    const previousData = localStorage.getItem('agent_data_theme-refiner')
    setHasPreviousData(previousData !== null)
  }, [])

  const handleSubmit = async (data: ThemeRefinementRequest) => {
    // Parse JSON themes if they're provided as a string
    if (typeof data.themes === 'string') {
      data.themes = JSON.parse(data.themes)
    }
    
    const result = await testThemeRefiner(data)
    
    // Store the result for the next agent (Report Generator)
    if (result.success && result.data) {
      localStorage.setItem('agent_data_report-generator', JSON.stringify({
        theme_refinement: result.data,
        research_domain: data.research_domain,
        refinement_level: data.refinement_level
      }))
    }
    
    return result
  }

  const handleSupervisorCheck = async (data: any) => {
    console.log('🔍 Theme Refiner supervisor check called with:', data)
    return await checkQuality({
      agent_output: data,
      agent_type: 'theme-refiner',
      original_agent_input: data
    })
  }

  const handleRetryAgent = async (retryData: RetryAgentRequest) => {
    console.log('🔄 Theme Refiner retry called with:', retryData)
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
              <p className="text-sm text-green-700">Themes from the Thematic Grouping agent have been automatically loaded.</p>
            </div>
          </div>
        </div>
      )}
      <EnhancedAgentForm
        agentType="theme-refiner"
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