// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  timestamp?: string
}

// Pipeline Types
export interface PipelineRequest {
  query: string
  research_domain: string
  max_results?: number
  year_from?: number
  year_to?: number
  quality_threshold?: number
  pipeline_config?: {
    enable_supervisor?: boolean
    auto_retry_failed_steps?: boolean
    save_intermediate_results?: boolean
  }
}

export interface PipelineResponse {
  success: boolean
  pipeline_id: string
  status: 'running' | 'completed' | 'failed' | 'halted'
  data: {
    current_step?: number
    total_steps?: number
    started_at?: string
    query?: string
    research_domain?: string
    quality_scores?: Record<string, number>
    supervisor_decisions?: Record<string, any>
  }
  timestamp: string
}

export interface PipelineProgress {
  pipeline_id: string
  status: 'running' | 'completed' | 'failed' | 'halted'
  current_step?: number
  total_steps?: number
  created_at?: string
  error_message?: string
  query?: string
  progress?: {
    current_step: number
    total_steps: number
    percentage: number
  }
  steps?: Record<string, {
    step_number: number
    step_name: string
    status: string
    timestamp: string
  }>
  quality_scores?: Record<string, number>
  supervisor_decisions?: Record<string, any>
  started_at?: string
  estimated_completion?: string
}

export interface PipelineResults {
  pipeline_id: string
  pipeline_status: string
  results: Record<string, any>
  quality_scores: Record<string, number>
  supervisor_decisions: Record<string, any>
  steps: Record<string, any>
  started_at?: string
  completed_at?: string
  query?: string
  research_domain?: string
}

export interface PipelineStatistics {
  total_pipelines: number
  completed: number
  failed: number
  halted: number
  running: number
  success_rate: number
  average_processing_time?: number
  research_domains?: Record<string, number>
}

// Agent Types
export interface AgentResponse {
  success: boolean
  agent_type?: string
  data: any
  timestamp: string
}

export interface AgentStatus {
  agent_type: string
  status: 'ready' | 'running' | 'error' | 'offline'
  last_used?: string
  performance_metrics?: {
    total_operations: number
    success_rate: number
    average_response_time: number
  }
}

// Agent Request Types
export interface DataExtractorRequest {
  query: string
  research_domain: string
  max_results?: number
  year_from?: number
  year_to?: number
}

export interface RetrieverRequest {
  query: string
  research_domain: string
  top_k?: number
  collection_name?: string
}

export interface LiteratureReviewRequest {
  documents: Array<{
    title: string
    authors?: string
    content: string
    year?: number
    doi?: string
    source?: string
    paper_id?: string
    chunk_index?: number
    research_domain?: string
    uuid?: string
    metadata?: {
      distance?: number
      certainty?: number
    }
  }>
  research_domain: string
  review_type?: string
}

export interface InitialCodingRequest {
  documents: Array<{
    title: string
    authors?: string
    content: string
    year?: number
    doi?: string
    source?: string
    paper_id?: string
    chunk_index?: number
    research_domain?: string
    uuid?: string
    metadata?: {
      distance?: number
      certainty?: number
    }
  }>
  research_domain: string
  coding_approach?: string
}

export interface ThematicGroupingRequest {
  coded_units: Array<{
    unit_id: string
    content: string
    codes: string[]
    confidence: number
    source_document?: string
  }>
  research_domain: string
  max_themes?: number
  min_codes_per_theme?: number
}

export interface ThemeRefinementRequest {
  themes: Array<{
    theme_name: string
    codes: string[]
    representative_units: string[]
    description?: string
  }>
  research_domain: string
  refinement_level?: string
}

export interface ReportGenerationRequest {
  sections: {
    literature_review?: any
    initial_coding?: any
    thematic_grouping?: any
    theme_refinement?: any
    research_domain?: string
  }
  research_domain?: string
  report_format?: string
}

// Document Types
export interface Document {
  title: string
  authors?: string
  content: string
  year?: number
  doi?: string
  source?: string
  paper_id?: string
  chunk_index?: number
  research_domain?: string
  uuid?: string
  metadata?: {
    distance?: number
    certainty?: number
  }
}

// Coded Unit Types
export interface CodedUnit {
  unit_id: string
  content: string
  codes: string[]
  confidence: number
  source_document?: string
}

// Theme Types
export interface Theme {
  theme_name: string
  codes: string[]
  representative_units: string[]
  description?: string
}

// Supervisor Types
export interface SupervisorRequest {
  agent_type: string
  agent_output: any
  original_agent_input: any
}

export interface RetryAgentRequest {
  agent_type: string
  original_agent_input: any
  enhanced_context: string
  user_context?: string
}

export interface SupervisorAssessment {
  status: 'APPROVED' | 'REVISE' | 'HALT'
  quality_score: number
  confidence: number
  issues_found: string[]
  improvement_suggestions: string[]
  enhanced_context_prompt: string
  assessment_reasoning: string
}

export interface SupervisorResult {
  initial_assessment: SupervisorAssessment
  final_status: 'APPROVED' | 'NEEDS_RETRY' | 'HALTED' | 'FAILED_RETRY'
  final_message: string
  retry_attempts: number
  retry_output: any | null
  final_assessment: SupervisorAssessment | null
} 