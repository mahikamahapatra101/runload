from datetime import date as date_type
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SessionCreate(BaseModel):
    """what gets sent when I log a run manually"""
    date: date_type
    
    # Enforce basic physical rules: we can't run negative miles (haha)!
    distance_mi: Optional[float] = Field(None, ge=0)
    
    # A run must actually take time (greater than 0 minutes) to be valid.
    duration_min: float = Field(..., gt=0)
    
    # Restrict the Borg RPE scale strictly to 1-10 to prevent bad math in load calculations.
    rpe: float = Field(..., ge=1, le=10)
    
    notes: Optional[str] = None


class SessionOut(BaseModel):
    """what comes back once a session's saved"""
    # Enables Pydantic to read SQLAlchemy model attributes directly (like `db_session.id`)
    # and automatically serialize them to JSON. Formerly called class Config: orm_mode = True.
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date_type
    distance_mi: Optional[float]
    duration_min: float
    rpe: float
    load: float  # Returns the pre-calculated load back to the client
    notes: Optional[str]


class DailyLoadPoint(BaseModel):
    """one day in the load timeline, with ACWR + risk already attached"""
    date: date_type
    daily_load: float
    
    # Made these optional because a user won't have rolling averages for the first
    # few weeks of using the app (we need a warm-up period to compute chronic loads).
    acute_load: Optional[float] = None       # 7-day rolling average
    chronic_load: Optional[float] = None     # 28-day rolling average
    acwr: Optional[float] = None
    risk_level: Optional[str] = None


class CurrentRisk(BaseModel):
    """this is what feeds the risk card on the dashboard"""
    date: Optional[date_type]
    acwr: Optional[float]
    risk_level: str
    recommendation: str
    days_of_data: int
    # A flag to tell the frontend if we have the minimum 28 days of data needed
    # to show an accurate ACWR, or if we are still in the setup phase.
    has_enough_data: bool


class UploadResult(BaseModel):
    # Returns a quick summary of the CSV upload action to show in a toast notification.
    sessions_added: int
    date_range: str