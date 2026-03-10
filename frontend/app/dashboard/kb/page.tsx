'use client'

import { useEffect, useState } from 'react'
import { kbApi } from '@/lib/api'
import { Search, BookOpen, Eye, ThumbsUp, ThumbsDown } from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'
import Link from 'next/link'

export default function KnowledgeBasePage() {
  const [articles, setArticles] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')

  useEffect(() => {
    fetchData()
  }, [selectedCategory])

  const fetchData = async () => {
    try {
      const [articlesRes, categoriesRes] = await Promise.all([
        kbApi.listArticles({ category_id: selectedCategory || undefined, page: 1, page_size: 20 }),
        kbApi.listCategories(),
      ])
      setArticles(articlesRes.data.items || [])
      setCategories(categoriesRes.data || [])
    } catch (error) {
      console.error('Failed to fetch KB data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setLoading(true)
    try {
      const response = await kbApi.searchArticles(searchQuery, selectedCategory || undefined)
      setArticles(response.data.results || [])
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Knowledge Base
        </h1>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
        <div className="flex gap-4">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search articles..."
              className="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
          >
            Search
          </button>
        </div>
      </form>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Categories Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
            <h2 className="font-semibold text-gray-900 dark:text-white mb-4">
              Categories
            </h2>
            <div className="space-y-2">
              <button
                onClick={() => setSelectedCategory('')}
                className={`w-full text-left px-3 py-2 rounded-lg transition ${
                  !selectedCategory
                    ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                All Articles
              </button>
              {categories.map((category: any) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition ${
                    selectedCategory === category.id
                      ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span>{category.name}</span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {category.article_count || 0}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Articles Grid */}
        <div className="lg:col-span-3">
          {loading ? (
            <div className="grid gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-32 bg-gray-200 dark:bg-gray-800 rounded-lg animate-pulse"></div>
              ))}
            </div>
          ) : articles.length === 0 ? (
            <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
              <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No articles found
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Try adjusting your search or category filter
              </p>
            </div>
          ) : (
            <div className="grid gap-4">
              {articles.map((article: any) => {
                const helpfulTotal = (article.helpful_count || 0) + (article.not_helpful_count || 0)
                const helpfulPercentage = helpfulTotal > 0
                  ? Math.round(((article.helpful_count || 0) / helpfulTotal) * 100)
                  : 0

                return (
                  <Link
                    key={article.id}
                    href={`/dashboard/kb/${article.slug}`}
                    className="block bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition p-6"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                          {article.title}
                        </h3>
                        {article.summary && (
                          <p className="text-gray-600 dark:text-gray-400 text-sm line-clamp-2">
                            {article.summary}
                          </p>
                        )}
                      </div>
                      {article.is_featured && (
                        <span className="ml-4 px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 text-xs font-medium rounded">
                          Featured
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <div className="flex items-center gap-1">
                        <Eye className="w-4 h-4" />
                        <span>{article.view_count || 0} views</span>
                      </div>
                      <span>•</span>
                      <div className="flex items-center gap-1">
                        <ThumbsUp className="w-4 h-4" />
                        <span>{helpfulPercentage}% helpful</span>
                      </div>
                      <span>•</span>
                      <span>Updated {formatRelativeTime(article.updated_at)}</span>
                    </div>
                  </Link>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
