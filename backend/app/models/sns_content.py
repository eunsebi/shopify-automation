from sqlalchemy import Column, String, Text, JSON, Integer, Boolean, DateTime
from app.models.base import BaseModel

class SNSContent(BaseModel):
    """SNS 콘텐츠 모델"""
    __tablename__ = "sns_contents"
    
    product_id = Column(Integer, nullable=False)
    platform = Column(String, nullable=False)  # instagram, tiktok, pinterest, etc.
    content_type = Column(String)  # post, story, reel, etc.
    
    # Content
    title = Column(String)
    description = Column(Text)
    hashtags = Column(String)
    image_urls = Column(JSON)  # Multiple images for carousel posts
    
    # Generated content
    generated_content = Column(Text)  # AI generated content
    generated_hashtags = Column(String)  # AI generated hashtags
    
    # Status
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime)
    published_url = Column(String)
    
    # Platform specific settings
    platform_settings = Column(JSON)  # Platform specific settings
    
    # Performance metrics
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
