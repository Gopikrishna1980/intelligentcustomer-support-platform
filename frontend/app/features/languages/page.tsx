import Link from 'next/link'
import { ArrowLeft, Globe, Languages as LanguagesIcon, MessageCircle, CheckCircle2, Sparkles } from 'lucide-react'

export default function LanguagesPage() {
  const languages = [
    'English', 'Spanish', 'French', 'German', 'Italian',
    'Portuguese', 'Russian', 'Chinese', 'Japanese', 'Korean',
    'Arabic', 'Hindi', 'Turkish', 'Dutch', 'Swedish',
    'Polish', 'Indonesian', 'Thai', 'Vietnamese', 'Hebrew',
  ]

  const features = [
    'Automatic language detection',
    'Real-time translation',
    'Native language support agents',
    'Multilingual knowledge base',
    'Translated error messages',
    'Localized date & time formats',
    'Right-to-left (RTL) support',
    'Custom language preferences',
  ]

  const benefits = [
    {
      title: 'Global Reach',
      description: 'Support customers worldwide in their native language without hiring multilingual staff',
      icon: Globe,
    },
    {
      title: 'Instant Translation',
      description: 'AI-powered translation happens in real-time during conversations',
      icon: Sparkles,
    },
    {
      title: 'Cultural Awareness',
      description: 'Context-aware translations that understand cultural nuances and idioms',
      icon: MessageCircle,
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
            <Globe className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white">
            20+ Languages
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Break down language barriers and provide exceptional support to customers worldwide.
            Automatic translation powered by AI ensures seamless communication.
          </p>
        </div>
      </section>

      {/* Supported Languages */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center gap-3 mb-12">
            <LanguagesIcon className="w-8 h-8 text-blue-600" />
            <h2 className="text-3xl font-bold text-center">Supported Languages</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {languages.map((language, index) => (
              <div
                key={index}
                className="p-4 bg-white dark:bg-gray-800 rounded-lg text-center hover:shadow-lg transition"
              >
                <span className="text-2xl mb-2 block">🌍</span>
                <span className="text-gray-700 dark:text-gray-300 font-medium">{language}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Translation Features</h2>
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
          <h2 className="text-3xl font-bold text-center mb-12">Why Multilingual Matters</h2>
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
              <div className="text-4xl font-bold text-blue-600">20+</div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">Languages</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-600">98%</div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">Accuracy</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-green-600">Instant</div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">Translation</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Go Global Today</h2>
          <p className="text-xl mb-8 text-blue-100">
            Start supporting customers in their native language
          </p>
          <Link
            href="/auth/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition text-lg font-semibold"
          >
            Enable Translations
          </Link>
        </div>
      </section>
    </div>
  )
}
