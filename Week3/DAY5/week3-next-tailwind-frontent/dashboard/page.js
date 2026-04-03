// import Card from '@/components/ui/Card';
// import Badge from '@/components/ui/Badge';
// import Button from '@/components/ui/Button';

// export default function DashboardPage() {
//   return (
//     <div className="p-6 space-y-6">
//         <div>
//         <h1 className="text-3xl font-bold text-gray-900 mb-2">Week3 Day1</h1>
//         <p className="text-gray-600">Basic navbar and sidebar</p>
//       </div>
//       <div>
//         <h1 className="text-3xl font-bold text-gray-900 mb-2">Week3 Day2</h1>
//         <p className="text-gray-600">Dashboard with cards, badges, buttons</p>
//       </div>
//       <div>
//         <h1 className="text-3xl font-bold text-gray-900 mb-2">Week3 Day3</h1>
//         <p className="text-gray-600">Routing using next.js</p>
//       </div>

//       {/* Stats Cards */}
//       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
//         <Card variant="primary">
//           <h3 className="text-white font-semibold mb-2">Primary in blue</h3>
//           <p className="text-3xl font-bold text-white">inline</p>
//         </Card>
//         <Card variant="success">
//           <h3 className="text-white font-semibold mb-2">Revenue in green</h3>
//           <p className="text-3xl font-bold text-white">inline</p>
//         </Card>
//         <Card variant="warning">
//           <h3 className="text-white font-semibold mb-2">Pending in yellow</h3>
//           <p className="text-3xl font-bold text-white">inline styles using classename</p>
//         </Card>
//         <Card variant="danger">
//           <h3 className="text-white font-semibold mb-2">Issues in red</h3>
//           <p className="text-3xl font-bold text-white">inline styles used</p>
//         </Card>
//       </div>

//       {/* Recent Activity */}
//       <Card title="Recent Activity">
//         <div className="space-y-3">
//           <div className="flex items-center justify-between py-2 border-b">
//             <div>
//               <p className="font-medium">Task</p>
//               <p className="text-sm text-gray-500">add landing page</p>
//             </div>
//             <Badge variant="success">New</Badge>
//           </div>
//           <div className="flex items-center justify-between py-2 border-b">
//             <div>
//               <p className="font-medium">js-task</p>
//               <p className="text-sm text-gray-500">link multiple pages together</p>
//             </div>
//             <Badge variant="primary">Routing</Badge>
//           </div>
//           <div className="flex items-center justify-between py-2">
//             <div>
//               <p className="font-medium">About of landing page</p>
//               <p className="text-sm text-gray-500">not linking</p>
//             </div>
//             <Badge variant="danger">Alert</Badge>
//           </div>
//         </div>
//       </Card>
//     </div>
//   );
// }

"use client"

import { useState } from 'react';
import Link from 'next/link';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
//import {users} from '/data/users';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, AreaChart,Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Users, DollarSign, ShoppingCart, TrendingUp, ArrowRight, MoreVertical } from 'lucide-react';

// Mock user data
const recentUsers = [
  { id: 1, name: 'user1', email: 'userone@example.com', status: 'Active', role: 'Admin', avatar: 'SJ' },
  { id: 2, name: 'user2', email: 'usertwo@example.com', status: 'Active', role: 'User', avatar: 'MC' },
  { id: 3, name: 'user3', email: 'userthree@example.com', status: 'Inactive', role: 'User', avatar: 'ED' },
  { id: 4, name: 'user4', email: 'userfour@example.com', status: 'Active', role: 'Editor', avatar: 'JW' },
  { id: 5, name: 'user5', email: 'userfive@example.com', status: 'Active', role: 'User', avatar: 'LA' },
];

// Chart data
const userGrowthData = [
  { month: 'Jan', users: 1200 },
  { month: 'Feb', users: 1600 },
  { month: 'Mar', users: 1900 },
  { month: 'Apr', users: 2100 },
  { month: 'May', users: 2300 },
  { month: 'Jun', users: 2543 },
];

const revenueData = [
  { month: 'Jan', revenue: 32000 },
  { month: 'Feb', revenue: 35000 },
  { month: 'Mar', revenue: 38000 },
  { month: 'Apr', revenue: 41000 },
  { month: 'May', revenue: 43000 },
  { month: 'Jun', revenue: 45231 },
];

const ordersData = [
  { month: 'Jan', orders: 980 },
  { month: 'Feb', orders: 1100 },
  { month: 'Mar', orders: 1250 },
  { month: 'Apr', orders: 1300 },
  { month: 'May', orders: 1270 },
  { month: 'Jun', orders: 1234 },
];

const userStatusData = [
  { name: 'Active', value: 2100, color: '#10b981' },
  { name: 'Inactive', value: 443, color: '#6b7280' },
];

const roleDistributionData = [
  { role: 'Users', count: 1800 },
  { role: 'Editors', count: 500 },
  { role: 'Admins', count: 243 },
];


export default function DashboardPage() {
  return (
    <div className="p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Welcome back!</p>
      </div>
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Week3 Day1</h1>
        <p className="text-gray-600">Basic Navbar and sidebar</p>
      </div>
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Week3 Day2</h1>
        <p className="text-gray-600">Css styling</p>
      </div>
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Week3 Day3</h1>
        <p className="text-gray-600">Routing</p>
      </div>
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Week3 Day4</h1>
        <p className="text-gray-600">Responsive site</p>
      </div>
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Week3 Day5</h1>
        <p className="text-gray-600">Full working dashboard</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {/* Stat 1 */}
        <Card className="hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Users</p>
              <p className="text-2xl sm:text-3xl font-bold text-gray-900">2,543</p>
              <p className="text-sm text-green-600 mt-2">+12.5% from last month</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="text-blue-600" size={24} />
            </div>
          </div>
        </Card>

        {/* Stat 2 */}
        <Card className="hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Revenue</p>
              <p className="text-2xl sm:text-3xl font-bold text-gray-900">$45,231</p>
              <p className="text-sm text-green-600 mt-2">+8.2% from last month</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <DollarSign className="text-green-600" size={24} />
            </div>
          </div>
        </Card>

        {/* Stat 3 */}
        <Card className="hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Orders</p>
              <p className="text-2xl sm:text-3xl font-bold text-gray-900">1,234</p>
              <p className="text-sm text-red-600 mt-2">-3.1% from last month</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <ShoppingCart className="text-purple-600" size={24} />
            </div>
          </div>
        </Card>

        {/* Stat 4 */}
        <Card className="hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Growth</p>
              <p className="text-2xl sm:text-3xl font-bold text-gray-900">23.5%</p>
              <p className="text-sm text-green-600 mt-2">+5.4% from last month</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="text-yellow-600" size={24} />
            </div>
          </div>
        </Card>
      </div>







      {/* Recent Users Section */}
      <Card 
        title="Recent Users"
        footer={
          <div className="flex justify-end">
            <Link href="/dashboard/users">
              <Button variant="outline" size="sm">
                View All Users
                <ArrowRight size={16} className="ml-2" />
              </Button>
            </Link>
          </div>
        }
      >
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">User</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 hidden sm:table-cell">Email</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 hidden md:table-cell">Role</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {recentUsers.map((user) => (
                <tr key={user.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                        {user.avatar}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{user.name}</p>
                        <p className="text-sm text-gray-500 sm:hidden">{user.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-gray-600 hidden sm:table-cell">{user.email}</td>
                  <td className="py-3 px-4">
                    <Badge variant={user.status === 'Active' ? 'success' : 'default'}>
                      {user.status}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-gray-600 hidden md:table-cell">{user.role}</td>
                  <td className="py-3 px-4 text-right">
                    <button className="text-gray-400 hover:text-gray-600">
                      <MoreVertical size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Quick Actions">
          <div className="space-y-3">
            <Link href="/dashboard/users">
              <Button variant="outline" className="w-full justify-start">
                <Users size={18} className="mr-2" />
                Manage Users
              </Button>
            </Link>
            <Button variant="outline" className="w-full justify-start">
              <ShoppingCart size={18} className="mr-2" />
              View Orders
            </Button>
            <Link href="/dashboard/profile">
              <Button variant="outline" className="w-full justify-start">
                <Users size={18} className="mr-2" />
                Edit Profile
              </Button>
            </Link>
          </div>
        </Card>

        <Card title="Recent Activity">
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">New user registered</p>
                <p className="text-xs text-gray-500">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">Order #1234 completed</p>
                <p className="text-xs text-gray-500">15 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">Payment received</p>
                <p className="text-xs text-gray-500">1 hour ago</p>
              </div>
            </div>
          </div>
        </Card>


        
      </div>
            {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Growth Chart */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">User Growth</h3>
              <p className="text-sm text-gray-600">Monthly user registrations</p>
            </div>
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="text-blue-600" size={20} />
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={userGrowthData}>
              <defs>
                <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" stroke="#6b7280" style={{ fontSize: '12px' }} />
              <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                labelStyle={{ color: '#374151', fontWeight: 'bold' }}
              />
              <Area type="monotone" dataKey="users" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorUsers)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Revenue Chart */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Revenue Trends</h3>
              <p className="text-sm text-gray-600">Monthly revenue in USD</p>
            </div>
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <DollarSign className="text-green-600" size={20} />
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" stroke="#6b7280" style={{ fontSize: '12px' }} />
              <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                labelStyle={{ color: '#374151', fontWeight: 'bold' }}
                formatter={(value) => `$${value.toLocaleString()}`}
              />
              <Line type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Orders Chart */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Orders Overview</h3>
              <p className="text-sm text-gray-600">Monthly order volume</p>
            </div>
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <ShoppingCart className="text-purple-600" size={20} />
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={ordersData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" stroke="#6b7280" style={{ fontSize: '12px' }} />
              <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                labelStyle={{ color: '#374151', fontWeight: 'bold' }}
              />
              <Bar dataKey="orders" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* User Status Pie Chart */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">User Status</h3>
              <p className="text-sm text-gray-600">Active vs Inactive users</p>
            </div>
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="text-yellow-600" size={20} />
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={userStatusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {userStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Active: 2,100</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Inactive: 443</span>
            </div>
          </div>
        </div>
      </div>

      {/* Role Distribution Chart */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">User Roles Distribution</h3>
            <p className="text-sm text-gray-600">Users by role type</p>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={roleDistributionData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis type="number" stroke="#6b7280" style={{ fontSize: '12px' }} />
            <YAxis dataKey="role" type="category" stroke="#6b7280" style={{ fontSize: '12px' }} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
              labelStyle={{ color: '#374151', fontWeight: 'bold' }}
            />
            <Bar dataKey="count" fill="#3b82f6" radius={[0, 8, 8, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

    </div>
    
  );
}