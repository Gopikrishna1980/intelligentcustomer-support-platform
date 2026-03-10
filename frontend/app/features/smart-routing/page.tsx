import Link from 'next/link'
import { ArrowLeft, Zap, Target, Brain, Route, CheckCircle2, TrendingUp } from 'lucide-react'

export default function SmartRoutingPage() {
  const features = [
    'AI-powered ticket categorization',
    'Skills-based agent matching',
    'Load balancing across agents',
    'Priority-based queue management',
    'Automatic escalation rules',
    'Round-robin distribution',
    'Department-specific routing',
    'Language-based assignment',
  ]

  const howItWorks = [
    {
      title: 'Analyze',
      description: 'AI analyzes ticket content, urgency, and customer sentiment',
      icon: Brain,
    },
    {
      title: 'Match',
      description: 'System finds the best-suited agent based on skills and availability',
      icon: Target,
    },
    {
      title: 'Route',
      description: 'Ticket is automatically assigned and agent receives notification',
      icon: Route,
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
            <Zap className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white">
            Smart Routing
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Intelligent ticket assignment that matches customers with the right agent every time.
            Reduce resolution time by up to 40% with AI-powered routing.
          </p>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Routing Features</h2>
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

      {/* How It Works */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {howItWorks.map((step, index) => {
              const Icon = step.icon
              return (
                <div key={index} className="relative">
                  {index < howItWorks.length - 1 && (
                    <div className="hidden md:block absolute top-12 left-full w-full h-0.5 bg-blue-200 dark:bg-blue-900 -ml-4" />
                  )}
                  <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg relative z-10">
                    <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-4">
                      <Icon className="w-6 h-6 text-blue-600" />
                    </div>
                    <div className="text-sm text-blue-600 font-semibold mb-2">Step {index + 1}</div>
                    <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                    <p className="text-gray-600 dark:text-gray-400">{step.description}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-2xl p-12 shadow-xl">
          <div className="flex items-center gap-3 mb-8 justify-center">
            <TrendingUp className="w-8 h-8 text-green-600" />
            <h2 className="text-2xl font-bold">Proven Results</h2>
          </div>
          <div className="grid grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-blue-600">40%</div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">Faster Resolution</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-600">85%</div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">First Contact Resolution</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-green-600">95%</div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">Customer Satisfaction</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Optimize Your Support Workflow</h2>
          <p className="text-xl mb-8 text-blue-100">
            Start routing tickets intelligently with AI
          </p>
          <Link
            href="/auth/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition text-lg font-semibold"
          >
            Get Started
          </Link>
        </div>
      </section>
    </div>
  )
}
