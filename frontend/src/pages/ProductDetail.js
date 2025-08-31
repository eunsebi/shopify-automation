import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import api from '../services/api';

function ProductDetail() {
  const { id } = useParams();
  
  const { data: product, isLoading, error } = useQuery(
    ['product', id],
    () => api.products.getProduct(id)
  );

  if (isLoading) {
    return (
      <div className="px-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">제품 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-6">
        <div className="text-center py-12">
          <div className="text-red-600 text-lg">제품 정보를 불러오는 중 오류가 발생했습니다.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">제품 상세</h1>
        <p className="text-gray-600">제품 정보 및 관리</p>
      </div>

      {product && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* 제품 이미지 */}
            <div>
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.title}
                  className="w-full rounded-lg"
                />
              ) : (
                <div className="w-full h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                  <span className="text-gray-400">이미지 없음</span>
                </div>
              )}
            </div>

            {/* 제품 정보 */}
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">{product.title}</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">가격</label>
                  <p className="text-2xl font-bold text-primary-600">${product.price || 0}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">설명</label>
                  <p className="text-gray-600">{product.description || '설명 없음'}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">상태</label>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    product.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {product.status}
                  </span>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">등록일</label>
                  <p className="text-gray-600">{new Date(product.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProductDetail;
