from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.product import Product
from app.services.shopify_service import ShopifyService
from app.services.logging_service import LoggingService

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """제품 목록 조회 (페이지네이션 지원)"""
    try:
        offset = (page - 1) * limit
        query = db.query(Product)
        
        if search:
            query = query.filter(Product.title.contains(search))
        
        products = query.offset(offset).limit(limit).all()
        
        # Convert to dict for response
        result = []
        for product in products:
            result.append({
                "id": product.id,
                "shopify_id": product.shopify_id,
                "title": product.title,
                "price": product.price,
                "image_url": product.image_url,
                "status": product.status,
                "created_at": product.created_at,
                "updated_at": product.updated_at
            })
        
        return result
    except Exception as e:
        LoggingService.log_error(f"제품 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="제품 목록 조회 중 오류가 발생했습니다.")

@router.get("/{product_id}", response_model=dict)
async def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db)
):
    """제품 상세 정보 조회"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")
        
        return {
            "id": product.id,
            "shopify_id": product.shopify_id,
            "title": product.title,
            "description": product.description,
            "price": product.price,
            "compare_at_price": product.compare_at_price,
            "vendor": product.vendor,
            "product_type": product.product_type,
            "tags": product.tags,
            "status": product.status,
            "meta_title": product.meta_title,
            "meta_description": product.meta_description,
            "image_url": product.image_url,
            "images": product.images,
            "inventory_quantity": product.inventory_quantity,
            "variants": product.variants,
            "handle": product.handle,
            "import_source": product.import_source,
            "source_url": product.source_url,
            "created_at": product.created_at,
            "updated_at": product.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        LoggingService.log_error(f"제품 상세 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="제품 상세 조회 중 오류가 발생했습니다.")

@router.put("/{product_id}")
async def update_product(
    product_id: int,
    product_data: dict,
    db: Session = Depends(get_db)
):
    """제품 정보 수정"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")
        
        # Update fields
        for field, value in product_data.items():
            if hasattr(product, field):
                setattr(product, field, value)
        
        db.commit()
        LoggingService.log_info(f"제품 수정 완료: {product_id}")
        
        return {"message": "제품이 성공적으로 수정되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        LoggingService.log_error(f"제품 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="제품 수정 중 오류가 발생했습니다.")

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """제품 삭제"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")
        
        db.delete(product)
        db.commit()
        LoggingService.log_info(f"제품 삭제 완료: {product_id}")
        
        return {"message": "제품이 성공적으로 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        LoggingService.log_error(f"제품 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="제품 삭제 중 오류가 발생했습니다.")

@router.post("/sync-shopify")
async def sync_shopify_products(db: Session = Depends(get_db)):
    """Shopify에서 제품 동기화"""
    try:
        shopify_service = ShopifyService()
        products = await shopify_service.get_products()
        
        # Sync products to database
        for product_data in products:
            existing_product = db.query(Product).filter(
                Product.shopify_id == product_data.get("id")
            ).first()
            
            if existing_product:
                # Update existing product
                for field, value in product_data.items():
                    if hasattr(existing_product, field):
                        setattr(existing_product, field, value)
            else:
                # Create new product
                new_product = Product(**product_data)
                db.add(new_product)
        
        db.commit()
        LoggingService.log_info(f"Shopify 제품 동기화 완료: {len(products)}개 제품")
        
        return {"message": f"{len(products)}개의 제품이 동기화되었습니다."}
    except Exception as e:
        db.rollback()
        LoggingService.log_error(f"Shopify 제품 동기화 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="제품 동기화 중 오류가 발생했습니다.")
