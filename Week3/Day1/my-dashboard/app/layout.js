/*import './globals.css'
import Sidebar from '@/components/ui/Sidebar'
import Navbar from '@/components/ui/Navbar'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="flex h-screen bg-gray-100">
          <Sidebar />
          <div className="flex-1 flex flex-col">
            <Navbar />
            <main className="flex-1 overflow-auto">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  )
}*/

import './globals.css'

export const metadata = {
  title: 'Dashboard App',
  description: 'WEEK3 DAY3',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  )
}

