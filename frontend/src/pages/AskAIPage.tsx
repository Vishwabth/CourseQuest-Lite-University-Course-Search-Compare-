import { useState } from 'react'
import { api, CoursesResponse } from '../api'

export default function AskAIPage() {
  const [question, setQuestion] = useState('UG online CS courses under 50k with rating 4+')
  const [loading, setLoading] = useState(false)
  const [parsed, setParsed] = useState<any>()
  const [data, setData] = useState<CoursesResponse>()
  const [message, setMessage] = useState<string>('')

  async function handleAsk() {
    setLoading(true); setMessage(''); setParsed(undefined); setData(undefined)
    try {
      const { data } = await api.post('/api/ask', { question })
      setParsed(data.parsed_filters)
      setData(data.results)
      if (data.message) setMessage(data.message)
    } catch (err: any) {
      setMessage(err?.message || 'Failed to ask')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid">
      <div className="col-12">
        <div className="card">
          <h2>Ask AI About Courses</h2>
          <div className="row mt-3" style={{ gap: 8 }}>
            <input
              style={{ flex: 1 }}
              placeholder="Type your question..."
              value={question}
              onChange={e => setQuestion(e.target.value)}
            />
            <button className="primary" onClick={handleAsk}>
              {loading ? 'Thinking…' : 'Ask'}
            </button>
          </div>
          {parsed && (
            <div className="mt-3">
              <div className="badge">Parsed Filters</div>
              <pre className="mono" style={{ whiteSpace: 'pre-wrap' }}>
                {JSON.stringify(parsed, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
      <div className="col-12 mt-3">
        {message && <div className="card">{message}</div>}
        {data && data.items.length > 0 && (
          <div className="card">
            <h3>Results</h3>
            {data.items.map(c => (
              <div key={c.id} className="mt-2">
                <div style={{ fontWeight: 600 }}>{c.course_name}</div>
                <div className="mt-2">
                  <span className="badge">{c.department}</span>{' '}
                  <span className="badge">{c.level}</span>{' '}
                  <span className="badge">{c.delivery_mode}</span>{' '}
                  <span className="badge">⭐ {c.rating.toFixed(1)}</span>{' '}
                  <span className="badge">₹ {c.tuition_fee_inr.toLocaleString()}</span>{' '}
                  <span className="badge">{c.credits} credits</span>{' '}
                  <span className="badge">{c.duration_weeks} weeks</span>{' '}
                  <span className="badge">📅 {c.year_offered}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
