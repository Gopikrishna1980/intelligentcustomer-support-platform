import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Welcome to Intelligent Customer Support
          </h1>
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Experience next-generation customer support powered by AI. Get instant answers,
            create tickets, and connect with our support team 24/7.
          </p>
          <div className="flex justify-center space-x-4">
            <Link
              to="/register"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg text-lg font-semibold"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="bg-white hover:bg-gray-50 text-blue-600 px-8 py-3 rounded-lg text-lg font-semibold border-2 border-blue-600"
            >
              Sign In
            </Link>
          </div>
        </div>

        <div className="mt-20 grid md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-lg shadow-lg">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-bold mb-3">AI-Powered Chat</h3>
            <p className="text-gray-600">
              Get instant answers from our intelligent AI assistant trained on our knowledge base.
            </p>
          </div>
          <div className="bg-white p-8 rounded-lg shadow-lg">
            <div className="text-4xl mb-4">🎫</div>
            <h3 className="text-xl font-bold mb-3">Ticket Management</h3>
            <p className="text-gray-600">
              Create, track, and manage your support tickets with real-time updates.
            </p>
          </div>
          <div className="bg-white p-8 rounded-lg shadow-lg">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-bold mb-3">24/7 Support</h3>
            <p className="text-gray-600">
              Our AI and human agents work together to provide round-the-clock support.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
