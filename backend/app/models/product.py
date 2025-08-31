from sqlalchemy import Column, String, Text, Float, Boolean, JSON, Integer
from app.models.base import BaseModel

class Product(BaseModel):
    """제품 모델"""
    __tablename__ = "products"
    
    shopify_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float)
    compare_at_price = Column(Float)
    vendor = Column(String)
    product_type = Column(String)
    tags = Column(String)
    status = Column(String, default="active")
    published_at = Column(String)
    
    # SEO fields
    meta_title = Column(String)
    meta_description = Column(Text)
    
    # Images
    image_url = Column(String)
    images = Column(JSON)  # Store multiple images as JSON
    
    # Inventory
    inventory_quantity = Column(Integer, default=0)
    inventory_management = Column(String)
    
    # Variants
    variants = Column(JSON)  # Store variants as JSON
    
    # Additional fields
    handle = Column(String, unique=True)
    template_suffix = Column(String)
    published_scope = Column(String)
    
    # Import source
    import_source = Column(String)  # "aliexpress", "manual", etc.
    source_url = Column(String)
    source_data = Column(JSON)  # Store original source data
