import asyncio
import re
import json
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import httpx
from app.services.logging_service import LoggingService

class AliExpressService:
    """알리익스프레스 웹 스크래핑 서비스"""
    
    def __init__(self):
        self.base_url = "https://www.aliexpress.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def search_products(self, keyword: str, category: str = "Home & Garden", 
                            min_orders: int = 100, max_price: Optional[float] = None,
                            page: int = 1, limit: int = 20) -> List[Dict]:
        """알리익스프레스에서 제품 검색"""
        try:
            # Build search URL
            search_url = f"{self.base_url}/wholesale"
            params = {
                'SearchText': keyword,
                'catId': self._get_category_id(category),
                'minOrder': min_orders,
                'page': page
            }
            
            if max_price:
                params['maxPrice'] = max_price
            
            # Use Playwright for dynamic content
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page_obj = await browser.new_page()
                
                # Set user agent
                await page_obj.set_extra_http_headers(self.headers)
                
                # Navigate to search page
                await page_obj.goto(f"{search_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}")
                
                # Wait for products to load
                await page_obj.wait_for_selector('[data-product-id]', timeout=10000)
                
                # Extract product data
                products = await page_obj.evaluate("""
                    () => {
                        const products = [];
                        const productElements = document.querySelectorAll('[data-product-id]');
                        
                        productElements.forEach((element, index) => {
                            if (index >= 20) return; // Limit to 20 products
                            
                            const productId = element.getAttribute('data-product-id');
                            const titleElement = element.querySelector('.product-title');
                            const priceElement = element.querySelector('.product-price');
                            const imageElement = element.querySelector('img');
                            const ordersElement = element.querySelector('.product-orders');
                            
                            if (productId && titleElement) {
                                products.push({
                                    id: productId,
                                    title: titleElement.textContent.trim(),
                                    price: priceElement ? priceElement.textContent.trim() : '',
                                    image_url: imageElement ? imageElement.src : '',
                                    orders: ordersElement ? ordersElement.textContent.trim() : '',
                                    url: element.href || ''
                                });
                            }
                        });
                        
                        return products;
                    }
                """)
                
                await browser.close()
                
                LoggingService.log_info(f"알리익스프레스 제품 검색 완료: {keyword}, {len(products)}개 결과")
                return products
                
        except Exception as e:
            LoggingService.log_error(f"알리익스프레스 제품 검색 실패: {str(e)}")
            return []
    
    async def get_trending_products(self, category: str = "Home & Garden", limit: int = 20) -> List[Dict]:
        """인기 제품 조회 (판매 주문이 많은 제품)"""
        try:
            # Use trending products page
            trending_url = f"{self.base_url}/wholesale"
            params = {
                'catId': self._get_category_id(category),
                'sortType': 'total_tranpro_desc',  # Sort by sales
                'page': 1
            }
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page_obj = await browser.new_page()
                
                await page_obj.set_extra_http_headers(self.headers)
                await page_obj.goto(f"{trending_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}")
                
                # Wait for products to load
                await page_obj.wait_for_selector('[data-product-id]', timeout=10000)
                
                # Extract trending products
                products = await page_obj.evaluate(f"""
                    () => {{
                        const products = [];
                        const productElements = document.querySelectorAll('[data-product-id]');
                        
                        productElements.forEach((element, index) => {{
                            if (index >= {limit}) return;
                            
                            const productId = element.getAttribute('data-product-id');
                            const titleElement = element.querySelector('.product-title');
                            const priceElement = element.querySelector('.product-price');
                            const imageElement = element.querySelector('img');
                            const ordersElement = element.querySelector('.product-orders');
                            const ratingElement = element.querySelector('.product-rating');
                            
                            if (productId && titleElement) {{
                                products.push({{
                                    id: productId,
                                    title: titleElement.textContent.trim(),
                                    price: priceElement ? priceElement.textContent.trim() : '',
                                    image_url: imageElement ? imageElement.src : '',
                                    orders: ordersElement ? ordersElement.textContent.trim() : '',
                                    rating: ratingElement ? ratingElement.textContent.trim() : '',
                                    url: element.href || '',
                                    is_trending: true
                                }});
                            }}
                        }});
                        
                        return products;
                    }}
                """)
                
                await browser.close()
                
                LoggingService.log_info(f"알리익스프레스 인기 제품 조회 완료: {category}, {len(products)}개 결과")
                return products
                
        except Exception as e:
            LoggingService.log_error(f"알리익스프레스 인기 제품 조회 실패: {str(e)}")
            return []
    
    async def get_product_detail(self, product_id: str) -> Optional[Dict]:
        """제품 상세 정보 조회"""
        try:
            product_url = f"{self.base_url}/item/{product_id}.html"
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page_obj = await browser.new_page()
                
                await page_obj.set_extra_http_headers(self.headers)
                await page_obj.goto(product_url)
                
                # Wait for product details to load
                await page_obj.wait_for_selector('.product-title', timeout=10000)
                
                # Extract detailed product information
                product_detail = await page_obj.evaluate("""
                    () => {
                        const titleElement = document.querySelector('.product-title');
                        const priceElement = document.querySelector('.product-price-current');
                        const descriptionElement = document.querySelector('.product-description');
                        const images = Array.from(document.querySelectorAll('.product-image img')).map(img => img.src);
                        const variants = Array.from(document.querySelectorAll('.product-variant')).map(variant => ({
                            name: variant.querySelector('.variant-name')?.textContent.trim(),
                            price: variant.querySelector('.variant-price')?.textContent.trim()
                        }));
                        const shippingElement = document.querySelector('.shipping-info');
                        const ratingElement = document.querySelector('.product-rating');
                        const reviewsElement = document.querySelector('.product-reviews-count');
                        
                        return {
                            id: window.location.pathname.split('/').pop().replace('.html', ''),
                            title: titleElement ? titleElement.textContent.trim() : '',
                            price: priceElement ? priceElement.textContent.trim() : '',
                            description: descriptionElement ? descriptionElement.textContent.trim() : '',
                            images: images,
                            variants: variants,
                            shipping: shippingElement ? shippingElement.textContent.trim() : '',
                            rating: ratingElement ? ratingElement.textContent.trim() : '',
                            reviews_count: reviewsElement ? reviewsElement.textContent.trim() : '',
                            url: window.location.href
                        };
                    }
                """)
                
                await browser.close()
                
                LoggingService.log_info(f"알리익스프레스 제품 상세 조회 완료: {product_id}")
                return product_detail
                
        except Exception as e:
            LoggingService.log_error(f"알리익스프레스 제품 상세 조회 실패: {product_id}, 오류: {str(e)}")
            return None
    
    def transform_to_shopify_format(self, aliexpress_product: Dict) -> Dict:
        """알리익스프레스 제품 데이터를 Shopify 형식으로 변환"""
        try:
            # Extract price (remove currency symbols and convert to float)
            price_str = aliexpress_product.get('price', '0')
            price = self._extract_price(price_str)
            
            # Calculate markup price (example: 50% markup)
            markup_price = price * 1.5 if price > 0 else 0
            
            # Create Shopify product data
            shopify_product = {
                "title": aliexpress_product.get('title', ''),
                "description": aliexpress_product.get('description', ''),
                "price": markup_price,
                "compare_at_price": price,  # Original price as compare price
                "vendor": "AliExpress Import",
                "product_type": "General",
                "tags": "aliexpress,import",
                "image_url": aliexpress_product.get('images', [None])[0] if aliexpress_product.get('images') else None,
                "images": aliexpress_product.get('images', []),
                "inventory_quantity": 100,  # Default inventory
                "inventory_management": "shopify",
                "status": "active"
            }
            
            # Add variants if available
            if aliexpress_product.get('variants'):
                shopify_product['variants'] = []
                for variant in aliexpress_product['variants']:
                    variant_price = self._extract_price(variant.get('price', '0'))
                    shopify_product['variants'].append({
                        "title": variant.get('name', 'Default'),
                        "price": variant_price * 1.5,
                        "compare_at_price": variant_price,
                        "inventory_quantity": 50
                    })
            
            return shopify_product
            
        except Exception as e:
            LoggingService.log_error(f"제품 데이터 변환 실패: {str(e)}")
            return {}
    
    def _get_category_id(self, category: str) -> str:
        """카테고리명을 알리익스프레스 카테고리 ID로 변환"""
        category_mapping = {
            "Home & Garden": "15",
            "Electronics": "1",
            "Fashion": "3",
            "Sports & Entertainment": "18",
            "Automotive": "26",
            "Beauty & Health": "66",
            "Toys & Hobbies": "7",
            "Tools & Hardware": "13"
        }
        return category_mapping.get(category, "15")  # Default to Home & Garden
    
    def _extract_price(self, price_str: str) -> float:
        """가격 문자열에서 숫자 추출"""
        try:
            # Remove currency symbols and non-numeric characters except decimal point
            price_clean = re.sub(r'[^\d.]', '', price_str)
            return float(price_clean) if price_clean else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    async def check_us_shipping(self, product_id: str) -> bool:
        """US 배송 가능 여부 확인"""
        try:
            product_detail = await self.get_product_detail(product_id)
            if not product_detail:
                return False
            
            shipping_info = product_detail.get('shipping', '').lower()
            
            # Check for US shipping indicators
            us_shipping_indicators = [
                'free shipping to us',
                'ships to us',
                'us shipping',
                'united states',
                'usa'
            ]
            
            return any(indicator in shipping_info for indicator in us_shipping_indicators)
            
        except Exception as e:
            LoggingService.log_error(f"US 배송 확인 실패: {product_id}, 오류: {str(e)}")
            return False
    
    async def get_product_analytics(self, product_id: str) -> Dict:
        """제품 분석 정보 조회"""
        try:
            product_detail = await self.get_product_detail(product_id)
            if not product_detail:
                return {}
            
            # Extract analytics data
            orders_str = product_detail.get('orders', '0')
            orders = self._extract_number(orders_str)
            
            rating_str = product_detail.get('rating', '0')
            rating = self._extract_rating(rating_str)
            
            reviews_str = product_detail.get('reviews_count', '0')
            reviews = self._extract_number(reviews_str)
            
            return {
                "product_id": product_id,
                "orders": orders,
                "rating": rating,
                "reviews_count": reviews,
                "popularity_score": orders * rating if rating > 0 else 0,
                "has_us_shipping": await self.check_us_shipping(product_id)
            }
            
        except Exception as e:
            LoggingService.log_error(f"제품 분석 조회 실패: {product_id}, 오류: {str(e)}")
            return {}
    
    def _extract_number(self, text: str) -> int:
        """텍스트에서 숫자 추출"""
        try:
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else 0
        except (ValueError, IndexError):
            return 0
    
    def _extract_rating(self, rating_str: str) -> float:
        """평점 추출"""
        try:
            # Look for rating pattern like "4.5/5" or "4.5"
            rating_match = re.search(r'(\d+\.?\d*)', rating_str)
            if rating_match:
                rating = float(rating_match.group(1))
                # If rating is out of 5, normalize to 5
                if rating > 5:
                    rating = rating / 10
                return rating
            return 0.0
        except (ValueError, TypeError):
            return 0.0
