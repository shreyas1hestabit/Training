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

/*import './globals.css'

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
}*/

import './globals.css'

export const metadata = {
  title: 'Dashboard App - Build Powerful Dashboards Faster',
  description: 'The modern platform for building powerful dashboards. Get real-time insights, beautiful charts, and seamless collaboration. Start your free trial today.',
  keywords: ['dashboard', 'analytics', 'data visualization', 'business intelligence', 'SaaS'],
  authors: [{ name: 'Dashboard App Team' }],
  openGraph: {
    title: 'Dashboard App - Build Powerful Dashboards Faster',
    description: 'Transform your data into insights with our modern dashboard platform.',
    type: 'website',
    locale: 'en_US',
  },
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        {children}
      </body>
    </html>
  )
}

