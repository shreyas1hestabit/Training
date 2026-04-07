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

// import Link from 'next/link';
// import LandingNavbar from '@/components/LandingNavbar';
// import Button from '@/components/ui/Button';
// import Card from '@/components/ui/Card';

// export default function Home() {
//   return (
//     <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
//       <LandingNavbar />
      
//       {/* Hero Section */}
//       <section className="max-w-7xl mx-auto px-4 py-20 text-center">
//         <h1 className="text-5xl font-bold text-gray-900 mb-6">
//           Dashboard App
//         </h1>
//         <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
//           Learning React.js with Tailwind CSS.
//         </p>
//         <div className="flex gap-4 justify-center">
//           <Link href="/dashboard">
//             <Button size="lg">Get Started</Button>
//           </Link>
//           <Link href="/page">
//             <Button variant="outline" size="lg">Learn More</Button>
//           </Link>
//         </div>
//       </section>

//       {/* Features Section */}
//       <section className="max-w-7xl mx-auto px-4 py-16">
//         <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
//           <Card title="CARD1">
//             <p className="text-gray-600">
//               Landing Page
//             </p>
//           </Card>
//           <Card title="CARD 2">
//             <p className="text-gray-600">
//               WEEK3
//             </p>
//           </Card>
//           <Card title="CARD 3">
//             <p className="text-gray-600">
//               DAY3
//             </p>
//           </Card>
//         </div>
//       </section>
//     </div>
//   );
// }

"use client"

import { useState } from 'react';
import Link from 'next/link';
import { Menu, X, Check, Star, ArrowRight, Zap, Shield, Users, BarChart3 } from 'lucide-react';

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className="fixed w-full bg-white shadow-sm z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link href="/">
              <h1 className="text-2xl font-bold text-blue-600">Dashboard App</h1>
            </Link>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-gray-700 hover:text-blue-600">Features</a>
              <a href="#testimonials" className="text-gray-700 hover:text-blue-600">Reviews</a>
              <Link href="/about" className="text-gray-700 hover:text-blue-600">About</Link>
              <Link href="/dashboard" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                Dashboard
              </Link>
              <Link href="/login" className="block bg-blue-600 text-white px-4 py-2 rounded-lg text-center">
                Login
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="md:hidden">
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden border-t py-4 space-y-2">
              <a href="#features" className="block py-2 text-gray-700">Features</a>
              <a href="#testimonials" className="block py-2 text-gray-700">Reviews</a>
              <Link href="/about/page" className="block py-2 text-gray-700">About</Link>
              <Link href="/dashboard" className="block bg-blue-600 text-white px-4 py-2 rounded-lg text-center">
                Dashboard
              </Link>
              <Link href="/login" className="block bg-blue-600 text-white px-4 py-2 rounded-lg text-center">
                Login
              </Link>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-24 pb-12 md:pt-32 md:pb-20 px-4 bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Text */}
            <div>
              <div className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm mb-6">
                <Zap size={16} className="mr-2" /> {/**lightning bolt icon from lucide react */}
                AI-Powered Analytics Dashboard
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
                Your Dream Dashboard
              </h1>
              <p className="text-lg text-gray-600 mb-8">
                The modern platform for building powerful dashboards. Get real-time insights and beautiful charts.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/dashboard" className="inline-flex items-center justify-center px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700">
                  Explore Now
                  <ArrowRight size={20} className="ml-2" />
                </Link>
                <button className="px-8 py-4 bg-white text-gray-700 font-semibold rounded-lg border-2 border-gray-300 hover:border-blue-600">
                  Watch Demo
                </button>
              </div>
            </div>

            {/* Image Placeholder */}
            <div className="bg-gradient-to-br from-blue-400 to-indigo-600 rounded-2xl h-96 flex items-center justify-center text-white text-xl font-semibold">
              Dashboard Preview
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Everything you need
            </h2>
            <p className="text-xl text-gray-600">
              Powerful features for your business
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="p-8 bg-white rounded-xl border-2 border-gray-200 hover:border-blue-500 hover:shadow-xl transition-all">
              <div className="w-14 h-14 bg-blue-100 rounded-lg flex items-center justify-center mb-6">
                <BarChart3 className="text-blue-600" size={28} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Real-time Analytics</h3>
              <p className="text-gray-600">
                Get instant insights with live data updates and beautiful visualizations.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="p-8 bg-white rounded-xl border-2 border-gray-200 hover:border-blue-500 hover:shadow-xl transition-all">
              <div className="w-14 h-14 bg-purple-100 rounded-lg flex items-center justify-center mb-6">
                <Shield className="text-purple-600" size={28} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Secure</h3>
              <p className="text-gray-600">
                Bank-level encryption keeps your data safe and protected.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="p-8 bg-white rounded-xl border-2 border-gray-200 hover:border-blue-500 hover:shadow-xl transition-all">
              <div className="w-14 h-14 bg-green-100 rounded-lg flex items-center justify-center mb-6">
                <Users className="text-green-600" size={28} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Team Collaboration</h3>
              <p className="text-gray-600">
                Work together seamlessly with your team in real-time.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Reviews */}
      <section id="testimonials" className="py-20 px-4 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Loved by teams worldwide
            </h2>
            <p className="text-xl text-gray-600">
              See what our customers say
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Testimonial 1 */}
            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} size={20} className="fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-6">
                "DashPro transformed how we analyze data. The interface is so intuitive."
              </p>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                  SM
                </div>
                <div>
                  <p className="font-semibold">Sarah Mitchell</p>
                  <p className="text-sm text-gray-600">CEO, TechStart</p>
                </div>
              </div>
            </div>

            {/* Testimonial 2 */}
            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} size={20} className="fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-6">
                "Best dashboard tool we've used. Makes collaboration easy."
              </p>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                  JD
                </div>
                <div>
                  <p className="font-semibold">James Davis</p>
                  <p className="text-sm text-gray-600">Product Manager</p>
                </div>
              </div>
            </div>

            {/* Testimonial 3 */}
            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} size={20} className="fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-6">
                "Outstanding support. They helped us migrate seamlessly."
              </p>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center text-white font-bold">
                  EW
                </div>
                <div>
                  <p className="font-semibold">Emily Wang</p>
                  <p className="text-sm text-gray-600">CTO, FinTech</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to get started?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of teams using Dashboard App
          </p>
          <Link href="/dashboard" className="inline-flex items-center px-8 py-4 bg-white text-blue-600 font-semibold rounded-lg hover:bg-gray-100">
            Start Now
            <ArrowRight size={20} className="ml-2" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="text-white font-bold text-lg mb-4">Dashboard App</h3>
              <p className="text-sm">
                Build powerful dashboards with ease.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/about" className="hover:text-white">About</Link></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Privacy</a></li>
                <li><a href="#" className="hover:text-white">Terms</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center">
            <p className="text-sm">&copy; 2026 Dashboard App. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}