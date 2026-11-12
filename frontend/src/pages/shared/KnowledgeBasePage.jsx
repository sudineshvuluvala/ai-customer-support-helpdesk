import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { knowledgeService } from '../../services/knowledgeService'
import { useFetch, useDebounce } from '../../hooks/useFetch'
import SearchBar from '../../components/SearchBar'
import Loading from '../../components/Loading'
import ErrorMessage from '../../components/ErrorMessage'
import { fmtDate } from '../../utils/format'

export default function KnowledgeBasePage({ role = 'customer' }) {
  const { id } = useParams()
  const [search, setSearch] = useState('')
  const [selectedCat, setSelectedCat] = useState('')
  const debouncedSearch = useDebounce(search, 300)

  const { data: categories } = useFetch(knowledgeService.categories)

  // If viewing a single article
  if (id) {
    return <ArticleView id={id} role={role} />
  }

  return (
    <ArticleIndex
      role={role}
      categories={categories}
      search={search}
      setSearch={setSearch}
      debouncedSearch={debouncedSearch}
      selectedCat={selectedCat}
      setSelectedCat={setSelectedCat}
    />
  )
}

function ArticleIndex({ role, categories, search, setSearch, debouncedSearch, selectedCat, setSelectedCat }) {
  const { data, loading, error, reload } = useFetch(
    () => knowledgeService.articles({ q: debouncedSearch || undefined, category_id: selectedCat || undefined }),
    [debouncedSearch, selectedCat]
  )

  return (
    <div>
      <div className="mb-4">
        <h1 className="h4 fw-bold mb-1">Knowledge Base &amp; Help Center</h1>
        <p className="text-muted small">Explore answers, troubleshooting guides, and step-by-step instructions.</p>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-md-6">
          <SearchBar value={search} onChange={setSearch} placeholder="Search articles by title or keyword..." />
        </div>
        <div className="col-md-4">
          <select className="form-select" value={selectedCat} onChange={(e) => setSelectedCat(e.target.value)}>
            <option value="">All Categories</option>
            {categories?.map((c) => (
              <option key={c.category_id} value={c.category_id}>{c.category_name}</option>
            ))}
          </select>
        </div>
      </div>

      {loading && <Loading text="Fetching articles..." />}
      {error && <ErrorMessage error={error} onRetry={reload} />}

      <div className="row g-3">
        {data?.data?.map((art) => (
          <div key={art.article_id} className="col-md-6">
            <div className="card shadow-sm border-0 h-100 p-3">
              <span className="badge bg-light text-primary border align-self-start mb-2">{art.category?.category_name}</span>
              <h2 className="h6 fw-bold mb-2">
                <Link to={`/${role}/knowledge/${art.article_id}`} className="text-decoration-none text-dark">
                  {art.title}
                </Link>
              </h2>
              <p className="small text-secondary flex-grow-1">{art.summary}</p>
              <div className="small text-muted border-top pt-2 mt-2">
                Updated {fmtDate(art.updated_at)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ArticleView({ id, role }) {
  const { data: article, loading, error, reload } = useFetch(() => knowledgeService.article(id), [id])

  if (loading) return <Loading text="Loading article..." />
  if (error) return <ErrorMessage error={error} onRetry={reload} />

  return (
    <div className="row justify-content-center">
      <div className="col-lg-9">
        <Link to={`/${role}/knowledge`} className="btn btn-link btn-sm p-0 mb-3 text-decoration-none">
          <i className="bi bi-arrow-left me-1" />Back to Knowledge Base
        </Link>
        <div className="card shadow-sm border-0 mb-4">
          <div className="card-body p-4">
            <span className="badge bg-light text-primary border mb-2">{article.category?.category_name}</span>
            <h1 className="h3 fw-bold mb-3">{article.title}</h1>
            <div className="small text-muted mb-4 border-bottom pb-2">
              Published: {fmtDate(article.created_at)} · Last updated: {fmtDate(article.updated_at)}
            </div>
            <div className="article-content" style={{ whiteSpace: 'pre-wrap', lineHeight: '1.7' }}>
              {article.content}
            </div>
          </div>
        </div>

        {/* Related Articles */}
        {article.related?.length > 0 && (
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white fw-bold">Related Help Articles</div>
            <div className="list-group list-group-flush">
              {article.related.map((r) => (
                <Link
                  key={r.article_id}
                  to={`/${role}/knowledge/${r.article_id}`}
                  className="list-group-item list-group-item-action py-3"
                >
                  <div className="fw-semibold text-primary">{r.title}</div>
                  <div className="small text-muted">{r.summary}</div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
