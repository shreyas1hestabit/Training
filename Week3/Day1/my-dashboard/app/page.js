/*export default function Home() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <p className="text-gray-600">Week3 Day1 task- Create Dashboard</p>
    </div>
  );
}*/

/*"use client"

import { useState } from 'react';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Modal from '@/components/ui/Modal';

export default function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold mb-4">Week3-Day1:Dashboard</h1>
      <p className="text-gray-600">Create Dashboard with navbar and sidebar</p>
      <h1 className="text-3xl font-bold">Week3-Day2:Component Testing</h1>
      
      <Card title="Button Examples">
        <div className="flex flex-wrap gap-3">
          <Button>Primary</Button>
          <Button variant="success">Success</Button>
          <Button variant="danger">Danger</Button>
          <Badge variant="primary">New</Badge>
          <Badge variant="success">Active</Badge>
        </div>
      </Card>

      <Card title="Modal Example">
        <Button onClick={() => setIsModalOpen(true)}>Open Modal</Button>
      </Card>
      <Card title="Card example">
        <div>
          <Card title="nested-cards">
            <button className='bg-blue-200 border-3 border-blue-500 p-4 rounded text-blue-700'>Nested Cards</button>
          </Card>
        </div>
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Test Modal"
        footer={
          <Button onClick={() => setIsModalOpen(false)}>Close</Button>
        }
      >
        <p>This is a test modal!</p>
        <Input label="Test Input" placeholder="Type something..." />
      </Modal>
    </div>
  );
}*/

import Link from 'next/link';
import LandingNavbar from '@/components/LandingNavbar';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <LandingNavbar />
      
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Dashboard App
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Learning React.js with Tailwind CSS.
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/dashboard">
            <Button size="lg">Get Started</Button>
          </Link>
          <Link href="/page">
            <Button variant="outline" size="lg">Learn More</Button>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card title="CARD1">
            <p className="text-gray-600">
              Landing Page
            </p>
          </Card>
          <Card title="CARD 2">
            <p className="text-gray-600">
              WEEK3
            </p>
          </Card>
          <Card title="CARD 3">
            <p className="text-gray-600">
              DAY3
            </p>
          </Card>
        </div>
      </section>
    </div>
  );
}
