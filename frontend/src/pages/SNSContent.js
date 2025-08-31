import React from 'react';
import { useQuery } from 'react-query';
import api from '../services/api';

function SNSContent() {
  const { data: platforms, isLoading: platformsLoading } = useQuery(
    'sns-platforms',
    api.sns.getPlatforms
  );

  const { data: analytics, isLoading: analyticsLoading } = useQuery(
    'sns-analytics',
    () => api.sns.getAnalytics({ days: 30 })
  );

  return (
    <div className="px-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">SNS 콘텐츠</h1>
        <p className="text-gray-600">AI 기반 SNS 콘텐츠 생성 및 관리</p>
      </div>

      {/* Analytics */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">📝</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">총 콘텐츠</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {analytics.overview?.total_content || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">✅</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">발행된 콘텐츠</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {analytics.overview?.published_content || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">📊</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">발행률</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {analytics.overview?.publish_rate?.toFixed(1) || 0}%
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">👥</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">총 참여도</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {analytics.overview?.total_engagement || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Platforms */}
      <div className="bg-white shadow rounded-lg mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">지원 플랫폼</h3>
        </div>
        
        <div className="p-6">
          {platformsLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">플랫폼 정보를 불러오는 중...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {platforms?.platforms?.map((platform) => (
                <div
                  key={platform.name}
                  className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                      <span className="text-primary-600 text-xl">
                        {platform.name === 'instagram' && '📷'}
                        {platform.name === 'tiktok' && '🎵'}
                        {platform.name === 'pinterest' && '📌'}
                        {platform.name === 'facebook' && '📘'}
                        {platform.name === 'twitter' && '🐦'}
                      </span>
                    </div>
                    <div className="ml-4">
                      <h4 className="text-lg font-semibold text-gray-900">
                        {platform.display_name}
                      </h4>
                      <p className="text-sm text-gray-500">{platform.description}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-gray-700">콘텐츠 타입:</p>
                    <div className="flex flex-wrap gap-2">
                      {platform.content_types.map((type) => (
                        <span
                          key={type}
                          className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800"
                        >
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-4">사용 방법</h3>
        <div className="space-y-3 text-blue-800">
          <p>1. <strong>제품 선택</strong>: 제품 관리 페이지에서 SNS 콘텐츠를 생성할 제품을 선택하세요.</p>
          <p>2. <strong>플랫폼 선택</strong>: Instagram, TikTok, Pinterest 등 원하는 플랫폼을 선택하세요.</p>
          <p>3. <strong>AI 생성</strong>: AI가 자동으로 제품에 맞는 매력적인 콘텐츠를 생성합니다.</p>
          <p>4. <strong>편집 및 발행</strong>: 생성된 콘텐츠를 편집하고 SNS에 발행하세요.</p>
        </div>
      </div>
    </div>
  );
}

export default SNSContent;
