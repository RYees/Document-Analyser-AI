import { API_BASE_URL, API_ENDPOINTS } from './utils'
import type {
  ApiResponse,
  PipelineRequest,
  PipelineResponse,
  PipelineProgress,
  PipelineStatistics,
  AgentResponse,
  DataExtractorRequest,
  RetrieverRequest,
  LiteratureReviewRequest,
  InitialCodingRequest,
  ThematicGroupingRequest,
  ThemeRefinementRequest,
  ReportGenerationRequest,
  SupervisorRequest,
  RetryAgentRequest,
  SupervisorResult
} from '@/types/api'

// Generic API client
class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    console.log('🌐 Making API request to:', url)
    console.log('🌐 Request options:', options)

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      console.log('🌐 Sending request...')
      const response = await fetch(url, config)
      console.log('🌐 Response status:', response.status)
      console.log('🌐 Response headers:', Object.fromEntries(response.headers.entries()))

      if (!response.ok) {
        const errorText = await response.text()
        console.error('🌐 API error response:', errorText)
        let errorData
        try {
          errorData = JSON.parse(errorText)
        } catch {
          errorData = { detail: errorText }
        }
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('🌐 API response data:', data)
      return data
    } catch (error) {
      console.error(`🌐 API request failed for ${endpoint}:`, error)
      throw error
    }
  }

  // Pipeline endpoints
  async createPipeline(data: PipelineRequest): Promise<PipelineResponse> {
    return this.request<PipelineResponse>(API_ENDPOINTS.pipelines.create, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async listPipelines(params?: {
    limit?: number
    status?: string
    research_domain?: string
  }): Promise<PipelineResponse[]> {
    const searchParams = new URLSearchParams()
    if (params?.limit) searchParams.append('limit', params.limit.toString())
    if (params?.status) searchParams.append('status', params.status)
    if (params?.research_domain) searchParams.append('research_domain', params.research_domain)

    const queryString = searchParams.toString()
    const endpoint = queryString ? `${API_ENDPOINTS.pipelines.list}?${queryString}` : API_ENDPOINTS.pipelines.list
    
    return this.request<PipelineResponse[]>(endpoint)
  }

  async getPipelineProgress(pipelineId: string): Promise<ApiResponse<PipelineProgress>> {
    return this.request<ApiResponse<PipelineProgress>>(API_ENDPOINTS.pipelines.progress(pipelineId))
  }

  async getPipelineResults(pipelineId: string): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>(API_ENDPOINTS.pipelines.results(pipelineId))
  }

  async getPipelineStatistics(): Promise<ApiResponse<PipelineStatistics>> {
    return this.request<ApiResponse<PipelineStatistics>>(API_ENDPOINTS.pipelines.statistics)
  }

  async deletePipeline(pipelineId: string): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>(API_ENDPOINTS.pipelines.delete(pipelineId), {
      method: 'DELETE',
    })
  }

  async retryPipelineStep(pipelineId: string, stepName: string): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>(API_ENDPOINTS.pipelines.retry(pipelineId, stepName), {
      method: 'POST',
    })
  }

  async haltPipeline(pipelineId: string, reason: string): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>(API_ENDPOINTS.pipelines.halt(pipelineId, reason), {
      method: 'POST',
    })
  }

  async downloadPipelineReport(pipelineId: string, format: string = 'pdf'): Promise<Blob> {
    const url = `${this.baseUrl}${API_ENDPOINTS.pipelines.download(pipelineId)}?format=${format}`
    console.log('🌐 Downloading report from:', url)
    
    const response = await fetch(url)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('🌐 Download error:', errorText)
      throw new Error(`Download failed: ${response.status} ${response.statusText}`)
    }
    
    return response.blob()
  }

  // Agent endpoints
  async testDataExtractor(data: DataExtractorRequest): Promise<AgentResponse> {
    return this.request<AgentResponse>(API_ENDPOINTS.agents.dataExtractor, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async testRetriever(data: RetrieverRequest): Promise<AgentResponse> {
    return this.request<AgentResponse>(API_ENDPOINTS.agents.retriever, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async testLiteratureReview(data: LiteratureReviewRequest): Promise<AgentResponse> {
    return this.request<AgentResponse>(API_ENDPOINTS.agents.literatureReview, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async testInitialCoding(data: InitialCodingRequest): Promise<AgentResponse> {
    return this.request<AgentResponse>(API_ENDPOINTS.agents.initialCoding, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async testThematicGrouping(data: ThematicGroupingRequest): Promise<AgentResponse> {
    return this.request<AgentResponse>(API_ENDPOINTS.agents.thematicGrouping, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async testThemeRefiner(data: ThemeRefinementRequest): Promise<AgentResponse> {
    return this.request<AgentResponse>(API_ENDPOINTS.agents.themeRefiner, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async testReportGenerator(data: ReportGenerationRequest): Promise<AgentResponse> {
    return this.request<AgentResponse>(API_ENDPOINTS.agents.reportGenerator, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Supervisor endpoints
  async checkQuality(data: SupervisorRequest): Promise<AgentResponse> {
    return this.request<AgentResponse>(API_ENDPOINTS.agents.supervisor, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async retryAgent(data: RetryAgentRequest): Promise<AgentResponse> {
    return this.request<AgentResponse>(API_ENDPOINTS.agents.retry, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getAgentStatus(): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>(API_ENDPOINTS.agents.status)
  }

  async getAgentTypes(): Promise<string[]> {
    return this.request<string[]>(API_ENDPOINTS.agents.types)
  }

  async testConnection(): Promise<{ success: boolean; message: string }> {
    try {
      console.log('🔗 Testing API connection...')
      const response = await fetch(`${this.baseUrl}/api/v1/agents/status`)
      console.log('🔗 Connection test response status:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        return { success: true, message: 'API connected successfully' }
      } else {
        return { success: false, message: `HTTP ${response.status}: ${response.statusText}` }
      }
    } catch (error) {
      console.error('🔗 Connection test failed:', error)
      return { success: false, message: `Connection failed: ${error}` }
    }
  }
}

// Create and export the API client instance
export const apiClient = new ApiClient(API_BASE_URL)

// Export individual functions for convenience with proper binding
export const createPipeline = apiClient.createPipeline.bind(apiClient)
export const listPipelines = apiClient.listPipelines.bind(apiClient)
export const getPipelineProgress = apiClient.getPipelineProgress.bind(apiClient)
export const getPipelineResults = apiClient.getPipelineResults.bind(apiClient)
export const getPipelineStatistics = apiClient.getPipelineStatistics.bind(apiClient)
export const deletePipeline = apiClient.deletePipeline.bind(apiClient)
export const retryPipelineStep = apiClient.retryPipelineStep.bind(apiClient)
export const haltPipeline = apiClient.haltPipeline.bind(apiClient)
export const downloadPipelineReport = apiClient.downloadPipelineReport.bind(apiClient)
export const testDataExtractor = apiClient.testDataExtractor.bind(apiClient)
export const testRetriever = apiClient.testRetriever.bind(apiClient)
export const testLiteratureReview = apiClient.testLiteratureReview.bind(apiClient)
export const testInitialCoding = apiClient.testInitialCoding.bind(apiClient)
export const testThematicGrouping = apiClient.testThematicGrouping.bind(apiClient)
export const testThemeRefiner = apiClient.testThemeRefiner.bind(apiClient)
export const testReportGenerator = apiClient.testReportGenerator.bind(apiClient)
export const checkQuality = apiClient.checkQuality.bind(apiClient)
export const retryAgent = apiClient.retryAgent.bind(apiClient)
export const getAgentStatus = apiClient.getAgentStatus.bind(apiClient)
export const getAgentTypes = apiClient.getAgentTypes.bind(apiClient)
export const testConnection = apiClient.testConnection.bind(apiClient) 