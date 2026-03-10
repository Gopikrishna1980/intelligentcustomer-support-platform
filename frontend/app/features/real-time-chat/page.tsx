import Link from 'next/link'
import { ArrowLeft, MessageSquare, Wifi, Users, Clock, CheckCircle2, Zap } from 'lucide-react'

export default function RealTimeChatPage() {
  const features = [
    'WebSocket-based instant messaging',
    'Typing indicators',
    'Online/offline status',
    'Message read receipts',
    'File sharing & attachments',
    'Chat history & search',
    'Multi-agent support',
    'Customer context preview',
  ]

  const benefits = [
    {
      title: 'Instant Responses',
      description: 'No page refreshes needed. Messages appear instantly for both customers and agents',
      icon: Zap,
    },
    {
      title: 'Multi-Agent Routing',
      description: 'Seamlessly transfer conversations between agents without losing context',
      icon: Users,
    },
    {
      title: 'Always Available',
      description: 'Chat remains accessible 24/7 with AI handling off-hours support',
      icon: Clock,
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Home
        </Link>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto">
            <MessageSquare className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white">
            Real-Time Chat
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Lightning-fast WebSocket connections deliver instant communication between customers
            and support agents with zero lag.
          </p>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center gap-3 mb-12">
            <Wifi className="w-8 h-8 text-blue-600" />
            <h2 className="text-3xl font-bold text-center">Built for Speed</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            {features.map((feature, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-lg"
              >
                <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0" />
                <span className="text-gray-700 dark:text-gray-300">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Why Real-Time Matters</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon
              return (
                <div
                  key={index}
                  className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg"
                >
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{benefit.title}</h3>
                  <p className="text-gray-600 dark:text-gray-400">{benefit.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-2xl p-12 shadow-xl">
          <div className="grid grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-blue-600">&lt;50ms</div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">Latency</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-600">99.9%</div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">Uptime</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-green-600">10K+</div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">Concurrent</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Start Chatting in Real-Time</h2>
          <p className="text-xl mb-8 text-blue-100">
            Join thousands of companies delivering instant support
          </p>
          <Link
            href="/auth/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition text-lg font-semibold"
          >
            Try It Free
          </Link>
        </div>
      </section>
    </div>
  )
}
