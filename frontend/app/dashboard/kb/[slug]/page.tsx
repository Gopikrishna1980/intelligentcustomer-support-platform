'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { kbApi } from '@/lib/api'
import { ArrowLeft, Eye, ThumbsUp, ThumbsDown, CheckCircle } from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'
import ReactMarkdown from 'react-markdown'
import Link from 'next/link'

export default function ArticlePage() {
  const params = useParams()
  const slug = params.slug as string
  
  const [article, setArticle] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [voted, setVoted] = useState(false)

  useEffect(() => {
    fetchArticle()
  }, [slug])

  const fetchArticle = async () => {
    try {
      const response = await kbApi.getArticle(slug)
      setArticle(response.data)
    } catch (error) {
      console.error('Failed to fetch article:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleVote = async (helpful: boolean) => {
    if (voted) return

    try {
      await kbApi.voteArticle(article.id, helpful)
      setVoted(true)
      // Update local state
      if (helpful) {
        setArticle({
          ...article,
          helpful_count: (article.helpful_count || 0) + 1,
        })
      } else {
        setArticle({
          ...article,
          not_helpful_count: (article.not_helpful_count || 0) + 1,
        })
      }
    } catch (error) {
      console.error('Failed to vote:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading article...</p>
        </div>
      </div>
    )
  }

  if (!article) {
    return (
      <div className="text-center py-12">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Article not found
        </h3>
        <Link href="/dashboard/kb" className="text-blue-600 hover:text-blue-700">
          Back to Knowledge Base
        </Link>
      </div>
    )
  }

  const helpfulTotal = (article.helpful_count || 0) + (article.not_helpful_count || 0)
  const helpfulPercentage = helpfulTotal > 0
    ? Math.round(((article.helpful_count || 0) / helpfulTotal) * 100)
    : 0

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          href="/dashboard/kb"
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          {article.is_featured && (
            <span className="inline-block px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 text-xs font-medium rounded mb-2">
              Featured Article
            </span>
          )}
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {article.title}
          </h1>
        </div>
      </div>

      {/* Meta Info */}
      <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
        <div className="flex items-center gap-1">
          <Eye className="w-4 h-4" />
          <span>{article.view_count || 0} views</span>
        </div>
        <span>•</span>
        <div className="flex items-center gap-1">
          <ThumbsUp className="w-4 h-4" />
          <span>{helpfulPercentage}% found this helpful</span>
        </div>
        <span>•</span>
        <span>Last updated {formatRelativeTime(article.updated_at)}</span>
      </div>

      {/* Content */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
        {article.summary && (
          <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-600 rounded">
            <p className="text-gray-700 dark:text-gray-300">
              {article.summary}
            </p>
          </div>
        )}

        <div className="prose prose-blue dark:prose-invert max-w-none">
          <ReactMarkdown>{article.content}</ReactMarkdown>
        </div>
      </div>

      {/* Vote Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Was this article helpful?
        </h3>
        {voted ? (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle className="w-5 h-5" />
            <span>Thank you for your feedback!</span>
          </div>
        ) : (
          <div className="flex gap-4">
            <button
              onClick={() => handleVote(true)}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 border-2 border-green-600 text-green-600 rounded-lg hover:bg-green-50 dark:hover:bg-green-900/20 transition"
            >
              <ThumbsUp className="w-5 h-5" />
              Yes, helpful
            </button>
            <button
              onClick={() => handleVote(false)}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 border-2 border-red-600 text-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition"
            >
              <ThumbsDown className="w-5 h-5" />
              Not helpful
            </button>
          </div>
        )}
      </div>

      {/* Related Articles */}
      {article.category && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            More from {article.category.name}
          </h3>
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            Explore more articles in this category
          </p>
          <Link
            href={`/dashboard/kb?category=${article.category_id}`}
            className="inline-block mt-4 text-blue-600 hover:text-blue-700 font-medium"
          >
            View all →
          </Link>
        </div>
      )}
    </div>
  )
}
