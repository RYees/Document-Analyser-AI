from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents import create_openai_functions_agent, AgentExecutor
import aiohttp
import asyncio
import json
import re
import numpy as np
from datetime import datetime
import os
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from io import BytesIO
import base64

from .base_agent import BaseResearchAgent
from ..core.research_state import ResearchState, ResearchTask, TaskStatus, ResearchPhase

# Tool Input Models
class WebScrapingInput(BaseModel):
    url: str = Field(description="URL to scrape for content")
    content_type: str = Field(default="blog", description="Type of content (blog, forum, social)")
    max_pages: int = Field(default=5, description="Maximum pages to scrape")

class Web3DataInput(BaseModel):
    protocol: str = Field(description="Web3 protocol to fetch data from")
    metric: str = Field(description="Metric to fetch (TVL, volume, users, etc.)")
    timeframe: str = Field(default="30d", description="Timeframe for data")

class QualitativeAnalysisInput(BaseModel):
    sources: List[str] = Field(description="List of sources to analyze")
    research_domain: str = Field(description="Research domain for context")
    analysis_type: str = Field(default="thematic", description="Type of analysis (thematic, sentiment, discourse)")

class QuantitativeAnalysisInput(BaseModel):
    data_sources: List[str] = Field(description="List of data sources")
    metrics: List[str] = Field(description="Metrics to analyze")
    analysis_type: str = Field(default="descriptive", description="Type of analysis (descriptive, correlation, regression)")

class ResultsIntegrationInput(BaseModel):
    qualitative_results: Dict[str, Any] = Field(description="Qualitative analysis results")
    quantitative_results: Dict[str, Any] = Field(description="Quantitative analysis results")
    research_questions: List[str] = Field(description="Research questions to address")

# LangChain Tools
class WebScrapingTool(BaseTool):
    name: str = "web_scraping"
    description: str = "Scrape content from blogs, forums, and social media"
    args_schema: type = WebScrapingInput
    
    async def _arun(self, url: str, content_type: str = "blog", max_pages: int = 5) -> Dict[str, Any]:
        """Scrape content from web sources"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Extract text content based on content type
                        if content_type == "blog":
                            content = self._extract_blog_content(soup)
                        elif content_type == "forum":
                            content = self._extract_forum_content(soup)
                        else:
                            content = soup.get_text()
                        
                        return {
                            "url": url,
                            "content_type": content_type,
                            "content": content,
                            "word_count": len(content.split()),
                            "scraped_at": datetime.utcnow().isoformat(),
                            "status": "success"
                        }
                    else:
                        return {
                            "url": url,
                            "status": "failed",
                            "error": f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            return {
                "url": url,
                "status": "failed",
                "error": str(e)
            }
    
    def _extract_blog_content(self, soup: BeautifulSoup) -> str:
        """Extract content from blog posts"""
        # Remove navigation, ads, etc.
        for element in soup(['nav', 'header', 'footer', 'aside', 'script', 'style']):
            element.decompose()
        
        # Find main content areas
        content_selectors = [
            'article', '.post-content', '.entry-content', '.blog-content',
            'main', '.content', '#content'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                return content.get_text(separator=' ', strip=True)
        
        # Fallback to body text
        return soup.get_text(separator=' ', strip=True)
    
    def _extract_forum_content(self, soup: BeautifulSoup) -> str:
        """Extract content from forum posts"""
        # Find forum posts
        posts = soup.find_all(['div', 'article'], class_=re.compile(r'post|message|comment'))
        
        if posts:
            content = ' '.join([post.get_text(separator=' ', strip=True) for post in posts])
            return content
        
        return soup.get_text(separator=' ', strip=True)

class Web3DataTool(BaseTool):
    name: str = "web3_data_fetch"
    description: str = "Fetch Web3 protocol data and statistics"
    args_schema: type = Web3DataInput
    
    async def _arun(self, protocol: str, metric: str, timeframe: str = "30d") -> Dict[str, Any]:
        """Fetch Web3 protocol data"""
        try:
            # Define API endpoints for different protocols
            api_endpoints = {
                "defillama": "https://api.llama.fi",
                "coingecko": "https://api.coingecko.com/api/v3",
                "etherscan": "https://api.etherscan.io/api"
            }
            
            # Fetch data based on protocol and metric
            if protocol.lower() in ["ethereum", "eth"]:
                data = await self._fetch_ethereum_data(metric, timeframe)
            elif protocol.lower() in ["uniswap", "uni"]:
                data = await self._fetch_uniswap_data(metric, timeframe)
            elif protocol.lower() in ["aave", "lending"]:
                data = await self._fetch_aave_data(metric, timeframe)
            else:
                data = await self._fetch_generic_defi_data(protocol, metric, timeframe)
            
            return {
                "protocol": protocol,
                "metric": metric,
                "timeframe": timeframe,
                "data": data,
                "fetched_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "protocol": protocol,
                "metric": metric,
                "status": "failed",
                "error": str(e)
            }
    
    async def _fetch_ethereum_data(self, metric: str, timeframe: str) -> Dict[str, Any]:
        """Fetch Ethereum data"""
        async with aiohttp.ClientSession() as session:
            # Example: Fetch ETH price and market data
            url = f"https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "price_usd": data.get("ethereum", {}).get("usd"),
                        "market_cap": data.get("ethereum", {}).get("usd_market_cap"),
                        "volume_24h": data.get("ethereum", {}).get("usd_24h_vol"),
                        "change_24h": data.get("ethereum", {}).get("usd_24h_change")
                    }
                else:
                    return {"error": f"Failed to fetch Ethereum data: {response.status}"}
    
    async def _fetch_uniswap_data(self, metric: str, timeframe: str) -> Dict[str, Any]:
        """Fetch Uniswap data"""
        async with aiohttp.ClientSession() as session:
            # Example: Fetch Uniswap TVL and volume
            url = "https://api.llama.fi/protocol/uniswap"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "tvl": data.get("tvl", []),
                        "volume_24h": data.get("volume24h"),
                        "total_volume": data.get("totalVolume"),
                        "protocols": data.get("protocols", [])
                    }
                else:
                    return {"error": f"Failed to fetch Uniswap data: {response.status}"}
    
    async def _fetch_aave_data(self, metric: str, timeframe: str) -> Dict[str, Any]:
        """Fetch Aave data"""
        async with aiohttp.ClientSession() as session:
            # Example: Fetch Aave lending data
            url = "https://api.llama.fi/protocol/aave"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "tvl": data.get("tvl", []),
                        "borrowed": data.get("borrowed"),
                        "supplied": data.get("supplied"),
                        "apy": data.get("apy", {})
                    }
                else:
                    return {"error": f"Failed to fetch Aave data: {response.status}"}
    
    async def _fetch_generic_defi_data(self, protocol: str, metric: str, timeframe: str) -> Dict[str, Any]:
        """Fetch generic DeFi protocol data"""
        async with aiohttp.ClientSession() as session:
            url = f"https://api.llama.fi/protocol/{protocol.lower()}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "tvl": data.get("tvl", []),
                        "volume": data.get("volume24h"),
                        "protocol_info": data
                    }
                else:
                    return {"error": f"Failed to fetch {protocol} data: {response.status}"}

class QualitativeAnalysisTool(BaseTool):
    name: str = "qualitative_analysis"
    description: str = "Perform qualitative analysis on scraped content"
    args_schema: type = QualitativeAnalysisInput
    
    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def _arun(self, sources: List[str], research_domain: str, analysis_type: str = "thematic") -> Dict[str, Any]:
        """Perform qualitative analysis"""
        try:
            # Combine all sources
            combined_content = " ".join(sources)
            
            # Create analysis prompt based on type
            if analysis_type == "thematic":
                prompt = self._create_thematic_analysis_prompt(combined_content, research_domain)
            elif analysis_type == "sentiment":
                prompt = self._create_sentiment_analysis_prompt(combined_content, research_domain)
            elif analysis_type == "discourse":
                prompt = self._create_discourse_analysis_prompt(combined_content, research_domain)
            else:
                prompt = self._create_thematic_analysis_prompt(combined_content, research_domain)
            
            # Perform analysis using LLM
            response = await self.llm.ainvoke(prompt)
            
            # Parse response
            try:
                analysis_result = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback to structured text
                analysis_result = {
                    "themes": [],
                    "insights": response.content,
                    "analysis_type": analysis_type,
                    "research_domain": research_domain
                }
            
            return {
                "analysis_type": analysis_type,
                "research_domain": research_domain,
                "sources_analyzed": len(sources),
                "word_count": len(combined_content.split()),
                "results": analysis_result,
                "analyzed_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "analysis_type": analysis_type,
                "research_domain": research_domain,
                "status": "failed",
                "error": str(e)
            }
    
    def _create_thematic_analysis_prompt(self, content: str, research_domain: str) -> str:
        """Create prompt for thematic analysis"""
        return f"""
        Perform thematic analysis on the following content related to {research_domain}:
        
        Content: {content[:2000]}...
        
        Analyze the content and identify:
        1. Key themes and patterns
        2. Recurring topics and concepts
        3. Stakeholder perspectives
        4. Emerging trends
        5. Research implications
        
        Format your response as JSON with the following structure:
        {{
            "themes": [
                {{
                    "theme": "theme_name",
                    "description": "theme_description",
                    "frequency": "high/medium/low",
                    "examples": ["example1", "example2"],
                    "implications": "research_implications"
                }}
            ],
            "patterns": [
                {{
                    "pattern": "pattern_description",
                    "significance": "pattern_significance",
                    "evidence": ["evidence1", "evidence2"]
                }}
            ],
            "stakeholder_perspectives": [
                {{
                    "stakeholder": "stakeholder_type",
                    "perspective": "perspective_description",
                    "key_concerns": ["concern1", "concern2"]
                }}
            ],
            "trends": [
                {{
                    "trend": "trend_description",
                    "direction": "increasing/decreasing/stable",
                    "evidence": "supporting_evidence"
                }}
            ],
            "research_implications": [
                "implication1",
                "implication2",
                "implication3"
            ]
        }}
        """
    
    def _create_sentiment_analysis_prompt(self, content: str, research_domain: str) -> str:
        """Create prompt for sentiment analysis"""
        return f"""
        Perform sentiment analysis on the following content related to {research_domain}:
        
        Content: {content[:2000]}...
        
        Analyze the sentiment and emotional tone of the content, focusing on:
        1. Overall sentiment (positive/negative/neutral)
        2. Emotional intensity
        3. Sentiment variations across topics
        4. Stakeholder sentiment differences
        
        Format as JSON with sentiment scores and analysis.
        """
    
    def _create_discourse_analysis_prompt(self, content: str, research_domain: str) -> str:
        """Create prompt for discourse analysis"""
        return f"""
        Perform discourse analysis on the following content related to {research_domain}:
        
        Content: {content[:2000]}...
        
        Analyze the discourse patterns, focusing on:
        1. Language use and terminology
        2. Argument structures
        3. Power dynamics in discourse
        4. Discursive frames and narratives
        
        Format as JSON with discourse analysis results.
        """

class QuantitativeAnalysisTool(BaseTool):
    name: str = "quantitative_analysis"
    description: str = "Perform quantitative analysis on Web3 data"
    args_schema: type = QuantitativeAnalysisInput
    
    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def _arun(self, data_sources: List[str], metrics: List[str], analysis_type: str = "descriptive") -> Dict[str, Any]:
        """Perform quantitative analysis"""
        try:
            # Parse and prepare data
            data = []
            for source in data_sources:
                try:
                    if isinstance(source, str):
                        source_data = json.loads(source)
                    else:
                        source_data = source
                    data.append(source_data)
                except (json.JSONDecodeError, TypeError):
                    continue
            
            # Perform analysis based on type
            if analysis_type == "descriptive":
                results = self._perform_descriptive_analysis(data, metrics)
            elif analysis_type == "correlation":
                results = self._perform_correlation_analysis(data, metrics)
            elif analysis_type == "regression":
                results = self._perform_regression_analysis(data, metrics)
            else:
                results = self._perform_descriptive_analysis(data, metrics)
            
            # Generate visualizations
            visualizations = await self._generate_visualizations(data, metrics)
            
            return {
                "analysis_type": analysis_type,
                "metrics_analyzed": metrics,
                "data_sources": len(data_sources),
                "results": results,
                "visualizations": visualizations,
                "analyzed_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "analysis_type": analysis_type,
                "metrics_analyzed": metrics,
                "status": "failed",
                "error": str(e)
            }
    
    def _perform_descriptive_analysis(self, data: List[Dict], metrics: List[str]) -> Dict[str, Any]:
        """Perform descriptive statistical analysis"""
        results = {}
        
        for metric in metrics:
            values = []
            for item in data:
                if metric in item:
                    try:
                        value = float(item[metric])
                        values.append(value)
                    except (ValueError, TypeError):
                        continue
            
            if values:
                results[metric] = {
                    "count": len(values),
                    "mean": np.mean(values),
                    "median": np.median(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "quartiles": np.percentile(values, [25, 50, 75]).tolist()
                }
            else:
                results[metric] = {"error": "No valid data found"}
        
        return results
    
    def _perform_correlation_analysis(self, data: List[Dict], metrics: List[str]) -> Dict[str, Any]:
        """Perform correlation analysis"""
        if len(metrics) < 2:
            return {"error": "Need at least 2 metrics for correlation analysis"}
        
        # Create data matrix
        matrix_data = {}
        for metric in metrics:
            values = []
            for item in data:
                if metric in item:
                    try:
                        value = float(item[metric])
                        values.append(value)
                    except (ValueError, TypeError):
                        values.append(np.nan)
            matrix_data[metric] = values
        
        # Calculate correlations
        correlations = {}
        for i, metric1 in enumerate(metrics):
            for j, metric2 in enumerate(metrics):
                if i < j:  # Avoid duplicate calculations
                    corr = np.corrcoef(matrix_data[metric1], matrix_data[metric2])[0, 1]
                    correlations[f"{metric1}_vs_{metric2}"] = {
                        "correlation": float(corr) if not np.isnan(corr) else None,
                        "strength": self._interpret_correlation(corr) if not np.isnan(corr) else "invalid"
                    }
        
        return correlations
    
    def _perform_regression_analysis(self, data: List[Dict], metrics: List[str]) -> Dict[str, Any]:
        """Perform simple regression analysis"""
        if len(metrics) < 2:
            return {"error": "Need at least 2 metrics for regression analysis"}
        
        # Use first metric as dependent variable, others as independent
        dependent = metrics[0]
        independent = metrics[1]
        
        x_values = []
        y_values = []
        
        for item in data:
            if dependent in item and independent in item:
                try:
                    x = float(item[independent])
                    y = float(item[dependent])
                    x_values.append(x)
                    y_values.append(y)
                except (ValueError, TypeError):
                    continue
        
        if len(x_values) > 1:
            # Simple linear regression
            slope, intercept, r_value, p_value, std_err = np.polyfit(x_values, y_values, 1, full=True)
            
            return {
                "dependent_variable": dependent,
                "independent_variable": independent,
                "slope": float(slope[0]),
                "intercept": float(intercept),
                "r_squared": float(r_value[0]**2),
                "p_value": float(p_value[0]) if len(p_value) > 0 else None,
                "std_error": float(std_err[0]) if len(std_err) > 0 else None,
                "sample_size": len(x_values)
            }
        else:
            return {"error": "Insufficient data for regression analysis"}
    
    def _interpret_correlation(self, corr: float) -> str:
        """Interpret correlation coefficient"""
        if abs(corr) >= 0.7:
            return "strong"
        elif abs(corr) >= 0.3:
            return "moderate"
        else:
            return "weak"
    
    async def _generate_visualizations(self, data: List[Dict], metrics: List[str]) -> List[Dict[str, Any]]:
        """Generate data visualizations"""
        visualizations = []
        
        try:
            # Create time series plot if time data is available
            if any("timestamp" in item or "date" in item for item in data):
                # Time series visualization
                pass
            
            # Create correlation heatmap
            if len(metrics) > 1:
                # Correlation heatmap
                pass
            
            # Create distribution plots
            for metric in metrics:
                values = []
                for item in data:
                    if metric in item:
                        try:
                            value = float(item[metric])
                            values.append(value)
                        except (ValueError, TypeError):
                            continue
                
                if values:
                    # Distribution plot
                    pass
            
        except Exception as e:
            visualizations.append({"error": f"Visualization failed: {str(e)}"})
        
        return visualizations

class ResultsIntegrationTool(BaseTool):
    name: str = "results_integration"
    description: str = "Integrate qualitative and quantitative analysis results"
    args_schema: type = ResultsIntegrationInput
    
    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def _arun(self, qualitative_results: Dict[str, Any], quantitative_results: Dict[str, Any], research_questions: List[str]) -> Dict[str, Any]:
        """Integrate qualitative and quantitative results"""
        try:
            # Create integration prompt
            prompt = f"""
            Integrate the following qualitative and quantitative analysis results to answer the research questions:
            
            Research Questions: {research_questions}
            
            Qualitative Results: {json.dumps(qualitative_results, indent=2)}
            
            Quantitative Results: {json.dumps(quantitative_results, indent=2)}
            
            Provide an integrated analysis that:
            1. Synthesizes qualitative themes with quantitative patterns
            2. Identifies convergent and divergent findings
            3. Addresses each research question with evidence from both analyses
            4. Highlights key insights and implications
            5. Suggests areas for further research
            
            Format as JSON with the following structure:
            {{
                "integrated_findings": [
                    {{
                        "research_question": "question",
                        "qualitative_evidence": ["evidence1", "evidence2"],
                        "quantitative_evidence": ["evidence1", "evidence2"],
                        "integrated_insight": "synthesized_insight",
                        "confidence": "high/medium/low"
                    }}
                ],
                "convergent_findings": [
                    {{
                        "finding": "finding_description",
                        "qualitative_support": "qualitative_evidence",
                        "quantitative_support": "quantitative_evidence"
                    }}
                ],
                "divergent_findings": [
                    {{
                        "finding": "finding_description",
                        "qualitative_perspective": "qualitative_view",
                        "quantitative_perspective": "quantitative_view",
                        "possible_explanation": "explanation"
                    }}
                ],
                "key_insights": [
                    "insight1",
                    "insight2",
                    "insight3"
                ],
                "research_implications": [
                    "implication1",
                    "implication2",
                    "implication3"
                ],
                "future_research_directions": [
                    "direction1",
                    "direction2",
                    "direction3"
                ]
            }}
            """
            
            # Generate integrated analysis
            response = await self.llm.ainvoke(prompt)
            
            # Parse response
            try:
                integration_result = json.loads(response.content)
            except json.JSONDecodeError:
                integration_result = {
                    "integrated_findings": [],
                    "convergent_findings": [],
                    "divergent_findings": [],
                    "key_insights": [response.content],
                    "research_implications": [],
                    "future_research_directions": []
                }
            
            return {
                "research_questions": research_questions,
                "qualitative_results_summary": self._summarize_results(qualitative_results),
                "quantitative_results_summary": self._summarize_results(quantitative_results),
                "integrated_analysis": integration_result,
                "integration_method": "LLM-based synthesis",
                "integrated_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "research_questions": research_questions,
                "status": "failed",
                "error": str(e)
            }
    
    def _summarize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of analysis results"""
        if "error" in results:
            return {"status": "error", "error": results["error"]}
        
        summary = {
            "analysis_type": results.get("analysis_type", "unknown"),
            "data_sources": results.get("data_sources", results.get("sources_analyzed", 0)),
            "key_metrics": list(results.get("results", {}).keys()) if isinstance(results.get("results"), dict) else [],
            "status": results.get("status", "unknown")
        }
        
        return summary

# --- Standalone Tool Functions ---

async def web_scraping(url: str, content_type: str = "blog", max_pages: int = 5) -> Dict[str, Any]:
    """Scrape content from web sources"""
    tool = WebScrapingTool()
    return await tool._arun(url, content_type, max_pages)

async def web3_data_fetch(protocol: str, metric: str, timeframe: str = "30d") -> Dict[str, Any]:
    """Fetch Web3 protocol data"""
    tool = Web3DataTool()
    return await tool._arun(protocol, metric, timeframe)

async def qualitative_analysis(sources: List[str], research_domain: str, analysis_type: str = "thematic") -> Dict[str, Any]:
    """Perform qualitative analysis"""
    tool = QualitativeAnalysisTool()
    return await tool._arun(sources, research_domain, analysis_type)

async def quantitative_analysis(data_sources: List[str], metrics: List[str], analysis_type: str = "descriptive") -> Dict[str, Any]:
    """Perform quantitative analysis"""
    tool = QuantitativeAnalysisTool()
    return await tool._arun(data_sources, metrics, analysis_type)

async def results_integration(qualitative_results: Dict[str, Any], quantitative_results: Dict[str, Any], research_questions: List[str]) -> Dict[str, Any]:
    """Integrate analysis results"""
    tool = ResultsIntegrationTool()
    return await tool._arun(qualitative_results, quantitative_results, research_questions)

# --- Agent Definition ---

class AnalysisAgent(BaseResearchAgent):
    """Analysis Agent for qualitative and quantitative research analysis"""
    
    def __init__(self):
        super().__init__("analysis_agent")
        
        # Add analysis tools
        self.add_tool(WebScrapingTool())
        self.add_tool(Web3DataTool())
        self.add_tool(QualitativeAnalysisTool())
        self.add_tool(QuantitativeAnalysisTool())
        self.add_tool(ResultsIntegrationTool())
    
    def _add_agent_tools(self) -> None:
        """Add analysis-specific tools"""
        # Tools are added in __init__ for this agent
        pass
    
    def _get_system_prompt(self) -> str:
        """Get analysis agent system prompt"""
        return """You are an Analysis Agent specialized in research data analysis. Your role is to:

1. Perform qualitative analysis on web-scraped content (blogs, forums, social media)
2. Conduct quantitative analysis on Web3 protocol data and statistics
3. Integrate qualitative and quantitative findings
4. Generate insights and visualizations
5. Provide data-driven recommendations

You have access to:
- Web scraping tools for qualitative data collection
- Web3 data fetching tools for quantitative data
- Qualitative analysis tools for pattern identification
- Quantitative analysis tools for statistical processing
- Results integration tools for synthesis
- Visualization generation capabilities

Always ensure methodological rigor, proper data interpretation, and clear communication of findings."""

    def _prepare_agent_input(self, state: ResearchState, task: ResearchTask) -> str:
        """Prepare input for the analysis agent"""
        parameters = task.parameters
        
        if task.phase == ResearchPhase.QUALITATIVE_ANALYSIS:
            return f"""Perform qualitative analysis for the research project:

Research Domain: {state.research_domain}
Project Title: {state.title}
Project Description: {state.description}

Analysis Parameters:
- Analysis Type: {parameters.get('analysis_type', 'thematic')}
- Sources: {parameters.get('sources', ['blogs', 'forums', 'social_media'])}
- Research Questions: {state.research_questions.primary_question if state.research_questions else 'Not specified'}

Please:
1. Scrape relevant content from blogs, forums, and social media
2. Perform {parameters.get('analysis_type', 'thematic')} analysis
3. Identify key themes, patterns, and insights
4. Relate findings to the research questions
5. Provide structured analysis results

Focus on relevance to the research domain and ensure comprehensive coverage."""

        elif task.phase == ResearchPhase.QUANTITATIVE_ANALYSIS:
            return f"""Perform quantitative analysis for the research project:

Research Domain: {state.research_domain}
Project Title: {state.title}
Project Description: {state.description}

Analysis Parameters:
- Analysis Type: {parameters.get('analysis_type', 'descriptive')}
- Protocols: {parameters.get('protocols', ['ethereum', 'uniswap', 'aave'])}
- Metrics: {parameters.get('metrics', ['TVL', 'volume', 'users'])}
- Timeframe: {parameters.get('timeframe', '30d')}

Please:
1. Fetch Web3 protocol data for specified metrics
2. Perform {parameters.get('analysis_type', 'descriptive')} statistical analysis
3. Generate visualizations and charts
4. Identify trends and patterns in the data
5. Provide statistical insights and interpretations

Ensure data quality, proper statistical methods, and clear visualization."""

        else:  # RESULTS_INTEGRATION
            return f"""Integrate qualitative and quantitative analysis results:

Research Domain: {state.research_domain}
Project Title: {state.title}
Project Description: {state.description}

Research Questions: {state.research_questions.primary_question if state.research_questions else 'Not specified'}

Please:
1. Combine qualitative and quantitative findings
2. Identify synergies and contradictions between analyses
3. Generate integrated insights and recommendations
4. Address research questions with combined evidence
5. Provide comprehensive analysis summary

Ensure logical integration, clear synthesis, and actionable recommendations."""

    def _process_agent_result(self, result: Dict[str, Any], state: ResearchState, task: ResearchTask) -> Dict[str, Any]:
        """Process the agent's result"""
        try:
            # Extract content from LangChain result
            content = result.get("output", result.get("content", ""))
            
            # Try to parse structured content
            structured_result = self._parse_structured_content(content)
            
            # Add metadata
            structured_result.update({
                "task_id": task.id,
                "agent_type": "analysis_agent",
                "phase": task.phase.value,
                "execution_time": task.execution_time,
                "generated_at": datetime.utcnow().isoformat()
            })
            
            return structured_result
            
        except Exception as e:
            return {
                "error": f"Failed to process agent result: {str(e)}",
                "raw_result": result
            }
    
    def _parse_structured_content(self, content: str) -> Dict[str, Any]:
        """Parse structured content from agent output"""
        try:
            # Try to extract JSON from the content
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback to extracting sections
        return {
            "analysis_summary": content[:500] + "..." if len(content) > 500 else content,
            "status": "completed"
        }

    async def execute_task(self, state: ResearchState, task: ResearchTask) -> Dict[str, Any]:
        """Execute analysis task"""
        try:
            # Prepare input
            agent_input = self._prepare_agent_input(state, task)
            
            # Run agent
            result = await self.agent_executor.ainvoke({
                "input": agent_input,
                "chat_history": []
            })
            
            # Process result
            processed_result = self._process_agent_result(result, state, task)
            
            # Update state
            self._update_state_with_result(state, processed_result, task)
            
            return processed_result
            
        except Exception as e:
            error_msg = f"Analysis task failed: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    def _update_state_with_result(self, state: ResearchState, result: Dict[str, Any], task: ResearchTask) -> None:
        """Update state with analysis result"""
        from ..core.research_state import ResearchResults
        
        if "error" not in result:
            # Update based on phase
            if task.phase == ResearchPhase.QUALITATIVE_ANALYSIS:
                if not state.results:
                    state.results = ResearchResults()
                state.results.qualitative_data = result
            
            elif task.phase == ResearchPhase.QUANTITATIVE_ANALYSIS:
                if not state.results:
                    state.results = ResearchResults()
                state.results.quantitative_data = result
            
            elif task.phase == ResearchPhase.RESULTS_INTEGRATION:
                if not state.results:
                    state.results = ResearchResults()
                state.results.analysis_results = result.get("integrated_results", {})
                state.results.interpretations = result.get("interpretations", {})
                state.results.visualizations = result.get("visualizations", [])
            
            self.logger.info(f"Analysis completed for phase: {task.phase.value}")
    
    def _prepare_feedback_input(self, state: ResearchState, task: ResearchTask, feedback: Dict[str, Any]) -> str:
        """Prepare input for feedback processing"""
        current_results = ""
        if state.results:
            if task.phase == ResearchPhase.QUALITATIVE_ANALYSIS:
                current_results = f"Qualitative data: {len(state.results.qualitative_data)} items"
            elif task.phase == ResearchPhase.QUANTITATIVE_ANALYSIS:
                current_results = f"Quantitative data: {len(state.results.quantitative_data)} items"
            elif task.phase == ResearchPhase.RESULTS_INTEGRATION:
                current_results = f"Integrated results: {len(state.results.analysis_results)} insights"
        
        return f"""
        Process human feedback for analysis:
        
        Original Task: {task.description}
        Current Results: {current_results}
        
        Human Feedback:
        Type: {feedback.get('feedback_type', '')}
        Content: {feedback.get('content', '')}
        Specific Changes: {feedback.get('specific_changes', [])}
        
        Please revise the analysis based on this feedback and provide an updated version.
        """ 