"use client"

import { useState } from 'react';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';

export default function ProfilePage() {
  const [name, setName] = useState('shreya singhal');
  const [email, setEmail] = useState('shreyas1.hestabit@example.com');

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile Settings</h1>
        <p className="text-gray-600">Manage your account settings and preferences.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Info Card */}
        <Card title="Profile Information" className="lg:col-span-2">
          <div className="space-y-4">
            <Input 
              label="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <Input 
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Input 
              label="Phone Number"
              type="tel"
              placeholder="+91 - 9700247391"
            />
            <div className="flex gap-2 pt-4">
              <Button>Save Changes</Button>
              <Button variant="outline">Cancel</Button>
            </div>
          </div>
        </Card>

        {/* Account Status Card */}
        <Card title="Account Status">
          <div className="space-y-4">
            <div className="flex items-center justify-center w-24 h-24 mx-auto bg-blue-500 rounded-full text-white text-3xl font-bold">
              JD
            </div>
            <div className="text-center">
              <h3 className="font-semibold text-lg">{name}</h3>
              <p className="text-sm text-gray-600">{email}</p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center">
              <Badge variant="success">Active</Badge>
              <Badge variant="primary">Premium</Badge>
            </div>
          </div>
        </Card>
      </div>

      {/* Security Settings */}
      <Card title="Security Settings">
        <div className="space-y-4">
          <Input 
            label="Current Password"
            type="password"
            placeholder="Enter current password"
          />
          <Input 
            label="New Password"
            type="password"
            placeholder="Enter new password"
          />
          <Input 
            label="Confirm New Password"
            type="password"
            placeholder="Confirm new password"
          />
          <Button variant="danger">Update Password</Button>
        </div>
      </Card>
    </div>
  );
}