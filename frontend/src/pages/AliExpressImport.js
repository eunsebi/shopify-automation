import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { toast } from 'react-hot-toast';
import api from '../services/api';

function AliExpressImport() {
  const [keyword, setKeyword] = useState('');
  const [category, setCategory] = useState('Home & Garden');
  const [minOrders, setMinOrders] = useState(100);

  const { data: products, isLoading, refetch } = useQuery(
    ['aliexpress-search', keyword, category, minOrders],
    () => api.aliexpress.searchProducts({ keyword, category, min_orders: minOrders }),
    {
      enabled: false,
    }
  );

  const importMutation = useMutation(api.aliexpress.importProduct, {
    onSuccess: () => {
      toast.success('제품 임포트가 시작되었습니다!');
    },
    onError: () => {
      toast.error('제품 임포트 중 오류가 발생했습니다.');
    },
  });

  const handleSearch = () => {
    if (!keyword.trim()) {
      toast.error('검색어를 입력해주세요.');
      return;
    }
    refetch();
  };

  const handleImport = (productId) => {
    importMutation.mutate(productId);
  };

  return (
    <div className="px-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">알리익스프레스 임포트</h1>
        <p className="text-gray-600">알리익스프레스에서 제품을 검색하고 Shopify에 임포트</p>
      </div>

      {/* Search Form */}
      <div className="bg-white shadow rounded-lg p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">검색어</label>
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="제품명 입력..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">카테고리</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="Home & Garden">Home & Garden</option>
              <option value="Electronics">Electronics</option>
              <option value="Fashion">Fashion</option>
              <option value="Sports & Entertainment">Sports & Entertainment</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">최소 주문수</label>
            <input
              type="number"
              value={minOrders}
              onChange={(e) => setMinOrders(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          
          <div className="flex items-end">
            <button
              onClick={handleSearch}
              disabled={isLoading}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              {isLoading ? '검색 중...' : '검색'}
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      {products && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              검색 결과 ({products.length}개)
            </h3>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map((product) => (
                <div
                  key={product.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="aspect-w-1 aspect-h-1 bg-gray-200 mb-4">
                    {product.image_url ? (
                      <img
                        src={product.image_url}
                        alt={product.title}
                        className="w-full h-48 object-cover rounded"
                      />
                    ) : (
                      <div className="w-full h-48 flex items-center justify-center bg-gray-100 rounded">
                        <span className="text-gray-400">이미지 없음</span>
                      </div>
                    )}
                  </div>
                  
                  <h4 className="font-semibold text-gray-900 mb-2 truncate">
                    {product.title}
                  </h4>
                  
                  <p className="text-lg font-bold text-primary-600 mb-2">
                    {product.price}
                  </p>
                  
                  <p className="text-sm text-gray-500 mb-4">
                    주문수: {product.orders}
                  </p>
                  
                  <button
                    onClick={() => handleImport(product.id)}
                    disabled={importMutation.isLoading}
                    className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    {importMutation.isLoading ? '임포트 중...' : '임포트'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {!products && !isLoading && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">검색어를 입력하고 검색해보세요.</div>
          <p className="text-gray-400 mt-2">인기 제품을 찾아서 Shopify에 임포트할 수 있습니다.</p>
        </div>
      )}
    </div>
  );
}

export default AliExpressImport;
