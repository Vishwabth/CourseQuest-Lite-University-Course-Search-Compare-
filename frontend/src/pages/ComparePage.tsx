import { useEffect, useState } from 'react'
import { api, Course } from '../api'

export default function ComparePage(){
  const [ids, setIds] = useState<number[]>(() => {
    try { return JSON.parse(localStorage.getItem('compare_ids')||'[]') } catch { return [] }
  })
  const [items, setItems] = useState<Course[]>([])

  useEffect(() => {
    async function run(){
      if(ids.length===0){ setItems([]); return }
      const { data } = await api.get('/api/compare', { params: { ids: ids.join(',') }})
      setItems(data)
    }
    run()
  }, [ids])

  const remove = (id:number) => {
    const next = ids.filter(x=>x!==id); setIds(next); localStorage.setItem('compare_ids', JSON.stringify(next))
  }

  return (
    <div>
      <h2>Compare Courses</h2>
      {items.length===0 && <div className="card mt-3">Select courses on the Search page to compare.</div>}
      {items.length>0 && (
        <div className="card mt-3">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th><th>Dept</th><th>Level</th><th>Mode</th><th>Credits</th><th>Weeks</th><th>Rating</th><th>Fee (₹)</th><th>Year</th><th></th>
              </tr>
            </thead>
            <tbody>
              {items.map(c=> (
                <tr key={c.id}>
                  <td>{c.course_name}</td>
                  <td>{c.department}</td>
                  <td>{c.level}</td>
                  <td>{c.delivery_mode}</td>
                  <td>{c.credits}</td>
                  <td>{c.duration_weeks}</td>
                  <td>{c.rating.toFixed(1)}</td>
                  <td>{c.tuition_fee_inr.toLocaleString()}</td>
                  <td>{c.year_offered}</td>
                  <td><button onClick={()=>remove(c.id)}>Remove</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
