import { useEffect, useMemo, useState } from 'react'
import { api, CoursesResponse, Course, fetchMeta } from '../api'

// 🔹 Spinner Component
function Spinner() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
      <div
        className="spinner"
        style={{
          width: '32px',
          height: '32px',
          border: '4px solid rgba(255, 255, 255, 0.2)',
          borderTop: '4px solid #60a5fa',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }}
        aria-label="Loading"
      />
    </div>
  )
}

// 🔹 Empty State Component
function EmptyState({ message }: { message?: string }) {
  return (
    <div
      className="card"
      style={{
        textAlign: 'center',
        padding: '40px 20px',
        color: '#94a3b8',
      }}
    >
      <div style={{ fontSize: '40px', marginBottom: '12px' }}>🔍</div>
      <h3 style={{ margin: '0 0 8px 0' }}>No Courses Found</h3>
      <p style={{ fontSize: '14px' }}>
        {message || 'Try adjusting filters or search keywords.'}
      </p>
    </div>
  )
}

type Filters = {
  department?: string
  level?: string
  delivery_mode?: string
  min_rating?: number
  max_fee?: number
  q?: string
}

function useCompare() {
  const [ids, setIds] = useState<number[]>(() => {
    try {
      return JSON.parse(localStorage.getItem('compare_ids') || '[]')
    } catch {
      return []
    }
  })
  useEffect(() => {
    localStorage.setItem('compare_ids', JSON.stringify(ids))
  }, [ids])
  const toggle = (id: number) =>
    setIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  return { ids, toggle }
}

export default function SearchPage() {
  const [meta, setMeta] = useState<{
    departments: string[]
    levels: string[]
    delivery_modes: string[]
  }>()
  const [filters, setFilters] = useState<Filters>({})
  const [page, setPage] = useState(1)
  const [data, setData] = useState<CoursesResponse>()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { ids, toggle } = useCompare()

  useEffect(() => {
    ;(async () => setMeta(await fetchMeta()))()
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    async function run() {
      setLoading(true)
      setError(null)
      try {
        const params: any = { page, page_size: 8, ...filters }
        const { data } = await api.get('/api/courses', {
          params,
          signal: controller.signal,
        })
        setData(data)
      } catch (err: any) {
        setError(err?.message || 'Failed to load')
      } finally {
        setLoading(false)
      }
    }
    run()
    return () => controller.abort()
  }, [filters, page])

  const totalPages = useMemo(
    () => (data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1),
    [data]
  )

  return (
    <div className="grid">
      {/* Filters Sidebar */}
      <div className="col-4">
        <div className="card" role="complementary">
          <h3>Filters</h3>

          {/* Search */}
          <div className="mt-3 field">
            <label htmlFor="search">Search</label>
            <input
              id="search"
              placeholder="e.g. data, statistics"
              value={filters.q ?? ''}
              onChange={e => {
                setPage(1)
                setFilters(f => ({ ...f, q: e.target.value || undefined }))
              }}
            />
          </div>

          {/* Department */}
          <div className="mt-3 field">
            <label htmlFor="dept">Department</label>
            <select
              id="dept"
              value={filters.department ?? ''}
              onChange={e => {
                setPage(1)
                const v = e.target.value
                setFilters(f => ({ ...f, department: v === '' ? undefined : v }))
              }}
            >
              <option value="">Any</option>
              {meta?.departments.map(d => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          {/* Level */}
          <div className="mt-3 field">
            <label htmlFor="level">Level</label>
            <select
              id="level"
              value={filters.level ?? ''}
              onChange={e => {
                setPage(1)
                const v = e.target.value
                setFilters(f => ({ ...f, level: v === '' ? undefined : v }))
              }}
            >
              <option value="">Any</option>
              {meta?.levels.map(d => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          {/* Delivery Mode */}
          <div className="mt-3 field">
            <label htmlFor="delivery">Delivery Mode</label>
            <select
              id="delivery"
              value={filters.delivery_mode ?? ''}
              onChange={e => {
                setPage(1)
                const v = e.target.value
                setFilters(f => ({
                  ...f,
                  delivery_mode: v === '' ? undefined : v,
                }))
              }}
            >
              <option value="">Any</option>
              {meta?.delivery_modes.map(d => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          {/* Min Rating */}
          <div className="mt-3 field">
            <label htmlFor="minRating">Min Rating</label>
            <input
              id="minRating"
              type="number"
              step="0.1"
              min="0"
              max="5"
              value={filters.min_rating ?? ''}
              onChange={e => {
                setPage(1)
                const v = e.target.value
                setFilters(f => ({
                  ...f,
                  min_rating: v === '' ? undefined : Number(v),
                }))
              }}
            />
          </div>

          {/* Max Fee */}
          <div className="mt-3 field">
            <label htmlFor="maxFee">Max Fee (INR)</label>
            <input
              id="maxFee"
              type="number"
              min="0"
              value={filters.max_fee ?? ''}
              onChange={e => {
                setPage(1)
                const v = e.target.value
                setFilters(f => ({
                  ...f,
                  max_fee: v === '' ? undefined : Number(v),
                }))
              }}
            />
          </div>

          {/* 🔹 Clear All Filters */}
          <div className="mt-4">
            <button
              className="secondary"
              style={{ width: '100%' }}
              onClick={() => {
                setFilters({})
                setPage(1)
              }}
              disabled={Object.keys(filters).length === 0}
            >
              Clear All Filters
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="col-8">
        <div className="row">
          <h2 id="resultsHeading">Results</h2>
          <span className="badge">{data?.total ?? 0} found</span>
          <span className="badge">Compare: {ids.length}</span>
        </div>

        {/* 🔹 Active Filters Pills */}
        <div
          className="mt-2"
          aria-live="polite"
          style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}
        >
          {Object.entries(filters).map(([key, value]) =>
            value ? (
              <span key={key} className="filter-pill">
                {key}: {value}
                <button
                  aria-label={`Remove filter ${key}`}
                  onClick={() => {
                    setFilters(f => ({ ...f, [key]: undefined }))
                    setPage(1)
                  }}
                >
                  ×
                </button>
              </span>
            ) : null
          )}
        </div>

        <div className="mt-3">
          {loading && <Spinner />}
          {error && (
            <div className="card" role="alert">
              Error: {error}
            </div>
          )}
          {!loading &&
            data?.items.map((c: Course) => (
              <div key={c.id} className="card mt-2">
                <div
                  className="row"
                  style={{ justifyContent: 'space-between' }}
                >
                  <div>
                    <div style={{ fontWeight: 600 }}>{c.course_name}</div>
                    <div className="mt-2">
                      <span className="badge">{c.department}</span>{' '}
                      <span className="badge">{c.level}</span>{' '}
                      <span className="badge">{c.delivery_mode}</span>{' '}
                      <span className="badge">⭐ {c.rating.toFixed(1)}</span>{' '}
                      <span className="badge">
                        ₹ {c.tuition_fee_inr.toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="row">
                    <button
                      onClick={() => toggle(c.course_id)}
                      className="primary"
                    >
                      {ids.includes(c.id) ? 'Remove' : 'Add to compare'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          {!loading && data?.items.length === 0 && <EmptyState />}
        </div>

        {/* Pagination */}
        <div className="row mt-4">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            Prev
          </button>
          <div className="badge" aria-live="polite">
            Page {page} / {totalPages}
          </div>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  )
}
