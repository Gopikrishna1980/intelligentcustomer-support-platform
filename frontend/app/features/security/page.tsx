import Link from 'next/link'
import { ArrowLeft, Shield, Lock, Eye, FileCheck, CheckCircle2, AlertTriangle, Key } from 'lucide-react'

export default function SecurityPage() {
  const features = [
    'Role-Based Access Control (RBAC)',
    'End-to-end encryption',
    'JWT token authentication',
    'Rate limiting & DDoS protection',
    'Comprehensive audit logs',
    'IP whitelisting',
    'Two-factor authentication (2FA)',
    'Session management',
    'Password encryption (bcrypt)',
    'GDPR & CCPA compliance',
    'Data retention policies',
    'Automated security scanning',
  ]

  const securityLayers = [
    {
      title: 'Authentication',
      description: 'Multi-layered authentication with JWT tokens, 2FA, and session management',
      icon: Key,
    },
    {
      title: 'Authorization',
      description: 'Granular RBAC with custom roles: Admin, Manager, Agent, and Customer',
      icon: Lock,
    },
    {
      title: 'Audit Trails',
      description: 'Complete activity logging for compliance and security monitoring',
      icon: FileCheck,
    },
    {
      title: 'Threat Protection',
      description: 'Real-time threat detection with rate limiting and IP blocking',
      icon: AlertTriangle,
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
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white">
            Enterprise Security
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Bank-level security designed for enterprise. Protect your data and your customers
            with military-grade encryption and compliance-ready features.
          </p>
        </div>
      </section>

      {/* Security Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center gap-3 mb-12">
            <Eye className="w-8 h-8 text-blue-600" />
            <h2 className="text-3xl font-bold text-center">Security Features</h2>
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

      {/* Security Layers */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Multi-Layer Protection</h2>
          <div className="grid md:grid-cols-2 gap-8">
            {securityLayers.map((layer, index) => {
              const Icon = layer.icon
              return (
                <div
                  key={index}
                  className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg"
                >
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{layer.title}</h3>
                  <p className="text-gray-600 dark:text-gray-400">{layer.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Compliance Badges */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Compliance Ready</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg text-center">
              <div className="text-3xl mb-2">🔒</div>
              <div className="font-semibold">SOC 2</div>
              <div className="text-sm text-gray-500 mt-1">Type II</div>
            </div>
            <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg text-center">
              <div className="text-3xl mb-2">🇪🇺</div>
              <div className="font-semibold">GDPR</div>
              <div className="text-sm text-gray-500 mt-1">Compliant</div>
            </div>
            <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg text-center">
              <div className="text-3xl mb-2">🔐</div>
              <div className="font-semibold">ISO 27001</div>
              <div className="text-sm text-gray-500 mt-1">Certified</div>
            </div>
            <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg text-center">
              <div className="text-3xl mb-2">✅</div>
              <div className="font-semibold">CCPA</div>
              <div className="text-sm text-gray-500 mt-1">Compliant</div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-2xl p-12 shadow-xl">
          <div className="grid grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-blue-600">99.9%</div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">Uptime SLA</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-600">256-bit</div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">Encryption</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-green-600">24/7</div>
              <div className="text-gray-600 dark:text-gray-400 mt-2">Monitoring</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <Shield className="w-12 h-12 mx-auto mb-4" />
          <h2 className="text-3xl font-bold mb-4">Security You Can Trust</h2>
          <p className="text-xl mb-8 text-blue-100">
            Enterprise-grade protection for your most sensitive data
          </p>
          <Link
            href="/auth/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition text-lg font-semibold"
          >
            Start Secure Trial
          </Link>
        </div>
      </section>
    </div>
  )
}
