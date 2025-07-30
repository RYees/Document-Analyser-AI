"""
Base Research Agent Module
Abstract base class for all research agents
"""

import os
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_community.vectorstores import Weaviate
from langchain_openai import OpenAIEmbeddings

from ..core.research_state import ResearchState, ResearchTask, TaskStatus
from .llm_backends import OpenAIBackend, LLMBackend

# Check if weaviate is available
try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

class BaseResearchAgent(ABC):
    """Abstract base class for all research agents"""
    
    def __init__(self, agent_name: str):
        """Initialize base agent"""
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name}")
        
        # Initialize LLM backend
        self.llm_backend: LLMBackend = OpenAIBackend()
        self.llm: ChatOpenAI = self.llm_backend.llm
        
        # Initialize embeddings directly
        self.embeddings: OpenAIEmbeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key="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"
        )
        
        # Initialize tools and agent
        self.tools: List[BaseTool] = []
        self.agent_executor: Optional[AgentExecutor] = None
        
        # Vector store will be handled by VectorStoreManager
        self.vector_store_manager = None
        
        # Setup agent
        self._setup_agent()
    
    def _initialize_vector_store_manager(self):
        """Initialize VectorStoreManager for this agent"""
        try:
            from analyser.utils.vector_store_manager import VectorStoreManager
            self.vector_store_manager = VectorStoreManager(
                collection_name=f"{self.agent_name}_research",
                research_domain="General"
            )
            self.logger.info(f"VectorStoreManager initialized for {self.agent_name}")
        except Exception as e:
            self.logger.warning(f"Failed to initialize VectorStoreManager: {e}")
            self.vector_store_manager = None
    
    def add_tool(self, tool: BaseTool) -> None:
        """Add a tool to the agent"""
        self.tools.append(tool)
        self.logger.debug(f"Added tool {tool.name} to {self.agent_name}")
    
    def _setup_agent(self) -> None:
        """Setup the LangChain agent with tools and prompt"""
        # Add agent-specific tools
        self._add_agent_tools()
        
        # Create system prompt
        system_prompt = self._get_system_prompt()
        
        # Create agent prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10
        )
        
        self.logger.info(f"Agent {self.agent_name} setup completed with {len(self.tools)} tools")
    
    @abstractmethod
    def _add_agent_tools(self) -> None:
        """Add agent-specific tools - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get agent-specific system prompt - to be implemented by subclasses"""
        pass
    
    async def execute_task(self, state: ResearchState, task: ResearchTask) -> Dict[str, Any]:
        """Execute a research task"""
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting task {task.id} for {self.agent_name}")
            
            # Update task status
            state.update_task(task.id, status=TaskStatus.IN_PROGRESS)
            state.current_task = task
            
            # Prepare input for agent
            agent_input = self._prepare_agent_input(state, task)
            
            # Run agent
            result = await self.agent_executor.ainvoke({
                "input": agent_input,
                "chat_history": []
            })
            
            # Process result
            processed_result = self._process_agent_result(result, state, task)
            
            # Update task
            execution_time = time.time() - start_time
            state.update_task(
                task.id,
                status=TaskStatus.COMPLETED,
                result=processed_result,
                execution_time=execution_time
            )
            
            # Update state with agent-specific data
            self._update_state_with_result(state, processed_result, task)
            
            self.logger.info(f"Task {task.id} completed successfully in {execution_time:.2f}s")
            return processed_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Task {task.id} failed: {str(e)}"
            
            self.logger.error(error_msg)
            
            # Update task with error
            state.update_task(
                task.id,
                status=TaskStatus.FAILED,
                error=error_msg,
                execution_time=execution_time
            )
            
            raise
    
    @abstractmethod
    def _prepare_agent_input(self, state: ResearchState, task: ResearchTask) -> str:
        """Prepare input for the agent - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def _process_agent_result(self, result: Dict[str, Any], state: ResearchState, task: ResearchTask) -> Dict[str, Any]:
        """Process agent result - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def _update_state_with_result(self, state: ResearchState, result: Dict[str, Any], task: ResearchTask) -> None:
        """Update state with agent result - to be implemented by subclasses"""
        pass
    
    async def handle_human_feedback(self, state: ResearchState, task: ResearchTask, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Handle human feedback for a task"""
        try:
            self.logger.info(f"Processing human feedback for task {task.id}")
            
            # Prepare feedback input
            feedback_input = self._prepare_feedback_input(state, task, feedback)
            
            # Run agent with feedback
            result = await self.agent_executor.ainvoke({
                "input": feedback_input,
                "chat_history": []
            })
            
            # Process updated result
            updated_result = self._process_agent_result(result, state, task)
            
            # Update task
            state.update_task(
                task.id,
                status=TaskStatus.COMPLETED,
                result=updated_result
            )
            
            # Update state
            self._update_state_with_result(state, updated_result, task)
            
            self.logger.info(f"Human feedback processed successfully for task {task.id}")
            return updated_result
            
        except Exception as e:
            error_msg = f"Failed to process human feedback: {str(e)}"
            self.logger.error(error_msg)
            raise
    
    @abstractmethod
    def _prepare_feedback_input(self, state: ResearchState, task: ResearchTask, feedback: Dict[str, Any]) -> str:
        """Prepare input for feedback processing - to be implemented by subclasses"""
        pass
    
    async def store_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Store documents using VectorStoreManager"""
        try:
            if self.vector_store_manager is None:
                self._initialize_vector_store_manager()
            
            if self.vector_store_manager:
                # Extract content and metadata
                chunks = [doc.get("content", "") for doc in documents]
                metadata_list = [{"source": doc.get("source", ""), "title": doc.get("title", "")} for doc in documents]
                
                # Store using VectorStoreManager
                success = self.vector_store_manager.add_chunks(chunks, metadata_list)
                if success:
                    self.logger.info(f"Successfully stored {len(documents)} documents")
                else:
                    self.logger.warning("Failed to store documents")
            else:
                self.logger.warning("VectorStoreManager not available")
                
        except Exception as e:
            self.logger.error(f"Failed to store documents: {e}")
    
    async def search_documents(self, query: str, k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search documents using VectorStoreManager"""
        try:
            if self.vector_store_manager is None:
                self._initialize_vector_store_manager()
            
            if self.vector_store_manager:
                results = self.vector_store_manager.similarity_search(query, top_k=k)
                return [{"content": result, "score": 1.0} for result in results]
            else:
                self.logger.warning("VectorStoreManager not available")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to search documents: {e}")
            return []
    
    def create_chain(self, prompt_template: str, output_parser=None):
        """Create a simple LLM chain"""
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
        
        prompt = PromptTemplate(
            input_variables=["input"],
            template=prompt_template
        )
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_parser=output_parser
        )
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": self.agent_name,
            "tools": [tool.name for tool in self.tools],
            "llm_backend": self.llm_backend.get_backend_info(),
            "vector_store_available": self.vector_store_manager is not None
        } 