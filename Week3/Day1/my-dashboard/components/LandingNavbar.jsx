import Link from 'next/link';

export default function LandingNavbar() {
  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link href="/" className="text-2xl font-bold text-blue-600">
              MyApp
            </Link>
          </div>
          
          <div className="flex gap-6 items-center">
            <Link href="/" className="text-gray-700 hover:text-blue-600 font-medium">
              Home
            </Link>
            <Link href="Week3/Day1/my-dashboard/app/about/pagee.js" className="text-gray-700 hover:text-blue-600 font-medium">
              About
            </Link>
            <Link href="/dashboard" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              Dashboard
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}