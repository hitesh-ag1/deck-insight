from typing import TypedDict
from pydantic import BaseModel, Field
from typing import TypedDict, List, Dict, Optional

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

class SectorInfo(TypedDict):
    name: str
    citation: List[str]

class MarketSizeInfo(TypedDict):
    tam: str
    citation: List[str]

class CompetitorInfo(TypedDict):
    name: str
    description: str
    citation: List[str]

class MarketResearchData(TypedDict):
    sector: SectorInfo
    market_size: MarketSizeInfo
    competitors: List[CompetitorInfo]

class GraphState(TypedDict):
    input_overview: CompanyOverview
    sector: Optional[SectorInfo]
    market_size: Optional[MarketSizeInfo]
    competitors: Optional[List[CompetitorInfo]]
    error: Optional[str]

class SectorModel(BaseModel):
    name: str
    citation: List[str]

class MarketSizeModel(BaseModel):
    tam: str
    citation: List[str]

class CompetitorModel(BaseModel):
    name: str
    description: str
    citation: List[str]

class MarketResearchResponse(BaseModel):
    sector: SectorModel
    market_size: MarketSizeModel
    competitors: List[CompetitorModel]
