"use client"
import { LayoutDashboard, Layers, FileText, BarChart3, Table, Menu, ChevronRight } from 'lucide-react';
import { useState } from 'react';

export default function Sidebar() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-gray-800 text-white transition-all duration-300 flex flex-col h-screen`}>
      {/* Sidebar Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <span className={`font-semibold text-lg ${!sidebarOpen && 'hidden'}`}>Start Bootstrap</span>
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-1 hover:bg-gray-700 rounded"
        >
          <Menu size={20} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        {/* CORE Section */}
        <div className="mb-6">
          <p className={`text-xs text-gray-400 mb-2 uppercase tracking-wide ${!sidebarOpen && 'hidden'}`}>Core</p>
          <button className="w-full flex items-center gap-3 p-2 rounded hover:bg-gray-700 bg-gray-700">
            <LayoutDashboard size={20} />
            <span className={`${!sidebarOpen && 'hidden'}`}>Dashboard</span>
          </button>
        </div>

        {/* INTERFACE Section */}
        <div className="mb-6">
          <p className={`text-xs text-gray-400 mb-2 uppercase tracking-wide ${!sidebarOpen && 'hidden'}`}>Interface</p>
          <button className="w-full flex items-center justify-between p-2 rounded hover:bg-gray-700 mb-1">
            <div className="flex items-center gap-3">
              <Layers size={20} />
              <span className={`${!sidebarOpen && 'hidden'}`}>Layouts</span>
            </div>
            <ChevronRight size={16} className={`${!sidebarOpen && 'hidden'}`} />
          </button>
          <button className="w-full flex items-center justify-between p-2 rounded hover:bg-gray-700">
            <div className="flex items-center gap-3">
              <FileText size={20} />
              <span className={`${!sidebarOpen && 'hidden'}`}>Pages</span>
            </div>
            <ChevronRight size={16} className={`${!sidebarOpen && 'hidden'}`} />
          </button>
        </div>

        {/* ADDONS Section */}
        <div>
          <p className={`text-xs text-gray-400 mb-2 uppercase tracking-wide ${!sidebarOpen && 'hidden'}`}>Addons</p>
          <button className="w-full flex items-center gap-3 p-2 rounded hover:bg-gray-700 mb-1">
            <BarChart3 size={20} />
            <span className={`${!sidebarOpen && 'hidden'}`}>Charts</span>
          </button>
          <button className="w-full flex items-center gap-3 p-2 rounded hover:bg-gray-700">
            <Table size={20} />
            <span className={`${!sidebarOpen && 'hidden'}`}>Tables</span>
          </button>
        </div>
      </nav>
    </aside>
  );
}
