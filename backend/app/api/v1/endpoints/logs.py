from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.log import Log
from app.services.logging_service import LoggingService

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    level: Optional[str] = None,
    module: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """로그 목록 조회 (실시간 로그 출력용)"""
    try:
        offset = (page - 1) * limit
        query = db.query(Log)
        
        # Filter by level
        if level:
            query = query.filter(Log.level == level.upper())
        
        # Filter by module
        if module:
            query = query.filter(Log.module.contains(module))
        
        # Filter by date range
        if start_date:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Log.created_at >= start_datetime)
        
        if end_date:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Log.created_at <= end_datetime)
        
        # Search in message
        if search:
            query = query.filter(Log.message.contains(search))
        
        # Order by created_at descending (latest first)
        logs = query.order_by(Log.created_at.desc()).offset(offset).limit(limit).all()
        
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "level": log.level,
                "message": log.message,
                "module": log.module,
                "function": log.function,
                "user_id": log.user_id,
                "product_id": log.product_id,
                "ip_address": log.ip_address,
                "request_path": log.request_path,
                "request_method": log.request_method,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        
        return result
    except Exception as e:
        LoggingService.log_error(f"로그 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="로그 목록 조회 중 오류가 발생했습니다.")

@router.get("/realtime")
async def get_realtime_logs(
    last_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """실시간 로그 스트리밍 (WebSocket 대신 polling 방식)"""
    try:
        query = db.query(Log).order_by(Log.created_at.desc())
        
        if last_id:
            query = query.filter(Log.id > last_id)
        
        # Get latest 10 logs
        logs = query.limit(10).all()
        
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "level": log.level,
                "message": log.message,
                "module": log.module,
                "function": log.function,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        
        return {
            "logs": result,
            "latest_id": max([log.id for log in logs]) if logs else last_id
        }
    except Exception as e:
        LoggingService.log_error(f"실시간 로그 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="실시간 로그 조회 중 오류가 발생했습니다.")

@router.get("/stats")
async def get_log_stats(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """로그 통계 정보"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get logs within date range
        logs = db.query(Log).filter(
            Log.created_at >= start_date,
            Log.created_at <= end_date
        ).all()
        
        # Calculate statistics
        total_logs = len(logs)
        level_counts = {}
        module_counts = {}
        
        for log in logs:
            # Count by level
            level_counts[log.level] = level_counts.get(log.level, 0) + 1
            
            # Count by module
            if log.module:
                module_counts[log.module] = module_counts.get(log.module, 0) + 1
        
        # Get error logs
        error_logs = [log for log in logs if log.level == "ERROR"]
        
        return {
            "total_logs": total_logs,
            "error_count": len(error_logs),
            "level_distribution": level_counts,
            "module_distribution": module_counts,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    except Exception as e:
        LoggingService.log_error(f"로그 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="로그 통계 조회 중 오류가 발생했습니다.")

@router.get("/errors")
async def get_error_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """에러 로그만 조회"""
    try:
        offset = (page - 1) * limit
        error_logs = db.query(Log).filter(
            Log.level == "ERROR"
        ).order_by(Log.created_at.desc()).offset(offset).limit(limit).all()
        
        result = []
        for log in error_logs:
            result.append({
                "id": log.id,
                "message": log.message,
                "module": log.module,
                "function": log.function,
                "traceback": log.traceback,
                "ip_address": log.ip_address,
                "request_path": log.request_path,
                "request_method": log.request_method,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        
        return result
    except Exception as e:
        LoggingService.log_error(f"에러 로그 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="에러 로그 조회 중 오류가 발생했습니다.")

@router.delete("/")
async def clear_logs(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """오래된 로그 삭제"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Count logs to be deleted
        count = db.query(Log).filter(Log.created_at < cutoff_date).count()
        
        # Delete old logs
        db.query(Log).filter(Log.created_at < cutoff_date).delete()
        db.commit()
        
        LoggingService.log_info(f"오래된 로그 삭제 완료: {count}개 로그 삭제됨")
        
        return {
            "message": f"{count}개의 오래된 로그가 삭제되었습니다.",
            "deleted_count": count
        }
    except Exception as e:
        db.rollback()
        LoggingService.log_error(f"로그 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="로그 삭제 중 오류가 발생했습니다.")

@router.get("/export")
async def export_logs(
    format: str = Query("json", regex="^(json|csv)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """로그 내보내기"""
    try:
        query = db.query(Log)
        
        # Apply filters
        if start_date:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Log.created_at >= start_datetime)
        
        if end_date:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Log.created_at <= end_datetime)
        
        if level:
            query = query.filter(Log.level == level.upper())
        
        logs = query.order_by(Log.created_at.desc()).all()
        
        if format == "json":
            result = []
            for log in logs:
                result.append({
                    "id": log.id,
                    "level": log.level,
                    "message": log.message,
                    "module": log.module,
                    "function": log.function,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                })
            return {"logs": result}
        
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Level", "Message", "Module", "Function", "Created At"])
            
            for log in logs:
                writer.writerow([
                    log.id,
                    log.level,
                    log.message,
                    log.module,
                    log.function,
                    log.created_at.isoformat() if log.created_at else ""
                ])
            
            return {"csv_data": output.getvalue()}
    
    except Exception as e:
        LoggingService.log_error(f"로그 내보내기 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="로그 내보내기 중 오류가 발생했습니다.")
