"use client"

import { useState } from 'react';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Modal from '@/components/ui/Modal';
import { Search, Plus, Edit, Trash2, Mail, Phone } from 'lucide-react';

// Mock data - more complete user list
const allUsers = [
  { id: 1, name: 'user1', email: 'userone@example.com', phone: '+91 2345678901', status: 'Active', role: 'Admin', joinDate: '2024-01-15' },
  { id: 2, name: 'user2', email: 'usertwo@example.com', phone: '+91 2345678902', status: 'Active', role: 'User', joinDate: '2024-02-20' },
  { id: 3, name: 'user3', email: 'userthree@example.com', phone: '+91 2345678903', status: 'Inactive', role: 'User', joinDate: '2024-01-10' },
  { id: 4, name: 'user4', email: 'userfour@example.com', phone: '+91 2345678904', status: 'Active', role: 'Editor', joinDate: '2024-03-05' },
  { id: 5, name: 'user5', email: 'userfive@example.com', phone: '+91 2345678905', status: 'Active', role: 'User', joinDate: '2024-02-14' },
  { id: 6, name: 'user6', email: 'usersix@example.com', phone: '+91 2345678906', status: 'Active', role: 'User', joinDate: '2024-01-28' },
  { id: 7, name: 'user7', email: 'userseven@example.com', phone: '+91 2345678907', status: 'Inactive', role: 'User', joinDate: '2024-03-12' },
  { id: 8, name: 'user8', email: 'usereight@example.com', phone: '+91 2345678908', status: 'Active', role: 'Editor', joinDate: '2024-02-08' },
  { id: 9, name: 'user9', email: 'usernine@example.com', phone: '+91 2345678909', status: 'Active', role: 'Admin', joinDate: '2024-01-05' },
  { id: 10, name: 'user10', email: 'userten@example.com', phone: '+91 2345678910', status: 'Active', role: 'User', joinDate: '2024-03-18' },
];

export default function UsersPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Filter users based on search
  const filteredUsers = allUsers.filter(user => 
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewUser = (user) => {
    setSelectedUser(user);
    setIsModalOpen(true);
  };

  return (
    <div className="p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Users</h1>
          <p className="text-gray-600">Manage your team members and their roles</p>
        </div>
        <Button>
          <Plus size={18} className="mr-2" />
          Add User
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search users by name or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <select className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>All Roles</option>
              <option>Admin</option>
              <option>Editor</option>
              <option>User</option>
            </select>
            <select className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>All Status</option>
              <option>Active</option>
              <option>Inactive</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Users Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">User</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 hidden lg:table-cell">Contact</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 hidden md:table-cell">Role</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 hidden xl:table-cell">Join Date</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user) => (
                <tr key={user.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
                        {user.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium text-gray-900 truncate">{user.name}</p>
                        <p className="text-sm text-gray-500 truncate lg:hidden">{user.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4 hidden lg:table-cell">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Mail size={14} />
                        <span className="truncate">{user.email}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Phone size={14} />
                        <span>{user.phone}</span>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant={user.status === 'Active' ? 'success' : 'default'} size="sm">
                      {user.status}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-gray-600 hidden md:table-cell">
                    <Badge 
                      variant={user.role === 'Admin' ? 'danger' : user.role === 'Editor' ? 'warning' : 'primary'}
                      size="sm"
                    >
                      {user.role}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-gray-600 text-sm hidden xl:table-cell">
                    {new Date(user.joinDate).toLocaleDateString()}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center justify-end gap-2">
                      <button 
                        onClick={() => handleViewUser(user)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="View Details"
                      >
                        <Edit size={16} />
                      </button>
                      <button 
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete User"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-6 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            Showing <strong>1-10</strong> of <strong>{allUsers.length}</strong> users
          </p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled>Previous</Button>
            <Button variant="outline" size="sm">1</Button>
            <Button size="sm">2</Button>
            <Button variant="outline" size="sm">3</Button>
            <Button variant="outline" size="sm">Next</Button>
          </div>
        </div>
      </Card>

      {/* User Details Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="User Details"
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>Close</Button>
            <Button>Save Changes</Button>
          </div>
        }
      >
        {selectedUser && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                {selectedUser.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <h3 className="text-lg font-semibold">{selectedUser.name}</h3>
                <Badge variant={selectedUser.status === 'Active' ? 'success' : 'default'}>
                  {selectedUser.status}
                </Badge>
              </div>
            </div>
            <Input label="Full Name" value={selectedUser.name} readOnly />
            <Input label="Email" value={selectedUser.email} readOnly />
            <Input label="Phone" value={selectedUser.phone} readOnly />
            <Input label="Role" value={selectedUser.role} readOnly />
            <Input label="Join Date" value={selectedUser.joinDate} readOnly />
          </div>
        )}
      </Modal>
    </div>
  );
}