import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';

export default function DashboardPage() {
  return (
    <div className="p-6 space-y-6">
        <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Week3 Day1</h1>
        <p className="text-gray-600">Basic navbar and sidebar</p>
      </div>
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Week3 Day2</h1>
        <p className="text-gray-600">Dashboard with cards, badges, buttons</p>
      </div>
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Week3 Day3</h1>
        <p className="text-gray-600">Routing using next.js</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card variant="primary">
          <h3 className="text-white font-semibold mb-2">Primary in blue</h3>
          <p className="text-3xl font-bold text-white">inline</p>
        </Card>
        <Card variant="success">
          <h3 className="text-white font-semibold mb-2">Revenue in green</h3>
          <p className="text-3xl font-bold text-white">inline</p>
        </Card>
        <Card variant="warning">
          <h3 className="text-white font-semibold mb-2">Pending in yellow</h3>
          <p className="text-3xl font-bold text-white">inline styles using classename</p>
        </Card>
        <Card variant="danger">
          <h3 className="text-white font-semibold mb-2">Issues in red</h3>
          <p className="text-3xl font-bold text-white">inline styles used</p>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card title="Recent Activity">
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b">
            <div>
              <p className="font-medium">Task</p>
              <p className="text-sm text-gray-500">add landing page</p>
            </div>
            <Badge variant="success">New</Badge>
          </div>
          <div className="flex items-center justify-between py-2 border-b">
            <div>
              <p className="font-medium">js-task</p>
              <p className="text-sm text-gray-500">link multiple pages together</p>
            </div>
            <Badge variant="primary">Routing</Badge>
          </div>
          <div className="flex items-center justify-between py-2">
            <div>
              <p className="font-medium">About of landing page</p>
              <p className="text-sm text-gray-500">not linking</p>
            </div>
            <Badge variant="danger">Alert</Badge>
          </div>
        </div>
      </Card>
    </div>
  );
}