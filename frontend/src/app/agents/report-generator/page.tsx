'use client'

import { useState, useEffect } from 'react'
import { EnhancedAgentForm } from '@/components/agents/enhanced-agent-form'
import { testReportGenerator, checkQuality, retryAgent } from '@/lib/api'
import { AGENT_TYPES } from '@/lib/utils'
import type { ReportGenerationRequest, RetryAgentRequest } from '@/types/api'

export default function ReportGeneratorPage() {
  const agent = AGENT_TYPES.reportGenerator

  const fields = [
    {
      name: 'research_domain',
      label: 'Research Domain',
      type: 'text' as const,
      required: true,
      placeholder: 'Enter research domain (e.g., "Blockchain Technology")',
      helpText: 'The specific research area for the report'
    },
    {
      name: 'report_format',
      label: 'Report Format',
      type: 'select' as const,
      required: false,
      options: [
        { value: 'academic', label: 'Academic Paper' },
        { value: 'executive', label: 'Executive Summary' },
        { value: 'technical', label: 'Technical Report' }
      ],
      helpText: 'Format of the generated report'
    },
    {
      name: 'sections',
      label: 'Report Sections (JSON)',
      type: 'json' as const,
      required: true,
      placeholder: `{
  "literature_review": { /* Literature review output */ },
  "initial_coding": { /* Initial coding output */ },
  "thematic_grouping": { /* Thematic grouping output */ },
  "theme_refinement": { /* Theme refinement output */ },
  "research_domain": "Blockchain Technology"
}`,
      helpText: 'JSON object containing outputs from all previous agents. Include literature_review, initial_coding, thematic_grouping, and theme_refinement sections.'
    }
  ]

  const getDefaultValues = () => {
    if (typeof window === 'undefined') {
      return {
        research_domain: '',
        sections: ''
      }
    }
    try {
      // Load data from all previous agents
      const sections: any = {}
      let researchDomain = 'Blockchain Technology'
      let hasAnyData = false

      // Load Literature Review data
      const literatureData = localStorage.getItem('agent_data_literature-review')
      if (literatureData) {
        const parsed = JSON.parse(literatureData)
        sections.literature_review = parsed
        researchDomain = parsed.research_domain || researchDomain
        hasAnyData = true
      }

      // Load Initial Coding data
      const initialCodingData = localStorage.getItem('agent_data_initial-coding')
      if (initialCodingData) {
        const parsed = JSON.parse(initialCodingData)
        sections.initial_coding = parsed
        researchDomain = parsed.research_domain || researchDomain
        hasAnyData = true
      }

      // Load Thematic Grouping data
      const thematicGroupingData = localStorage.getItem('agent_data_thematic-grouping')
      if (thematicGroupingData) {
        const parsed = JSON.parse(thematicGroupingData)
        sections.thematic_grouping = parsed
        researchDomain = parsed.research_domain || researchDomain
        hasAnyData = true
      }

      // Load Theme Refinement data
      const themeRefinementData = localStorage.getItem('agent_data_theme-refiner')
      if (themeRefinementData) {
        const parsed = JSON.parse(themeRefinementData)
        sections.theme_refinement = parsed
        researchDomain = parsed.research_domain || researchDomain
        hasAnyData = true
      }

      // Load Report Generator data (if any)
      const reportGeneratorData = localStorage.getItem('agent_data_report-generator')
      if (reportGeneratorData) {
        const parsed = JSON.parse(reportGeneratorData)
        sections.theme_refinement = parsed.theme_refinement || sections.theme_refinement
        researchDomain = parsed.research_domain || researchDomain
        hasAnyData = true
      }

      if (hasAnyData) {
        sections.research_domain = researchDomain
        return {
          research_domain: researchDomain,
          sections: JSON.stringify(sections, null, 2)
        }
      }
    } catch (error) {
      console.log('Error loading previous agent data:', error)
    }

    // Return empty values when no previous data exists
    return {
      research_domain: '',
      sections: ''
    }
  }

  const defaultValues = getDefaultValues()
  const [hasPreviousData, setHasPreviousData] = useState(false)

  // Check for previous data on client side
  useEffect(() => {
    if (typeof window === 'undefined') return
    const hasLiteratureData = localStorage.getItem('agent_data_literature-review') !== null
    const hasInitialCodingData = localStorage.getItem('agent_data_initial-coding') !== null
    const hasThematicGroupingData = localStorage.getItem('agent_data_thematic-grouping') !== null
    const hasThemeRefinementData = localStorage.getItem('agent_data_theme-refiner') !== null
    const hasReportGeneratorData = localStorage.getItem('agent_data_report-generator') !== null
    
    setHasPreviousData(hasLiteratureData || hasInitialCodingData || hasThematicGroupingData || hasThemeRefinementData || hasReportGeneratorData)
  }, [])

  const handleSubmit = async (data: ReportGenerationRequest) => {
    // Parse JSON sections if they're provided as a string
    if (typeof data.sections === 'string') {
      data.sections = JSON.parse(data.sections)
    }
    return await testReportGenerator(data)
  }

  const handleSupervisorCheck = async (data: any) => {
    console.log('🔍 Report Generator supervisor check called with:', data)
    return await checkQuality({
      agent_output: data,
      agent_type: 'report-generator',
      original_agent_input: data
    })
  }

  const handleRetryAgent = async (retryData: RetryAgentRequest) => {
    console.log('🔄 Report Generator retry called with:', retryData)
    return await retryAgent(retryData)
  }

  return (
    <div>
      {hasPreviousData && (
        <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <div className="text-green-600">✅</div>
            <div>
              <h3 className="text-sm font-medium text-green-800">Data Loaded from Previous Agents</h3>
              <p className="text-sm text-green-700">Data from Literature Review, Initial Coding, Thematic Grouping, and Theme Refinement agents has been automatically loaded.</p>
            </div>
          </div>
        </div>
      )}
      <EnhancedAgentForm
        agentType="report-generator"
        agentName={agent.name}
        description={agent.description}
        icon={agent.icon}
        color={agent.color}
        onSubmit={handleSubmit}
        onSupervisorCheck={handleSupervisorCheck}
        onRetryAgent={handleRetryAgent}
        defaultValues={defaultValues}
        fields={fields}
        nextAgents={[]}
      />
    </div>
  )
} 