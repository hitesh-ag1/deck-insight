# supervisor/models.py

from typing import TypedDict, List, Optional, Dict
from pydantic import BaseModel, Field

# Import relevant models from other agents
from agents.pitch_deck.models import (
    CompanyOverview,
    FounderMarketFit,
    MarketSizingGrowth,
    Traction,
    ScoringResponse,
    Slide,
    SlideContent
)
from agents.market_size.models import (
    SectorInfo,
    MarketSizeInfo,
    CompetitorInfo
)
from agents.github_repo.models import ExtractSchema

class PitchDeckAnalysis(BaseModel):
    """Pitch deck analysis results"""
    company_overview: Optional[CompanyOverview] = Field(default=None)
    founder_market_fit: Optional[FounderMarketFit] = Field(default=None)
    market_sizing: Optional[MarketSizingGrowth] = Field(default=None)
    traction: Optional[Traction] = Field(default=None)
    slide_content: Optional[List[SlideContent]] = Field(default=None)

class MarketAnalysis(BaseModel):
    """Market analysis results"""
    sector: Optional[SectorInfo] = Field(default=None)
    market_size: Optional[MarketSizeInfo] = Field(default=None)
    competitors: Optional[List[CompetitorInfo]] = Field(default=None)

class GitHubAnalysis(BaseModel):
    """GitHub repository analysis results"""
    repositories: Optional[List[ExtractSchema]] = Field(default=None)

class SupervisorResponse(BaseModel):
    """Complete analysis response"""
    pitch_deck_summary: Optional[PitchDeckAnalysis] = Field(
        default=None,
        description="Complete pitch deck analysis"
    )
    pitch_deck_scorecard: Optional[List[ScoringResponse]] = Field(
        default=None,
        description="Scorecard for the pitch deck"
    )
    market_analysis: Optional[MarketAnalysis] = Field(
        default=None,
        description="Market research results"
    )
    github_analysis: Optional[GitHubAnalysis] = Field(
        default=None,
        description="GitHub repository analysis"
    )
    is_tech_company: bool = Field(
        default=False,
        description="Whether the company is a tech/SaaS company"
    )

class GraphState(TypedDict):
    """State management for the supervisor agent"""
    # Input data
    slides: List[Slide]
    
    # Pitch deck analysis results
    summary: Optional[Dict]
    scorecard: Optional[List[Dict]]
    slide_content: Optional[List[SlideContent]]
    
    # Market analysis results
    market_analysis: Optional[Dict]
    sector: Optional[SectorInfo]
    market_size: Optional[MarketSizeInfo]
    competitors: Optional[List[CompetitorInfo]]
    
    # GitHub analysis results
    github_url: Optional[str]
    github_details: Optional[List[ExtractSchema]]
    
    # Status flags
    is_tech_company: bool
    error: Optional[str]

class SupervisorState(TypedDict):
    """Complete state including all analyses"""
    input_state: GraphState
    pitch_deck_analysis: Optional[PitchDeckAnalysis]
    market_analysis: Optional[MarketAnalysis]
    github_analysis: Optional[GitHubAnalysis]
    is_tech_company: bool
    error: Optional[str]

