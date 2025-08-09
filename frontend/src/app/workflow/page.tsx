'use client'

import { useState } from 'react'
import { 
  Plus, 
  ArrowRight, 
  Play, 
  Save,
  Trash2,
  Settings
} from 'lucide-react'
import { AGENT_TYPES } from '@/lib/utils'

interface WorkflowStep {
  id: string
  agentType: string
  agentName: string
  icon: string
  config: any
}

export default function WorkflowPage() {
  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([])
  const [workflowName, setWorkflowName] = useState('')
  const [isRunning, setIsRunning] = useState(false)

  const addStep = (agentType: string) => {
    const agent = AGENT_TYPES[agentType as keyof typeof AGENT_TYPES]
    const newStep: WorkflowStep = {
      id: `step-${Date.now()}`,
      agentType,
      agentName: agent.name,
      icon: agent.icon,
      config: {}
    }
    setWorkflowSteps([...workflowSteps, newStep])
  }

  const removeStep = (stepId: string) => {
    setWorkflowSteps(workflowSteps.filter(step => step.id !== stepId))
  }

  const moveStep = (stepId: string, direction: 'up' | 'down') => {
    const index = workflowSteps.findIndex(step => step.id === stepId)
    if (index === -1) return

    const newSteps = [...workflowSteps]
    if (direction === 'up' && index > 0) {
      [newSteps[index], newSteps[index - 1]] = [newSteps[index - 1], newSteps[index]]
    } else if (direction === 'down' && index < newSteps.length - 1) {
      [newSteps[index], newSteps[index + 1]] = [newSteps[index + 1], newSteps[index]]
    }
    setWorkflowSteps(newSteps)
  }

  const runWorkflow = async () => {
    setIsRunning(true)
    // TODO: Implement workflow execution
    setTimeout(() => {
      setIsRunning(false)
    }, 2000)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workflow Builder</h1>
          <p className="text-gray-600 mt-1">
            Create custom research workflows by connecting multiple agents
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={runWorkflow}
            disabled={workflowSteps.length === 0 || isRunning}
            className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <Play className="w-4 h-4 mr-2" />
            {isRunning ? 'Running...' : 'Run Workflow'}
          </button>
          <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Save className="w-4 h-4 mr-2" />
            Save Workflow
          </button>
        </div>
      </div>

      {/* Workflow Configuration */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Workflow Configuration</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Workflow Name
            </label>
            <input
              type="text"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              placeholder="Enter workflow name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Available Agents */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Agents</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(AGENT_TYPES).map(([key, agent]) => (
            <button
              key={key}
              onClick={() => addStep(key)}
              className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-left"
            >
              <div className="text-2xl">{agent.icon}</div>
              <div>
                <h3 className="font-medium text-gray-900">{agent.name}</h3>
                <p className="text-sm text-gray-600">{agent.description}</p>
              </div>
              <Plus className="w-4 h-4 text-gray-400 ml-auto" />
            </button>
          ))}
        </div>
      </div>

      {/* Workflow Steps */}
      {workflowSteps.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Workflow Steps</h2>
          <div className="space-y-4">
            {workflowSteps.map((step, index) => (
              <div key={step.id} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3 flex-1">
                  <div className="text-2xl">{step.icon}</div>
                  <div>
                    <h3 className="font-medium text-gray-900">{step.agentName}</h3>
                    <p className="text-sm text-gray-500">Step {index + 1}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => moveStep(step.id, 'up')}
                    disabled={index === 0}
                    className="p-1 text-gray-400 hover:text-gray-600 disabled:text-gray-200"
                  >
                    ↑
                  </button>
                  <button
                    onClick={() => moveStep(step.id, 'down')}
                    disabled={index === workflowSteps.length - 1}
                    className="p-1 text-gray-400 hover:text-gray-600 disabled:text-gray-200"
                  >
                    ↓
                  </button>
                  <button
                    onClick={() => removeStep(step.id)}
                    className="p-1 text-red-400 hover:text-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                
                {index < workflowSteps.length - 1 && (
                  <ArrowRight className="w-5 h-5 text-gray-400" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Workflow Preview */}
      {workflowSteps.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Workflow Preview</h2>
          <div className="flex items-center space-x-4 overflow-x-auto">
            {workflowSteps.map((step, index) => (
              <div key={step.id} className="flex items-center space-x-2">
                <div className="flex items-center space-x-2 bg-white px-3 py-2 rounded-lg border border-gray-200">
                  <span className="text-lg">{step.icon}</span>
                  <span className="text-sm font-medium text-gray-900">{step.agentName}</span>
                </div>
                {index < workflowSteps.length - 1 && (
                  <ArrowRight className="w-4 h-4 text-gray-400" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
} 