#!/bin/bash

echo "🚀 Shopify Automation System 시작 중..."

# 환경변수 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. env.example을 복사합니다..."
    cp env.example .env
    echo "📝 .env 파일을 편집하여 API 키를 설정해주세요."
    echo "   - SHOPIFY_SHOP_URL"
    echo "   - SHOPIFY_ACCESS_TOKEN"
    echo "   - OPENAI_API_KEY"
    exit 1
fi

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다."
    echo "   https://docs.docker.com/get-docker/ 에서 Docker를 설치해주세요."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되지 않았습니다."
    echo "   https://docs.docker.com/compose/install/ 에서 Docker Compose를 설치해주세요."
    exit 1
fi

# 기존 컨테이너 정리
echo "🧹 기존 컨테이너 정리 중..."
docker-compose down

# 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker-compose build

# 서비스 시작
echo "🚀 서비스 시작 중..."
docker-compose up -d

# 서비스 상태 확인
echo "⏳ 서비스 상태 확인 중..."
sleep 10

# 헬스 체크
echo "🏥 헬스 체크 중..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend 서비스가 정상적으로 실행되었습니다."
else
    echo "❌ Backend 서비스에 문제가 있습니다."
    echo "   로그를 확인해주세요: docker-compose logs backend"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend 서비스가 정상적으로 실행되었습니다."
else
    echo "❌ Frontend 서비스에 문제가 있습니다."
    echo "   로그를 확인해주세요: docker-compose logs frontend"
fi

echo ""
echo "🎉 Shopify Automation System이 시작되었습니다!"
echo ""
echo "📱 접속 정보:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API 문서: http://localhost:8000/docs"
echo ""
echo "📋 유용한 명령어:"
echo "   로그 확인: docker-compose logs -f"
echo "   서비스 중지: docker-compose down"
echo "   서비스 재시작: docker-compose restart"
echo ""
