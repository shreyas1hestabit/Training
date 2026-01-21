import { Search, User } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="bg-gray-800 text-white shadow-md">
      <div className="flex items-center justify-between px-6 py-3">
        <div className="flex items-center gap-4">
          <span className="text-lg font-semibold">Start Bootstrap</span>
        </div>

        {/* Search Bar */}
        <div className="flex-1 max-w-md mx-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search for..."
              className="w-full px-4 py-2 pr-10 bg-white text-gray-800 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button className="absolute right-0 top-0 h-full px-3 bg-blue-600 text-white rounded-r hover:bg-blue-700">
              <Search size={18} />
            </button>
          </div>
        </div>

        {/* User Menu */}
        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-gray-700 rounded-full">
            <User size={20} />
          </button>
        </div>
      </div>
    </header>
  );
}
