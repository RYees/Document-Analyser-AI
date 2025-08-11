'use client'

import { EnhancedAgentForm } from '@/components/agents/enhanced-agent-form'
import { testMultiSourceExtractor } from '@/lib/api'

type FieldDef = {
  name: string
  label: string
  type: 'text' | 'textarea' | 'number' | 'select' | 'multiselect' | 'chips' | 'json' | 'documents' | 'coded_units' | 'themes'
  required?: boolean
  placeholder?: string
  options?: Array<{ value: string; label: string }>
  defaultValue?: any
  helpText?: string
}

export default function MultiSourceExtractorPage() {
  const fields: FieldDef[] = [
    { name: 'query', label: 'Query', type: 'text', required: true, placeholder: 'e.g., blockchain governance' },
    { name: 'research_domain', label: 'Research Domain', type: 'text', required: false, placeholder: 'e.g., Technology' },
    { name: 'mode', label: 'Mode', type: 'select', required: true, options: [
      { value: 'auto', label: 'Auto (all sources)' },
      { value: 'manual', label: 'Manual (choose sources)' }
    ] },
    { name: 'sources', label: 'Sources', type: 'chips', required: false, helpText: 'Click to add, then remove with ×. Disabled in Auto mode.', options: [
      { value: 'openalex', label: 'OpenAlex' },
      { value: 'europe_pmc', label: 'Europe PMC' },
      { value: 'arxiv', label: 'arXiv' },
      { value: 'core', label: 'CORE' }
    ] },
    { name: 'enrich', label: 'Enrichment', type: 'select', required: true, options: [
      { value: 'none', label: 'None' },
      { value: 'standard', label: 'Standard (Crossref, Unpaywall)' },
      { value: 'deep', label: 'Deep (Crossref, Unpaywall, Semantic Scholar)' }
    ] },
    { name: 'limit', label: 'Limit', type: 'number', required: false, placeholder: 'e.g., 12' },
    { name: 'year_from', label: 'Year From', type: 'number', required: false, placeholder: 'e.g., 2023', helpText: 'Optional filter lower bound' },
    { name: 'year_to', label: 'Year To', type: 'number', required: false, placeholder: 'e.g., 2025', helpText: 'Optional filter upper bound' },
    { name: 'store', label: 'Store to Weaviate', type: 'select', required: true, options: [
      { value: 'false', label: 'No' },
      { value: 'true', label: 'Yes' }
    ] },
    { name: 'collection_name', label: 'Collection Name', type: 'text', required: false, placeholder: 'ResearchPaper' },
  ]

  const handleSubmit = async (form: any) => {
    const payload: any = {
      query: form.query,
      research_domain: form.research_domain || 'General',
      mode: form.mode || 'auto',
      enrich: form.enrich || 'standard',
      limit: typeof form.limit === 'number' ? form.limit : Number(form.limit) || 12,
      years: undefined,
      store: String(form.store) === 'true',
      collection_name: form.collection_name || 'ResearchPaper',
    }

    const yFrom = typeof form.year_from === 'number' ? form.year_from : (form.year_from ? Number(form.year_from) : undefined)
    const yTo = typeof form.year_to === 'number' ? form.year_to : (form.year_to ? Number(form.year_to) : undefined)
    if (yFrom || yTo) {
      payload.years = { from_year: yFrom, to_year: yTo }
    }

    if (payload.mode === 'manual' && Array.isArray(form.sources) && form.sources.length) {
      payload.sources = form.sources
    }

    return await testMultiSourceExtractor(payload)
  }

  return (
    <EnhancedAgentForm
      agentType="multi-source-extractor"
      agentName="Multi-Source Extractor"
      description="Discover papers across OpenAlex, Europe PMC, arXiv, CORE with optional enrichment. Optionally fetch full text via Playwright."
      icon="🌐"
      color="cyan"
      onSubmit={handleSubmit}
      fields={fields}
      defaultValues={{ mode: 'auto', enrich: 'standard', store: 'false' }}
    />
  )
} 