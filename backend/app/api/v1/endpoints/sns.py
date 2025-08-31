from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.sns_content import SNSContent
from app.models.product import Product
from app.services.openai_service import OpenAIService
from app.services.logging_service import LoggingService

router = APIRouter()

@router.get("/content/{product_id}")
async def get_sns_content(
    product_id: int,
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """제품별 SNS 콘텐츠 조회"""
    try:
        query = db.query(SNSContent).filter(SNSContent.product_id == product_id)
        
        if platform:
            query = query.filter(SNSContent.platform == platform)
        
        sns_contents = query.all()
        
        result = []
        for content in sns_contents:
            result.append({
                "id": content.id,
                "platform": content.platform,
                "content_type": content.content_type,
                "title": content.title,
                "description": content.description,
                "hashtags": content.hashtags,
                "image_urls": content.image_urls,
                "generated_content": content.generated_content,
                "generated_hashtags": content.generated_hashtags,
                "is_published": content.is_published,
                "published_at": content.published_at.isoformat() if content.published_at else None,
                "published_url": content.published_url,
                "likes": content.likes,
                "comments": content.comments,
                "shares": content.shares,
                "views": content.views,
                "created_at": content.created_at.isoformat() if content.created_at else None
            })
        
        return result
    except Exception as e:
        LoggingService.log_error(f"SNS 콘텐츠 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="SNS 콘텐츠 조회 중 오류가 발생했습니다.")

@router.post("/generate/{product_id}")
async def generate_sns_content(
    product_id: int,
    platform: str,
    content_type: str = "post",
    db: Session = Depends(get_db)
):
    """AI를 사용하여 SNS 콘텐츠 생성"""
    try:
        # Get product information
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")
        
        # Generate content using OpenAI
        openai_service = OpenAIService()
        
        prompt = f"""
        제품 정보:
        - 제품명: {product.title}
        - 설명: {product.description}
        - 가격: ${product.price}
        - 카테고리: {product.product_type}
        
        {platform}용 {content_type} 콘텐츠를 생성해주세요.
        다음을 포함해주세요:
        1. 매력적인 제목
        2. 제품을 홍보하는 설명
        3. 관련 해시태그 (최대 20개)
        4. 고객이 행동하도록 유도하는 문구
        
        한국어로 작성해주세요.
        """
        
        generated_content = await openai_service.generate_content(prompt)
        
        # Parse generated content
        lines = generated_content.split('\n')
        title = ""
        description = ""
        hashtags = ""
        
        for line in lines:
            if line.strip().startswith('제목:') or line.strip().startswith('Title:'):
                title = line.split(':', 1)[1].strip()
            elif line.strip().startswith('설명:') or line.strip().startswith('Description:'):
                description = line.split(':', 1)[1].strip()
            elif '#' in line:
                hashtags = line.strip()
        
        # Save to database
        sns_content = SNSContent(
            product_id=product_id,
            platform=platform,
            content_type=content_type,
            title=title,
            description=description,
            hashtags=hashtags,
            generated_content=generated_content,
            image_urls=[product.image_url] if product.image_url else []
        )
        
        db.add(sns_content)
        db.commit()
        db.refresh(sns_content)
        
        LoggingService.log_info(f"SNS 콘텐츠 생성 완료: 제품 {product_id}, 플랫폼 {platform}")
        
        return {
            "id": sns_content.id,
            "platform": sns_content.platform,
            "content_type": sns_content.content_type,
            "title": sns_content.title,
            "description": sns_content.description,
            "hashtags": sns_content.hashtags,
            "generated_content": sns_content.generated_content,
            "message": "SNS 콘텐츠가 성공적으로 생성되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        LoggingService.log_error(f"SNS 콘텐츠 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="SNS 콘텐츠 생성 중 오류가 발생했습니다.")

@router.put("/content/{content_id}")
async def update_sns_content(
    content_id: int,
    content_data: dict,
    db: Session = Depends(get_db)
):
    """SNS 콘텐츠 수정"""
    try:
        sns_content = db.query(SNSContent).filter(SNSContent.id == content_id).first()
        if not sns_content:
            raise HTTPException(status_code=404, detail="SNS 콘텐츠를 찾을 수 없습니다.")
        
        # Update fields
        for field, value in content_data.items():
            if hasattr(sns_content, field):
                setattr(sns_content, field, value)
        
        db.commit()
        LoggingService.log_info(f"SNS 콘텐츠 수정 완료: {content_id}")
        
        return {"message": "SNS 콘텐츠가 성공적으로 수정되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        LoggingService.log_error(f"SNS 콘텐츠 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="SNS 콘텐츠 수정 중 오류가 발생했습니다.")

@router.post("/content/{content_id}/regenerate")
async def regenerate_sns_content(
    content_id: int,
    db: Session = Depends(get_db)
):
    """SNS 콘텐츠 재생성"""
    try:
        sns_content = db.query(SNSContent).filter(SNSContent.id == content_id).first()
        if not sns_content:
            raise HTTPException(status_code=404, detail="SNS 콘텐츠를 찾을 수 없습니다.")
        
        # Get product information
        product = db.query(Product).filter(Product.id == sns_content.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")
        
        # Regenerate content using OpenAI
        openai_service = OpenAIService()
        
        prompt = f"""
        제품 정보:
        - 제품명: {product.title}
        - 설명: {product.description}
        - 가격: ${product.price}
        - 카테고리: {product.product_type}
        
        {sns_content.platform}용 {sns_content.content_type} 콘텐츠를 다시 생성해주세요.
        이전 콘텐츠와 다른 스타일로 작성해주세요.
        
        다음을 포함해주세요:
        1. 매력적인 제목
        2. 제품을 홍보하는 설명
        3. 관련 해시태그 (최대 20개)
        4. 고객이 행동하도록 유도하는 문구
        
        한국어로 작성해주세요.
        """
        
        generated_content = await openai_service.generate_content(prompt)
        
        # Parse generated content
        lines = generated_content.split('\n')
        title = ""
        description = ""
        hashtags = ""
        
        for line in lines:
            if line.strip().startswith('제목:') or line.strip().startswith('Title:'):
                title = line.split(':', 1)[1].strip()
            elif line.strip().startswith('설명:') or line.strip().startswith('Description:'):
                description = line.split(':', 1)[1].strip()
            elif '#' in line:
                hashtags = line.strip()
        
        # Update content
        sns_content.title = title
        sns_content.description = description
        sns_content.hashtags = hashtags
        sns_content.generated_content = generated_content
        
        db.commit()
        
        LoggingService.log_info(f"SNS 콘텐츠 재생성 완료: {content_id}")
        
        return {
            "title": sns_content.title,
            "description": sns_content.description,
            "hashtags": sns_content.hashtags,
            "generated_content": sns_content.generated_content,
            "message": "SNS 콘텐츠가 성공적으로 재생성되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        LoggingService.log_error(f"SNS 콘텐츠 재생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="SNS 콘텐츠 재생성 중 오류가 발생했습니다.")

@router.get("/platforms")
async def get_supported_platforms():
    """지원되는 SNS 플랫폼 목록"""
    return {
        "platforms": [
            {
                "name": "instagram",
                "display_name": "Instagram",
                "content_types": ["post", "story", "reel"],
                "description": "사진과 비디오 공유 플랫폼"
            },
            {
                "name": "tiktok",
                "display_name": "TikTok",
                "content_types": ["video", "duet"],
                "description": "짧은 비디오 공유 플랫폼"
            },
            {
                "name": "pinterest",
                "display_name": "Pinterest",
                "content_types": ["pin", "board"],
                "description": "이미지 기반 소셜 미디어"
            },
            {
                "name": "facebook",
                "display_name": "Facebook",
                "content_types": ["post", "story"],
                "description": "소셜 네트워킹 플랫폼"
            },
            {
                "name": "twitter",
                "display_name": "Twitter",
                "content_types": ["tweet", "thread"],
                "description": "마이크로블로깅 플랫폼"
            }
        ]
    }

@router.get("/analytics")
async def get_sns_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """SNS 콘텐츠 분석"""
    try:
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get SNS contents within date range
        sns_contents = db.query(SNSContent).filter(
            SNSContent.created_at >= start_date,
            SNSContent.created_at <= end_date
        ).all()
        
        # Calculate analytics
        total_content = len(sns_contents)
        published_content = len([c for c in sns_contents if c.is_published])
        
        platform_stats = {}
        total_engagement = 0
        
        for content in sns_contents:
            platform = content.platform
            if platform not in platform_stats:
                platform_stats[platform] = {
                    "total": 0,
                    "published": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "total_shares": 0,
                    "total_views": 0
                }
            
            platform_stats[platform]["total"] += 1
            if content.is_published:
                platform_stats[platform]["published"] += 1
            
            platform_stats[platform]["total_likes"] += content.likes or 0
            platform_stats[platform]["total_comments"] += content.comments or 0
            platform_stats[platform]["total_shares"] += content.shares or 0
            platform_stats[platform]["total_views"] += content.views or 0
            
            total_engagement += (content.likes or 0) + (content.comments or 0) + (content.shares or 0)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "overview": {
                "total_content": total_content,
                "published_content": published_content,
                "publish_rate": (published_content / total_content * 100) if total_content > 0 else 0,
                "total_engagement": total_engagement
            },
            "platform_stats": platform_stats
        }
    except Exception as e:
        LoggingService.log_error(f"SNS 분석 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="SNS 분석 조회 중 오류가 발생했습니다.")
