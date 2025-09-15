import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL?.replace(/\/$/,'') || 'http://localhost:8000'
export const api = axios.create({ baseURL })

export type Course = {
  id: number
  course_id: number
  course_name: string
  department: string
  level: 'UG' | 'PG'
  delivery_mode: 'online' | 'offline' | 'hybrid'
  credits: number
  duration_weeks: number
  rating: number
  tuition_fee_inr: number
  year_offered: number
}

export type CoursesResponse = {
  items: Course[]
  total: number
  page: number
  page_size: number
}

export async function fetchMeta() {
  const { data } = await api.get('/api/meta')
  return data as { departments: string[]; levels: string[]; delivery_modes: string[] }
}
