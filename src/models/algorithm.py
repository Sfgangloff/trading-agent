"""
Algorithm models
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from .base import AlgorithmStatus


class Algorithm(BaseModel):
    """Trading algorithm model"""

    algorithm_id: str = Field(..., description="Unique algorithm identifier")
    name: str = Field(..., description="Human-readable algorithm name")
    description: Optional[str] = Field(None, description="Algorithm description")

    # Code
    code: str = Field(..., description="Python code for the algorithm")
    version: int = Field(default=1, ge=1, description="Algorithm version")

    # Parameters
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Algorithm configuration parameters")

    # Metadata
    status: AlgorithmStatus = Field(default=AlgorithmStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Genealogy (for tracking evolution)
    parent_algorithm_id: Optional[str] = Field(None, description="Parent algorithm if evolved from another")
    generation: int = Field(default=0, ge=0, description="Generation number in evolution")

    # Tags for categorization
    tags: list[str] = Field(default_factory=list, description="Tags for categorization (e.g., 'momentum', 'mean-reversion')")

    class Config:
        json_schema_extra = {
            "example": {
                "algorithm_id": "sma_crossover_v1",
                "name": "Simple Moving Average Crossover",
                "description": "Buys when short-term SMA crosses above long-term SMA",
                "code": "def analyze(data, sentiment): ...",
                "version": 1,
                "parameters": {
                    "short_window": 20,
                    "long_window": 50
                },
                "status": "ACTIVE",
                "created_at": "2025-11-09T10:00:00",
                "updated_at": "2025-11-09T10:00:00",
                "parent_algorithm_id": None,
                "generation": 0,
                "tags": ["technical", "trend-following", "sma"]
            }
        }


class AlgorithmMetadata(BaseModel):
    """Lightweight algorithm metadata (without code)"""

    algorithm_id: str
    name: str
    description: Optional[str] = None
    version: int
    status: AlgorithmStatus
    created_at: datetime
    tags: list[str] = Field(default_factory=list)
