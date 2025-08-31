import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  CubeIcon,
  GlobeAltIcon,
  DocumentTextIcon,
  UsersIcon,
  ShareIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { name: '대시보드', href: '/', icon: HomeIcon },
  { name: '제품 관리', href: '/products', icon: CubeIcon },
  { name: '알리익스프레스 임포트', href: '/aliexpress', icon: GlobeAltIcon },
  { name: '로그', href: '/logs', icon: DocumentTextIcon },
  { name: '사용자 관리', href: '/users', icon: UsersIcon },
  { name: 'SNS 콘텐츠', href: '/sns', icon: ShareIcon },
];

function Sidebar() {
  return (
    <div className="flex flex-col w-64 bg-white shadow-lg">
      {/* Logo */}
      <div className="flex items-center justify-center h-16 px-4 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">Shopify Automation</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                isActive
                  ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-500'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <item.icon className="w-5 h-5 mr-3" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          © 2024 Shopify Automation
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
