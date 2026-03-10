import Link from 'next/link'
import { ArrowRight, Bot, MessageSquare, Zap, BarChart, Globe, Shield } from 'lucide-react'

export default function LandingPage() {
  const features = [
    { icon: Bot, title: 'AI-Powered', description: 'GPT-4 chatbot with intelligent responses', href: '/features/ai-powered' },
    { icon: MessageSquare, title: 'Real-Time Chat', description: 'WebSocket-based instant messaging', href: '/features/real-time-chat' },
    { icon: Zap, title: 'Smart Routing', description: 'Intelligent ticket assignment', href: '/features/smart-routing' },
    { icon: BarChart, title: 'Analytics', description: 'Comprehensive insights and reports', href: '/features/analytics' },
    { icon: Globe, title: '20+ Languages', description: 'Multi-language translation support', href: '/features/languages' },
    { icon: Shield, title: 'Enterprise Security', description: 'RBAC, audit logs, rate limiting', href: '/features/security' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              SupportAI
            </span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/auth/login"
              className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition"
            >
              Login
            </Link>
            <Link
              href="/auth/register"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Get Started
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto space-y-6">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white">
            Customer Support
            <span className="block bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Powered by AI
            </span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Transform your customer support with 35+ intelligent features including AI chatbots,
            sentiment analysis, smart routing, and real-time analytics.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-6">
            <Link
              href="/auth/register"
              className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2 text-lg font-semibold"
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/auth/login"
              className="px-8 py-4 border-2 border-gray-300 dark:border-gray-600 rounded-lg hover:border-blue-600 dark:hover:border-blue-500 transition text-lg font-semibold"
            >
              View Demo
            </Link>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto mt-20">
          <div>
            <div className="text-4xl font-bold text-blue-600">35+</div>
            <div className="text-gray-600 dark:text-gray-400 mt-2">AI Features</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-purple-600">99.9%</div>
            <div className="text-gray-600 dark:text-gray-400 mt-2">Uptime</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-green-600">&lt;200ms</div>
            <div className="text-gray-600 dark:text-gray-400 mt-2">Response Time</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-orange-600">20+</div>
            <div className="text-gray-600 dark:text-gray-400 mt-2">Languages</div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">
          Everything You Need
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Link
                key={index}
                href={feature.href}
                className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition group cursor-pointer"
              >
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-200 dark:group-hover:bg-blue-900/50 transition">
                  <Icon className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2 group-hover:text-blue-600 transition">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-400">{feature.description}</p>
                <div className="mt-4 text-blue-600 text-sm font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                  Learn more <ArrowRight className="w-4 h-4" />
                </div>
              </Link>
            )
          })}
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Transform Your Support?
          </h2>
          <p className="text-xl mb-8 text-blue-100">
            Join thousands of companies using AI-powered support
          </p>
          <Link
            href="/auth/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition text-lg font-semibold"
          >
            Get Started Free
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 mt-20 border-t border-gray-200 dark:border-gray-800">
        <div className="text-center text-gray-600 dark:text-gray-400">
          <p>&copy; 2024 SupportAI. Built with Next.js 14 & FastAPI.</p>
        </div>
      </footer>
    </div>
  )
}
