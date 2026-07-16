from sqlalchemy import Column, Integer, Float, Date, String
from .database import Base


class TrainingSession(Base):
    """
    one row = one run.

    load gets calculated as duration_min * rpe (session-RPE / Foster's
    method) -- picked this because it just needs duration and how hard
    it felt, no GPS or heart-rate data needed.
    """
    __tablename__ = "training_sessions"

    # Primary key for standard database row lookup.
    id = Column(Integer, primary_key=True, index=True)
    
    # We index the date because almost every query we do (sorting, rolling ACWR windows,
    # and date filtering) relies heavily on date order.
    date = Column(Date, nullable=False, index=True)
    
    # Optional bc sometimes GPS watches die or we run on a treadmill with broken calibration,
    # but we can still calculate training load as long as we have time and RPE!
    distance_mi = Column(Float, nullable=True)
    
    duration_min = Column(Float, nullable=False)
    rpe = Column(Float, nullable=False)  # 1-10, how hard the run felt
    
    # Pre-calculated in the backend before saving. Storing this directly saves us from
    # having to do math on the fly every single time we pull a training load series.
    load = Column(Float, nullable=False)
    
    # Good for tracking context like "legs heavy :/", "ran in the rain", etc.
    notes = Column(String, nullable=True)