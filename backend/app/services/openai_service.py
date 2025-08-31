import openai
from typing import List, Dict, Optional
from app.core.config import settings
from app.services.logging_service import LoggingService

class OpenAIService:
    """OpenAI API 연동 서비스"""
    
    def __init__(self):
        """OpenAI API 초기화"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다. OPENAI_API_KEY를 확인해주세요.")
        
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_content(self, prompt: str, max_tokens: int = 1000) -> str:
        """텍스트 콘텐츠 생성"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 전문적인 마케팅 콘텐츠 작성자입니다. 한국어로 명확하고 매력적인 콘텐츠를 작성해주세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            LoggingService.log_info(f"OpenAI 콘텐츠 생성 완료: {len(content)}자")
            
            return content
            
        except Exception as e:
            LoggingService.log_error(f"OpenAI 콘텐츠 생성 실패: {str(e)}")
            return "콘텐츠 생성 중 오류가 발생했습니다."
    
    async def generate_sns_content(self, product_info: Dict, platform: str, content_type: str = "post") -> Dict:
        """SNS용 콘텐츠 생성"""
        try:
            prompt = f"""
            제품 정보:
            - 제품명: {product_info.get('title', '')}
            - 설명: {product_info.get('description', '')}
            - 가격: ${product_info.get('price', 0)}
            - 카테고리: {product_info.get('product_type', '')}
            
            {platform}용 {content_type} 콘텐츠를 생성해주세요.
            
            다음 형식으로 응답해주세요:
            
            제목: [매력적인 제목]
            설명: [제품을 홍보하는 설명]
            해시태그: [관련 해시태그들]
            CTA: [고객이 행동하도록 유도하는 문구]
            
            한국어로 작성하고, 각 플랫폼의 특성에 맞게 최적화해주세요.
            """
            
            content = await self.generate_content(prompt)
            
            # Parse the response
            lines = content.split('\n')
            result = {
                "title": "",
                "description": "",
                "hashtags": "",
                "cta": "",
                "full_content": content
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('제목:'):
                    result["title"] = line.replace('제목:', '').strip()
                elif line.startswith('설명:'):
                    result["description"] = line.replace('설명:', '').strip()
                elif line.startswith('해시태그:'):
                    result["hashtags"] = line.replace('해시태그:', '').strip()
                elif line.startswith('CTA:'):
                    result["cta"] = line.replace('CTA:', '').strip()
            
            LoggingService.log_info(f"SNS 콘텐츠 생성 완료: {platform}, {content_type}")
            return result
            
        except Exception as e:
            LoggingService.log_error(f"SNS 콘텐츠 생성 실패: {str(e)}")
            return {
                "title": "제품 제목",
                "description": "제품 설명",
                "hashtags": "#제품 #홍보",
                "cta": "지금 구매하세요!",
                "full_content": "콘텐츠 생성 중 오류가 발생했습니다."
            }
    
    async def generate_product_description(self, product_info: Dict) -> str:
        """제품 설명 생성"""
        try:
            prompt = f"""
            다음 제품 정보를 바탕으로 매력적인 제품 설명을 작성해주세요:
            
            제품명: {product_info.get('title', '')}
            원본 설명: {product_info.get('description', '')}
            가격: ${product_info.get('price', 0)}
            카테고리: {product_info.get('product_type', '')}
            
            다음을 포함한 전문적인 제품 설명을 작성해주세요:
            1. 제품의 주요 특징과 장점
            2. 사용 방법이나 활용법
            3. 고객이 구매해야 하는 이유
            4. 품질 보증이나 서비스 내용
            
            한국어로 작성하고, HTML 태그를 사용하여 구조화해주세요.
            """
            
            description = await self.generate_content(prompt, max_tokens=800)
            LoggingService.log_info(f"제품 설명 생성 완료")
            
            return description
            
        except Exception as e:
            LoggingService.log_error(f"제품 설명 생성 실패: {str(e)}")
            return product_info.get('description', '제품 설명을 생성할 수 없습니다.')
    
    async def generate_seo_content(self, product_info: Dict) -> Dict:
        """SEO 최적화 콘텐츠 생성"""
        try:
            prompt = f"""
            다음 제품 정보를 바탕으로 SEO 최적화된 메타 정보를 생성해주세요:
            
            제품명: {product_info.get('title', '')}
            설명: {product_info.get('description', '')}
            카테고리: {product_info.get('product_type', '')}
            
            다음 형식으로 응답해주세요:
            
            메타 타이틀: [SEO 최적화된 제목, 50-60자]
            메타 설명: [SEO 최적화된 설명, 150-160자]
            키워드: [주요 키워드들, 쉼표로 구분]
            
            검색 엔진 최적화를 고려하여 작성해주세요.
            """
            
            content = await self.generate_content(prompt)
            
            # Parse the response
            lines = content.split('\n')
            result = {
                "meta_title": "",
                "meta_description": "",
                "keywords": ""
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('메타 타이틀:'):
                    result["meta_title"] = line.replace('메타 타이틀:', '').strip()
                elif line.startswith('메타 설명:'):
                    result["meta_description"] = line.replace('메타 설명:', '').strip()
                elif line.startswith('키워드:'):
                    result["keywords"] = line.replace('키워드:', '').strip()
            
            LoggingService.log_info(f"SEO 콘텐츠 생성 완료")
            return result
            
        except Exception as e:
            LoggingService.log_error(f"SEO 콘텐츠 생성 실패: {str(e)}")
            return {
                "meta_title": product_info.get('title', ''),
                "meta_description": product_info.get('description', '')[:160],
                "keywords": product_info.get('product_type', '')
            }
    
    async def analyze_product_sentiment(self, product_info: Dict) -> Dict:
        """제품 감정 분석"""
        try:
            prompt = f"""
            다음 제품 정보를 분석하여 감정 분석 결과를 제공해주세요:
            
            제품명: {product_info.get('title', '')}
            설명: {product_info.get('description', '')}
            가격: ${product_info.get('price', 0)}
            
            다음 형식으로 응답해주세요:
            
            감정 점수: [1-10점, 10점이 가장 긍정적]
            주요 감정: [긍정적/부정적/중립]
            개선 제안: [개선할 수 있는 부분들]
            
            객관적으로 분석해주세요.
            """
            
            content = await self.generate_content(prompt)
            
            # Parse the response
            lines = content.split('\n')
            result = {
                "sentiment_score": 5,
                "sentiment": "중립",
                "improvements": []
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('감정 점수:'):
                    try:
                        score = int(line.replace('감정 점수:', '').strip().split()[0])
                        result["sentiment_score"] = max(1, min(10, score))
                    except:
                        pass
                elif line.startswith('주요 감정:'):
                    sentiment = line.replace('주요 감정:', '').strip()
                    result["sentiment"] = sentiment
                elif line.startswith('개선 제안:'):
                    improvements = line.replace('개선 제안:', '').strip()
                    result["improvements"] = [imp.strip() for imp in improvements.split(',')]
            
            LoggingService.log_info(f"제품 감정 분석 완료")
            return result
            
        except Exception as e:
            LoggingService.log_error(f"제품 감정 분석 실패: {str(e)}")
            return {
                "sentiment_score": 5,
                "sentiment": "중립",
                "improvements": ["분석을 완료할 수 없습니다."]
            }
    
    async def generate_multilingual_content(self, content: str, target_language: str) -> str:
        """다국어 콘텐츠 생성"""
        try:
            prompt = f"""
            다음 콘텐츠를 {target_language}로 번역해주세요:
            
            {content}
            
            자연스럽고 매력적인 {target_language}로 번역해주세요.
            """
            
            translated_content = await self.generate_content(prompt)
            LoggingService.log_info(f"다국어 콘텐츠 생성 완료: {target_language}")
            
            return translated_content
            
        except Exception as e:
            LoggingService.log_error(f"다국어 콘텐츠 생성 실패: {str(e)}")
            return content
    
    async def test_connection(self) -> bool:
        """OpenAI API 연결 테스트"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            LoggingService.log_error(f"OpenAI 연결 테스트 실패: {str(e)}")
            return False
