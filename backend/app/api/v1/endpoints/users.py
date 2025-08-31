from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.services.logging_service import LoggingService
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/", response_model=List[dict])
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """사용자 목록 조회"""
    try:
        offset = (page - 1) * limit
        query = db.query(User)
        
        if search:
            query = query.filter(
                User.username.contains(search) | 
                User.email.contains(search) |
                User.full_name.contains(search)
            )
        
        users = query.offset(offset).limit(limit).all()
        
        result = []
        for user in users:
            result.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "last_login": user.last_login,
                "created_at": user.created_at
            })
        
        return result
    except Exception as e:
        LoggingService.log_error(f"사용자 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="사용자 목록 조회 중 오류가 발생했습니다.")

@router.post("/", response_model=dict)
async def create_user(
    user_data: dict,
    db: Session = Depends(get_db)
):
    """새 사용자 등록"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user_data["username"]) | 
            (User.email == user_data["email"])
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="이미 존재하는 사용자명 또는 이메일입니다.")
        
        # Hash password
        hashed_password = pwd_context.hash(user_data["password"])
        
        # Create new user
        new_user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
            full_name=user_data.get("full_name"),
            phone=user_data.get("phone"),
            address=user_data.get("address"),
            company=user_data.get("company")
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        LoggingService.log_info(f"새 사용자 등록 완료: {new_user.username}")
        
        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "message": "사용자가 성공적으로 등록되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        LoggingService.log_error(f"사용자 등록 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="사용자 등록 중 오류가 발생했습니다.")

@router.get("/{user_id}", response_model=dict)
async def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db)
):
    """사용자 상세 정보 조회"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "last_login": user.last_login,
            "phone": user.phone,
            "address": user.address,
            "company": user.company,
            "preferences": user.preferences,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        LoggingService.log_error(f"사용자 상세 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="사용자 상세 조회 중 오류가 발생했습니다.")

@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_data: dict,
    db: Session = Depends(get_db)
):
    """사용자 정보 수정"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        # Update fields
        for field, value in user_data.items():
            if field == "password" and value:
                # Hash new password
                user.hashed_password = pwd_context.hash(value)
            elif hasattr(user, field) and field != "hashed_password":
                setattr(user, field, value)
        
        db.commit()
        LoggingService.log_info(f"사용자 정보 수정 완료: {user_id}")
        
        return {"message": "사용자 정보가 성공적으로 수정되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        LoggingService.log_error(f"사용자 정보 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="사용자 정보 수정 중 오류가 발생했습니다.")

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """사용자 삭제"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        db.delete(user)
        db.commit()
        LoggingService.log_info(f"사용자 삭제 완료: {user_id}")
        
        return {"message": "사용자가 성공적으로 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        LoggingService.log_error(f"사용자 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="사용자 삭제 중 오류가 발생했습니다.")

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """사용자 활성화"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        user.is_active = True
        db.commit()
        LoggingService.log_info(f"사용자 활성화 완료: {user_id}")
        
        return {"message": "사용자가 활성화되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        LoggingService.log_error(f"사용자 활성화 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="사용자 활성화 중 오류가 발생했습니다.")

@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """사용자 비활성화"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        user.is_active = False
        db.commit()
        LoggingService.log_info(f"사용자 비활성화 완료: {user_id}")
        
        return {"message": "사용자가 비활성화되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        LoggingService.log_error(f"사용자 비활성화 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="사용자 비활성화 중 오류가 발생했습니다.")
