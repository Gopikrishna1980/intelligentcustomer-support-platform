import { useAuthStore } from '../store/authStore';

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Welcome back, {user?.firstName}!
      </h1>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Open Tickets</h3>
          <p className="text-4xl font-bold text-blue-600">3</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Resolved</h3>
          <p className="text-4xl font-bold text-green-600">12</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Tickets</h3>
          <p className="text-4xl font-bold text-gray-600">15</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-4">
          <div className="border-l-4 border-blue-500 pl-4">
            <p className="font-medium">Ticket #1234 updated</p>
            <p className="text-sm text-gray-500">Status changed to In Progress - 2 hours ago</p>
          </div>
          <div className="border-l-4 border-green-500 pl-4">
            <p className="font-medium">Ticket #1233 resolved</p>
            <p className="text-sm text-gray-500">Issue resolved successfully - 1 day ago</p>
          </div>
        </div>
      </div>
    </div>
  );
}
