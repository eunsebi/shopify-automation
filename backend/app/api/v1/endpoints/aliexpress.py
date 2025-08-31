from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.aliexpress_service import AliExpressService
from app.services.shopify_service import ShopifyService
from app.services.logging_service import LoggingService
from app.models.product import Product

router = APIRouter()

@router.get("/search")
async def search_aliexpress_products(
    keyword: str = Query(..., description="검색할 제품 키워드"),
    category: str = Query("Home & Garden", description="카테고리"),
    min_orders: int = Query(100, description="최소 주문 수"),
    max_price: Optional[float] = Query(None, description="최대 가격"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """알리익스프레스에서 제품 검색"""
    try:
        aliexpress_service = AliExpressService()
        products = await aliexpress_service.search_products(
            keyword=keyword,
            category=category,
            min_orders=min_orders,
            max_price=max_price,
            page=page,
            limit=limit
        )
        
        LoggingService.log_info(f"알리익스프레스 제품 검색 완료: {keyword}, {len(products)}개 결과")
        
        return {
            "products": products,
            "total": len(products),
            "page": page,
            "limit": limit
        }
    except Exception as e:
        LoggingService.log_error(f"알리익스프레스 제품 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="제품 검색 중 오류가 발생했습니다.")

@router.get("/trending")
async def get_trending_products(
    category: str = Query("Home & Garden", description="카테고리"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """인기 제품 조회 (판매 주문이 많은 제품)"""
    try:
        aliexpress_service = AliExpressService()
        trending_products = await aliexpress_service.get_trending_products(
            category=category,
            limit=limit
        )
        
        LoggingService.log_info(f"인기 제품 조회 완료: {category}, {len(trending_products)}개 결과")
        
        return {
            "products": trending_products,
            "category": category,
            "total": len(trending_products)
        }
    except Exception as e:
        LoggingService.log_error(f"인기 제품 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="인기 제품 조회 중 오류가 발생했습니다.")

@router.get("/product/{product_id}")
async def get_aliexpress_product_detail(
    product_id: str,
    db: Session = Depends(get_db)
):
    """알리익스프레스 제품 상세 정보 조회"""
    try:
        aliexpress_service = AliExpressService()
        product_detail = await aliexpress_service.get_product_detail(product_id)
        
        LoggingService.log_info(f"알리익스프레스 제품 상세 조회 완료: {product_id}")
        
        return product_detail
    except Exception as e:
        LoggingService.log_error(f"알리익스프레스 제품 상세 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="제품 상세 조회 중 오류가 발생했습니다.")

@router.post("/import")
async def import_aliexpress_product(
    product_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """알리익스프레스 제품을 Shopify에 임포트"""
    try:
        # Check if product already exists
        existing_product = db.query(Product).filter(
            Product.source_url.contains(product_id)
        ).first()
        
        if existing_product:
            raise HTTPException(status_code=400, detail="이미 임포트된 제품입니다.")
        
        # Add background task for import
        background_tasks.add_task(
            import_product_to_shopify,
            product_id=product_id,
            db=db
        )
        
        LoggingService.log_info(f"알리익스프레스 제품 임포트 시작: {product_id}")
        
        return {
            "message": "제품 임포트가 시작되었습니다. 백그라운드에서 처리 중입니다.",
            "product_id": product_id,
            "status": "processing"
        }
    except HTTPException:
        raise
    except Exception as e:
        LoggingService.log_error(f"알리익스프레스 제품 임포트 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="제품 임포트 중 오류가 발생했습니다.")

@router.post("/import-batch")
async def import_aliexpress_products_batch(
    product_ids: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """여러 알리익스프레스 제품을 일괄 임포트"""
    try:
        # Check for existing products
        existing_products = []
        new_product_ids = []
        
        for product_id in product_ids:
            existing_product = db.query(Product).filter(
                Product.source_url.contains(product_id)
            ).first()
            
            if existing_product:
                existing_products.append(product_id)
            else:
                new_product_ids.append(product_id)
        
        if not new_product_ids:
            raise HTTPException(status_code=400, detail="모든 제품이 이미 임포트되어 있습니다.")
        
        # Add background task for batch import
        background_tasks.add_task(
            import_products_batch_to_shopify,
            product_ids=new_product_ids,
            db=db
        )
        
        LoggingService.log_info(f"알리익스프레스 제품 일괄 임포트 시작: {len(new_product_ids)}개 제품")
        
        return {
            "message": f"{len(new_product_ids)}개 제품의 임포트가 시작되었습니다.",
            "new_products": new_product_ids,
            "existing_products": existing_products,
            "status": "processing"
        }
    except HTTPException:
        raise
    except Exception as e:
        LoggingService.log_error(f"알리익스프레스 제품 일괄 임포트 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="제품 일괄 임포트 중 오류가 발생했습니다.")

@router.get("/import-status")
async def get_import_status(
    db: Session = Depends(get_db)
):
    """임포트 상태 조회"""
    try:
        # Get recently imported products
        recent_imports = db.query(Product).filter(
            Product.import_source == "aliexpress"
        ).order_by(Product.created_at.desc()).limit(10).all()
        
        result = []
        for product in recent_imports:
            result.append({
                "id": product.id,
                "title": product.title,
                "import_source": product.import_source,
                "source_url": product.source_url,
                "status": product.status,
                "created_at": product.created_at.isoformat() if product.created_at else None
            })
        
        return {
            "recent_imports": result,
            "total_imported": db.query(Product).filter(
                Product.import_source == "aliexpress"
            ).count()
        }
    except Exception as e:
        LoggingService.log_error(f"임포트 상태 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="임포트 상태 조회 중 오류가 발생했습니다.")

async def import_product_to_shopify(product_id: str, db: Session):
    """백그라운드에서 제품을 Shopify에 임포트하는 함수"""
    try:
        aliexpress_service = AliExpressService()
        shopify_service = ShopifyService()
        
        # Get product detail from AliExpress
        product_detail = await aliexpress_service.get_product_detail(product_id)
        
        # Transform product data for Shopify
        shopify_product_data = aliexpress_service.transform_to_shopify_format(product_detail)
        
        # Create product in Shopify
        shopify_product = await shopify_service.create_product(shopify_product_data)
        
        # Save to database
        new_product = Product(
            shopify_id=shopify_product.get("id"),
            title=shopify_product_data["title"],
            description=shopify_product_data.get("description"),
            price=shopify_product_data.get("price"),
            vendor=shopify_product_data.get("vendor"),
            product_type=shopify_product_data.get("product_type"),
            image_url=shopify_product_data.get("image_url"),
            images=shopify_product_data.get("images"),
            import_source="aliexpress",
            source_url=product_detail.get("url"),
            source_data=product_detail
        )
        
        db.add(new_product)
        db.commit()
        
        LoggingService.log_info(f"제품 임포트 완료: {product_id} -> Shopify ID: {shopify_product.get('id')}")
        
    except Exception as e:
        LoggingService.log_error(f"제품 임포트 실패: {product_id}, 오류: {str(e)}")
        db.rollback()

async def import_products_batch_to_shopify(product_ids: List[str], db: Session):
    """백그라운드에서 여러 제품을 일괄 임포트하는 함수"""
    for product_id in product_ids:
        try:
            await import_product_to_shopify(product_id, db)
        except Exception as e:
            LoggingService.log_error(f"일괄 임포트 중 제품 실패: {product_id}, 오류: {str(e)}")
            continue
