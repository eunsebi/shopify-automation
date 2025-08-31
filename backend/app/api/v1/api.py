from fastapi import APIRouter
from app.api.v1.endpoints import products, users, logs, aliexpress, sns

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(aliexpress.router, prefix="/aliexpress", tags=["aliexpress"])
api_router.include_router(sns.router, prefix="/sns", tags=["sns"])
