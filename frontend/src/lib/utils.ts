import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// API Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// API Endpoints
export const API_ENDPOINTS = {
  // Pipeline endpoints
  pipelines: {
    list: '/api/v1/pipelines/',
    create: '/api/v1/pipelines/',
    progress: (id: string) => `/api/v1/pipelines/${id}/progress`,
    results: (id: string) => `/api/v1/pipelines/${id}/results`,
    download: (id: string) => `/api/v1/pipelines/${id}/download`,
    statistics: '/api/v1/pipelines/statistics/overview',
    delete: (id: string) => `/api/v1/pipelines/${id}`,
    retry: (id: string, stepName: string) => `/api/v1/pipelines/${id}/retry?step_name=${stepName}`,
    halt: (id: string, reason: string) => `/api/v1/pipelines/${id}/halt?reason=${encodeURIComponent(reason)}`,
  },
  // Agent endpoints
  agents: {
    dataExtractor: '/api/v1/agents/data-extractor/extract',
    retriever: '/api/v1/agents/retriever/search',
    literatureReview: '/api/v1/agents/literature-review/generate',
    initialCoding: '/api/v1/agents/initial-coding/code',
    thematicGrouping: '/api/v1/agents/thematic-grouping/group',
    themeRefiner: '/api/v1/agents/theme-refiner/refine',
    reportGenerator: '/api/v1/agents/report-generator/generate',
    supervisor: '/api/v1/agents/supervisor/check-quality',
    retry: '/api/v1/agents/retry-agent',
    status: '/api/v1/agents/status',
    types: '/api/v1/agents/types',
  }
}

// Agent types for the UI
export const AGENT_TYPES = {
  dataExtractor: {
    name: 'Data Extractor',
    description: 'Fetch and extract academic papers from external sources',
    icon: '📄',
    color: 'blue',
    endpoint: API_ENDPOINTS.agents.dataExtractor
  },
  retriever: {
    name: 'Retriever',
    description: 'Search and retrieve relevant documents from vector store',
    icon: '🔍',
    color: 'green',
    endpoint: API_ENDPOINTS.agents.retriever
  },
  literatureReview: {
    name: 'Literature Review',
    description: 'Generate comprehensive literature review from documents',
    icon: '📚',
    color: 'purple',
    endpoint: API_ENDPOINTS.agents.literatureReview
  },
  initialCoding: {
    name: 'Initial Coding',
    description: 'Perform open coding analysis on documents',
    icon: '🎯',
    color: 'orange',
    endpoint: API_ENDPOINTS.agents.initialCoding
  },
  thematicGrouping: {
    name: 'Thematic Grouping',
    description: 'Group coded units into themes',
    icon: '🔗',
    color: 'indigo',
    endpoint: API_ENDPOINTS.agents.thematicGrouping
  },
  themeRefiner: {
    name: 'Theme Refiner',
    description: 'Refine themes with academic polish',
    icon: '✨',
    color: 'pink',
    endpoint: API_ENDPOINTS.agents.themeRefiner
  },
  reportGenerator: {
    name: 'Report Generator',
    description: 'Generate final academic report',
    icon: '📄',
    color: 'teal',
    endpoint: API_ENDPOINTS.agents.reportGenerator
  }
}

// Pipeline status colors
export const PIPELINE_STATUS_COLORS = {
  running: 'text-blue-600 bg-blue-50 border-blue-200',
  completed: 'text-green-600 bg-green-50 border-green-200',
  failed: 'text-red-600 bg-red-50 border-red-200',
  halted: 'text-yellow-600 bg-yellow-50 border-yellow-200'
}

// Agent status colors
export const AGENT_STATUS_COLORS = {
  ready: 'text-green-600 bg-green-50 border-green-200',
  running: 'text-blue-600 bg-blue-50 border-blue-200',
  error: 'text-red-600 bg-red-50 border-red-200',
  offline: 'text-gray-600 bg-gray-50 border-gray-200'
} 