import LandingNavbar from '@/components/LandingNavbar';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <LandingNavbar />
      
      <div className="max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">About This Project</h1>
        
        <Card className="mb-6">
          <h2 className="text-2xl font-semibold mb-4">Learning Goals</h2>
          <p className="text-gray-600 mb-4">
            Tailwind CSS and Next.js fundamentals including:
          </p>
          <div className="flex flex-wrap gap-2 mb-4">
            <Badge variant="primary">File-based Routing</Badge>
            <Badge variant="success">Nested Layouts</Badge>
            <Badge variant="info">Server Components</Badge>
            <Badge variant="warning">Client Components</Badge>
          </div>
        </Card>

        <Card title="Tech Stack">
          <ul className="space-y-2 text-gray-600">
            <li><strong>Next.js</strong> - React framework with App Router</li>
            <li><strong>React</strong> - UI library</li>
            <li><strong>Tailwind CSS</strong> - Utility-first CSS</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}