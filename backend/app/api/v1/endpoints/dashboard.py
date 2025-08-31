from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.models import product, user, log, sns_content
from sqlalchemy import func
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """대시보드 통계 정보 조회"""
    try:
        # 제품 통계
        total_products = db.query(product.Product).count()
        active_products = db.query(product.Product).filter(product.Product.status == "active").count()
        
        # 사용자 통계
        total_users = db.query(user.User).count()
        active_users = db.query(user.User).filter(user.User.is_active == True).count()
        
        # 로그 통계 (최근 7일)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_logs = db.query(log.Log).filter(log.Log.created_at >= seven_days_ago).count()
        error_logs = db.query(log.Log).filter(
            log.Log.created_at >= seven_days_ago,
            log.Log.level == "ERROR"
        ).count()
        
        # SNS 콘텐츠 통계
        total_sns_content = db.query(sns_content.SNSContent).count()
        published_sns_content = db.query(sns_content.SNSContent).filter(
            sns_content.SNSContent.is_published == True
        ).count()
        
        # 최근 30일 제품 등록 추이
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_products = db.query(
            func.date(product.Product.created_at).label('date'),
            func.count(product.Product.id).label('count')
        ).filter(
            product.Product.created_at >= thirty_days_ago
        ).group_by(
            func.date(product.Product.created_at)
        ).all()
        
        # 최근 활동
        recent_activities = db.query(log.Log).order_by(
            log.Log.created_at.desc()
        ).limit(10).all()
        
        return {
            "overview": {
                "total_products": total_products,
                "active_products": active_products,
                "total_users": total_users,
                "active_users": active_users,
                "recent_logs": recent_logs,
                "error_logs": error_logs,
                "total_sns_content": total_sns_content,
                "published_sns_content": published_sns_content
            },
            "product_trends": [
                {
                    "date": str(item.date),
                    "count": item.count
                } for item in recent_products
            ],
            "recent_activities": [
                {
                    "id": item.id,
                    "level": item.level,
                    "message": item.message,
                    "created_at": item.created_at.isoformat()
                } for item in recent_activities
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대시보드 통계 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/sales")
async def get_sales_data(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """매출 데이터 조회 (더미 데이터)"""
    try:
        # 더미 매출 데이터
        sales_data = [
            {"date": "2024-01-01", "sales": 1200},
            {"date": "2024-01-02", "sales": 1500},
            {"date": "2024-01-03", "sales": 1800},
            {"date": "2024-01-04", "sales": 2100},
            {"date": "2024-01-05", "sales": 1900},
            {"date": "2024-01-06", "sales": 2200},
            {"date": "2024-01-07", "sales": 2500},
        ]
        
        return {
            "sales_data": sales_data,
            "total_sales": sum(item["sales"] for item in sales_data),
            "average_daily_sales": sum(item["sales"] for item in sales_data) / len(sales_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매출 데이터 조회 중 오류가 발생했습니다: {str(e)}")
