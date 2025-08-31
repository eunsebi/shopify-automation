import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import api from '../services/api';

function Products() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const queryClient = useQueryClient();

  const { data: productsData, isLoading, error } = useQuery(
    ['products', page, search],
    () => api.products.getProducts({ page, limit: 20, search }),
    {
      keepPreviousData: true,
    }
  );

  const syncMutation = useMutation(api.products.syncShopify, {
    onSuccess: () => {
      toast.success('Shopify 동기화가 완료되었습니다!');
      queryClient.invalidateQueries('products');
    },
    onError: () => {
      toast.error('Shopify 동기화 중 오류가 발생했습니다.');
    },
  });

  const handleSync = () => {
    syncMutation.mutate();
  };

  if (error) {
    return (
      <div className="px-6">
        <div className="text-center py-12">
          <div className="text-red-600 text-lg">제품 목록을 불러오는 중 오류가 발생했습니다.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-6">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">제품 관리</h1>
            <p className="text-gray-600">Shopify 제품 목록 및 관리</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleSync}
              disabled={syncMutation.isLoading}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <ArrowPathIcon className={`h-4 w-4 mr-2 ${syncMutation.isLoading ? 'animate-spin' : ''}`} />
              Shopify 동기화
            </button>
            <Link
              to="/aliexpress"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              제품 임포트
            </Link>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="제품명으로 검색..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>

      {/* Products Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">제품 목록을 불러오는 중...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {productsData?.data?.map((product) => (
            <div
              key={product.id}
              className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
            >
              <div className="aspect-w-1 aspect-h-1 bg-gray-200">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.title}
                    className="w-full h-48 object-cover"
                  />
                ) : (
                  <div className="w-full h-48 flex items-center justify-center bg-gray-100">
                    <span className="text-gray-400">이미지 없음</span>
                  </div>
                )}
              </div>
              <div className="p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2 truncate">
                  {product.title}
                </h3>
                <p className="text-2xl font-bold text-primary-600 mb-2">
                  ${product.price || 0}
                </p>
                <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                  <span>상태: {product.status}</span>
                  <span>{new Date(product.created_at).toLocaleDateString()}</span>
                </div>
                <Link
                  to={`/products/${product.id}`}
                  className="block w-full text-center bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition-colors"
                >
                  상세보기
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {productsData?.data?.length > 0 && (
        <div className="mt-8 flex justify-center">
          <nav className="flex items-center space-x-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              이전
            </button>
            <span className="px-3 py-2 text-sm font-medium text-gray-700">
              {page}
            </span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={!productsData?.data || productsData.data.length < 20}
              className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              다음
            </button>
          </nav>
        </div>
      )}

      {productsData?.data?.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">등록된 제품이 없습니다.</div>
          <p className="text-gray-400 mt-2">알리익스프레스에서 제품을 임포트해보세요.</p>
        </div>
      )}
    </div>
  );
}

export default Products;
