from sqlalchemy import Column, String, Text, JSON, Integer
from app.models.base import BaseModel

class Log(BaseModel):
    """로그 모델"""
    __tablename__ = "logs"
    
    level = Column(String, nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    module = Column(String)  # Which module generated the log
    function = Column(String)  # Which function generated the log
    user_id = Column(Integer)  # Associated user if applicable
    product_id = Column(Integer)  # Associated product if applicable
    
    # Additional context
    context = Column(JSON)  # Store additional context as JSON
    traceback = Column(Text)  # For error logs
    
    # Request info
    ip_address = Column(String)
    user_agent = Column(String)
    request_path = Column(String)
    request_method = Column(String)
