# Shopify Automation System

Shopify 자동화 웹 애플리케이션으로, 알리익스프레스에서 제품을 자동으로 임포트하고 SNS 콘텐츠를 생성하는 시스템입니다.

## 🚀 주요 기능

### 1. 제품 관리
- Shopify 제품 목록 조회 및 관리
- 제품 상세 정보 수정
- Shopify와 실시간 동기화

### 2. 알리익스프레스 임포트
- 알리익스프레스에서 인기 제품 검색
- US 배송 가능한 제품 필터링
- 자동으로 Shopify에 제품 등록

### 3. SNS 콘텐츠 생성
- AI를 활용한 SNS 콘텐츠 자동 생성
- Instagram, TikTok, Pinterest 등 다중 플랫폼 지원
- 해시태그 및 CTA 자동 생성

### 4. 로그 관리
- 실시간 로그 모니터링
- 에러 로그 필터링 및 분석
- 로그 통계 및 내보내기

### 5. 사용자 관리
- 사용자 등록 및 관리
- 권한 관리
- 사용자 활동 추적

## 🛠 기술 스택

### Backend
- **Python 3.11**
- **FastAPI** - 웹 프레임워크
- **PostgreSQL** - 메인 데이터베이스
- **Redis** - 캐싱 및 세션 관리
- **SQLAlchemy** - ORM
- **Playwright** - 웹 스크래핑
- **OpenAI API** - AI 콘텐츠 생성
- **Shopify API** - 쇼핑몰 연동

### Frontend
- **React 18** - 프론트엔드 프레임워크
- **Tailwind CSS** - 스타일링
- **React Query** - 상태 관리
- **Recharts** - 차트 라이브러리
- **Axios** - HTTP 클라이언트

### DevOps
- **Docker & Docker Compose** - 컨테이너화
- **GitHub** - 버전 관리

## 📋 설치 및 실행

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd shopify-automation

# 환경변수 파일 생성
cp env.example .env
```

### 2. 환경변수 설정

`.env` 파일을 편집하여 다음 정보를 입력하세요:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password123@localhost:5432/shopify_automation
REDIS_URL=redis://localhost:6379

# Shopify API Configuration
SHOPIFY_SHOP_URL=your-shop.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_shopify_access_token
SHOPIFY_API_VERSION=2024-01

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key

# Application Configuration
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Docker로 실행

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

### 4. 개발 모드로 실행

```bash
# Backend 실행
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend 실행 (새 터미널)
cd frontend
npm install
npm start
```

## 🌐 접속 정보

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 프로젝트 구조

```
shopify-automation/
├── backend/                 # Python 백엔드
│   ├── app/
│   │   ├── api/            # API 엔드포인트
│   │   ├── core/           # 설정 및 데이터베이스
│   │   ├── models/         # 데이터 모델
│   │   └── services/       # 비즈니스 로직
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/     # 재사용 컴포넌트
│   │   ├── pages/         # 페이지 컴포넌트
│   │   ├── services/      # API 서비스
│   │   └── utils/         # 유틸리티 함수
│   ├── package.json
│   └── Dockerfile
├── logs/                   # 로그 파일
├── docker-compose.yml      # Docker 설정
├── env.example            # 환경변수 예시
└── README.md
```

## 🔧 API 사용법

### 제품 관리

```bash
# 제품 목록 조회
GET /api/v1/products?page=1&limit=20

# 제품 상세 조회
GET /api/v1/products/{id}

# Shopify 동기화
POST /api/v1/products/sync-shopify
```

### 알리익스프레스 임포트

```bash
# 제품 검색
GET /api/v1/aliexpress/search?keyword=garden&category=Home%20%26%20Garden

# 인기 제품 조회
GET /api/v1/aliexpress/trending?category=Home%20%26%20Garden

# 제품 임포트
POST /api/v1/aliexpress/import
```

### SNS 콘텐츠

```bash
# SNS 콘텐츠 생성
POST /api/v1/sns/generate/{product_id}

# 콘텐츠 조회
GET /api/v1/sns/content/{product_id}
```

## 🚨 주의사항

1. **API 키 보안**: 환경변수에 저장된 API 키를 절대 공개하지 마세요.
2. **웹 스크래핑**: 알리익스프레스 웹사이트의 이용약관을 준수하세요.
3. **데이터 백업**: 정기적으로 데이터베이스를 백업하세요.
4. **모니터링**: 로그를 정기적으로 확인하여 시스템 상태를 모니터링하세요.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.

---

**Shopify Automation System** - 효율적인 쇼핑몰 자동화 솔루션
