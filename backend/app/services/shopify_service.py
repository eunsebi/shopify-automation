import httpx
from typing import List, Dict, Optional
from app.core.config import settings
from app.services.logging_service import LoggingService

class ShopifyService:
    """Shopify API 연동 서비스"""
    
    def __init__(self):
        """Shopify API 초기화"""
        self.shop_url = settings.SHOPIFY_SHOP_URL
        self.access_token = settings.SHOPIFY_ACCESS_TOKEN
        self.api_version = settings.SHOPIFY_API_VERSION
        
        if not self.shop_url or not self.access_token:
            raise ValueError("Shopify 설정이 올바르지 않습니다. SHOPIFY_SHOP_URL과 SHOPIFY_ACCESS_TOKEN을 확인해주세요.")
    
    async def get_products(self, limit: int = 250) -> List[Dict]:
        """Shopify에서 제품 목록 조회"""
        try:
            products = []
            page_info = None
            
            while True:
                # Build query parameters
                params = {'limit': limit}
                if page_info:
                    params['page_info'] = page_info
                
                # Make API request
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"https://{self.shop_url}/admin/api/{self.api_version}/products.json",
                        headers={'X-Shopify-Access-Token': self.access_token},
                        params=params
                    )
                    response.raise_for_status()
                    data = response.json()
                
                # Extract products
                products.extend(data.get('products', []))
                
                # Check for next page
                link_header = response.headers.get('Link', '')
                if 'rel="next"' not in link_header:
                    break
                
                # Extract page_info from Link header
                import re
                match = re.search(r'page_info=([^&>]+)', link_header)
                if match:
                    page_info = match.group(1)
                else:
                    break
            
            LoggingService.log_info(f"Shopify에서 {len(products)}개 제품 조회 완료")
            return products
            
        except Exception as e:
            LoggingService.log_error(f"Shopify 제품 조회 실패: {str(e)}")
            raise
    
    async def get_product(self, product_id: str) -> Optional[Dict]:
        """특정 제품 조회"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://{self.shop_url}/admin/api/{self.api_version}/products/{product_id}.json",
                    headers={'X-Shopify-Access-Token': self.access_token}
                )
                response.raise_for_status()
                data = response.json()
                
                LoggingService.log_info(f"Shopify 제품 조회 완료: {product_id}")
                return data.get('product')
                
        except Exception as e:
            LoggingService.log_error(f"Shopify 제품 조회 실패: {product_id}, 오류: {str(e)}")
            return None
    
    async def create_product(self, product_data: Dict) -> Dict:
        """새 제품 생성"""
        try:
            # Prepare product data for Shopify
            shopify_product = {
                "product": {
                    "title": product_data.get("title"),
                    "body_html": product_data.get("description", ""),
                    "vendor": product_data.get("vendor", "Default Vendor"),
                    "product_type": product_data.get("product_type", "General"),
                    "tags": product_data.get("tags", ""),
                    "status": "active",
                    "variants": [
                        {
                            "price": str(product_data.get("price", "0.00")),
                            "compare_at_price": str(product_data.get("compare_at_price", "0.00")),
                            "inventory_quantity": product_data.get("inventory_quantity", 0),
                            "inventory_management": "shopify"
                        }
                    ]
                }
            }
            
            # Add images if available
            if product_data.get("image_url"):
                shopify_product["product"]["images"] = [
                    {"src": product_data["image_url"]}
                ]
            
            # Create product via API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://{self.shop_url}/admin/api/{self.api_version}/products.json",
                    headers={
                        'X-Shopify-Access-Token': self.access_token,
                        'Content-Type': 'application/json'
                    },
                    json=shopify_product
                )
                response.raise_for_status()
                data = response.json()
                
                LoggingService.log_info(f"Shopify 제품 생성 완료: {data['product']['id']}")
                return data['product']
                
        except Exception as e:
            LoggingService.log_error(f"Shopify 제품 생성 실패: {str(e)}")
            raise
    
    async def update_product(self, product_id: str, product_data: Dict) -> Dict:
        """제품 정보 수정"""
        try:
            # Prepare update data
            update_data = {"product": {}}
            
            # Add fields that are provided
            if "title" in product_data:
                update_data["product"]["title"] = product_data["title"]
            if "description" in product_data:
                update_data["product"]["body_html"] = product_data["description"]
            if "vendor" in product_data:
                update_data["product"]["vendor"] = product_data["vendor"]
            if "product_type" in product_data:
                update_data["product"]["product_type"] = product_data["product_type"]
            if "tags" in product_data:
                update_data["product"]["tags"] = product_data["tags"]
            if "status" in product_data:
                update_data["product"]["status"] = product_data["status"]
            
            # Update via API
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"https://{self.shop_url}/admin/api/{self.api_version}/products/{product_id}.json",
                    headers={
                        'X-Shopify-Access-Token': self.access_token,
                        'Content-Type': 'application/json'
                    },
                    json=update_data
                )
                response.raise_for_status()
                data = response.json()
                
                LoggingService.log_info(f"Shopify 제품 수정 완료: {product_id}")
                return data['product']
                
        except Exception as e:
            LoggingService.log_error(f"Shopify 제품 수정 실패: {product_id}, 오류: {str(e)}")
            raise
    
    async def delete_product(self, product_id: str) -> bool:
        """제품 삭제"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"https://{self.shop_url}/admin/api/{self.api_version}/products/{product_id}.json",
                    headers={'X-Shopify-Access-Token': self.access_token}
                )
                response.raise_for_status()
                
                LoggingService.log_info(f"Shopify 제품 삭제 완료: {product_id}")
                return True
                
        except Exception as e:
            LoggingService.log_error(f"Shopify 제품 삭제 실패: {product_id}, 오류: {str(e)}")
            return False
    
    async def get_orders(self, limit: int = 50) -> List[Dict]:
        """주문 목록 조회"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://{self.shop_url}/admin/api/{self.api_version}/orders.json",
                    headers={'X-Shopify-Access-Token': self.access_token},
                    params={'limit': limit, 'status': 'any'}
                )
                response.raise_for_status()
                data = response.json()
                
                LoggingService.log_info(f"Shopify 주문 조회 완료: {len(data.get('orders', []))}개")
                return data.get('orders', [])
                
        except Exception as e:
            LoggingService.log_error(f"Shopify 주문 조회 실패: {str(e)}")
            return []
    
    async def get_shop_info(self) -> Dict:
        """쇼핑몰 정보 조회"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://{self.shop_url}/admin/api/{self.api_version}/shop.json",
                    headers={'X-Shopify-Access-Token': self.access_token}
                )
                response.raise_for_status()
                data = response.json()
                
                LoggingService.log_info(f"Shopify 쇼핑몰 정보 조회 완료")
                return data.get('shop', {})
                
        except Exception as e:
            LoggingService.log_error(f"Shopify 쇼핑몰 정보 조회 실패: {str(e)}")
            return {}
    
    async def test_connection(self) -> bool:
        """Shopify API 연결 테스트"""
        try:
            shop_info = await self.get_shop_info()
            return bool(shop_info.get('id'))
        except Exception as e:
            LoggingService.log_error(f"Shopify 연결 테스트 실패: {str(e)}")
            return False
