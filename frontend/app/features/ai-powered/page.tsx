import Link from 'next/link'
import { ArrowLeft, Bot, Brain, MessageSquare, Sparkles, Zap, CheckCircle2 } from 'lucide-react'

export default function AIPoweredPage() {
  const capabilities = [
    'GPT-4 powered conversational AI',
    'Context-aware responses',
    'Natural language understanding',
    'Multi-turn conversations',
    'Sentiment analysis in real-time',
    'Intent detection and classification',
    'Automatic response suggestions',
    'Learning from past interactions',
  ]

  const useCases = [
    {
      title: 'Customer Queries',
      description: 'Instantly answer common questions about products, services, and policies',
      icon: MessageSquare,
    },
    {
      title: 'Technical Support',
      description: 'Guide users through troubleshooting steps with intelligent diagnostics',
      icon: Zap,
    },
    {
      title: 'Sentiment Detection',
      description: 'Identify frustrated customers and escalate to human agents automatically',
      icon: Brain,
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
            <Bot className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white">
            AI-Powered Support
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Harness the power of GPT-4 to provide intelligent, context-aware support 24/7.
            Our AI understands customer intent and delivers accurate responses instantly.
          </p>
        </div>
      </section>

      {/* Capabilities Grid */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">AI Capabilities</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {capabilities.map((capability, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-lg"
              >
                <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0" />
                <span className="text-gray-700 dark:text-gray-300">{capability}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Use Cases</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {useCases.map((useCase, index) => {
              const Icon = useCase.icon
              return (
                <div
                  key={index}
                  className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg"
                >
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{useCase.title}</h3>
                  <p className="text-gray-600 dark:text-gray-400">{useCase.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <Sparkles className="w-12 h-12 mx-auto mb-4" />
          <h2 className="text-3xl font-bold mb-4">Experience AI in Action</h2>
          <p className="text-xl mb-8 text-blue-100">
            See how our AI-powered chatbot can transform your customer support
          </p>
          <Link
            href="/auth/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition text-lg font-semibold"
          >
            Start Free Trial
          </Link>
        </div>
      </section>
    </div>
  )
}
