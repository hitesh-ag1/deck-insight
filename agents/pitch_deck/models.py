from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple, TypedDict

class FounderExperience(BaseModel):
    work_experience: Optional[str] = Field(default=None, alias="Work Experience", description="Work experience of the founder")
    education: Optional[str] = Field(default=None, alias="Education", description="Educational background of the founder")

class MarketMetric(BaseModel):
    value: Optional[str] = Field(default=None, alias="TAM", description="Market size value")  # or SAM/SOM as needed
    explanation: Optional[str] = Field(default=None, alias="Explanation", description="Explanation of the market size calculation")
    source: Optional[str] = Field(default=None, alias="Source", description="Source of the market size data")

class PreRevenue(BaseModel):
    number_of_users: Optional[List[str]] = Field(default=None, alias="Number of Users", description="User growth metrics")
    poc_evaluation: Optional[List[str]] = Field(default=None, alias="POC Evaluation", description="Proof of concept evaluation metrics")
    press_articles: Optional[List[str]] = Field(default=None, alias="Press Articles", description="Press coverage details")
    user_testimonials: Optional[List[str]] = Field(default=None, alias="User Testimonials", description="User testimonials")

class Revenue(BaseModel):
    revenue: Optional[List[str]] = Field(default=None, alias="Revenue", description="Revenue metrics")
    growth_rate: Optional[List[str]] = Field(default=None, alias="Growth Rate", description="Growth rate metrics")
    unit_economics: Optional[List[str]] = Field(default=None, alias="Unit Economics", description="Unit economics metrics")

class CompanyOverview(BaseModel):
    """Response model for company overview details"""
    company_name: Optional[str] = Field(default=None, alias="Company Name", description="Name of the company")
    what_company_does: Optional[str] = Field(default=None, alias="What the Company Does", description="Company description")
    team_size: Optional[str] = Field(default=None, alias="Team Size", description="Size of the team")
    industry: Optional[str] = Field(default=None, alias="Industry", description="Industry category")
    region: Optional[str] = Field(default=None, alias="Region", description="Geographic region")
    funding_stage: Optional[str] = Field(default=None, alias="Funding Stage", description="Current funding stage")
    ask: Optional[str] = Field(default=None, alias="Ask", description="Funding ask amount")
    valuation: Optional[str] = Field(default=None, alias="Valuation", description="Company valuation")
    previous_rounds: Optional[List[Dict[str, str]]] = Field(default=None, alias="Previous Rounds", description="Previous funding rounds")

class FounderMarketFit(BaseModel):
    """Response model for founder market fit details"""
    relevant_experience: Optional[Dict[str, FounderExperience]] = Field(
        default=None, alias="Relevant Experience", description="Relevant experience by founder name"
    )
    domain_expertise: Optional[Dict[str, str]] = Field(
        default=None, alias="Domain Expertise", description="Domain expertise by founder name"
    )

class MarketSizingGrowth(BaseModel):
    """Response model for market sizing growth details"""
    tam: Optional[MarketMetric] = Field(default=None, alias="TAM", description="Total Addressable Market")
    sam: Optional[MarketMetric] = Field(default=None, alias="SAM", description="Serviceable Addressable Market")
    som: Optional[MarketMetric] = Field(default=None, alias="SOM", description="Serviceable Obtainable Market")
    growth_rate: Optional[MarketMetric] = Field(default=None, alias="Growth Rate", description="Market growth rate")
    target_geographies: Optional[List[str]] = Field(default=None, alias="Target Geographies", description="Target geographic markets")

class Traction(BaseModel):
    """Response model for traction details"""
    pre_revenue: Optional[PreRevenue] = Field(default=None, alias="Pre-Revenue", description="Pre-revenue metrics")
    revenue: Optional[Revenue] = Field(default=None, alias="Revenue", description="Revenue metrics")

class Slide(TypedDict):
    imageByte: bytes
    slide_type: Optional[str]
    text: Optional[List[str]]
    images: Optional[List[str]]
    figures: Optional[List[str]]
    market_validation: Optional[str]
    competition_validation: Optional[str]

class SlideContent(TypedDict):
    index: int
    text: Optional[List[str]]
    image: Optional[List[str]]
    figure: Optional[List[str]]

class GraphState(TypedDict):
    slides: List[Slide]
    current_index: int
    summary: Optional[str]
    scorecard: Optional[str]
    slide_content: Optional[List[SlideContent]]

class ProcessSlideResponse(BaseModel):
    """Respond to the user with this"""
    text: List[str] = Field(
        description="The text content of the slide"
    )
    image: List[str] = Field(
        description="The image content of the slide"
    )
    figure: List[str] = Field(
        description="The figure content of the slide"
    )

class ScoringResponse(BaseModel):
    """Respond to the user with this"""
    category: str = Field(
        description="The category of the score (e.g., Team, Market, Traction)"
    )
    score: Optional[int] = Field(
        description="The score given to the startup out of 10"
    )
    justification: str = Field(
        description="Justification for each score"
    )

class ScoringResponseList(BaseModel):
    """Respond to the user with this"""
    scores: List[ScoringResponse] = Field(
        description="List of scores and justifications for each category"
    )
