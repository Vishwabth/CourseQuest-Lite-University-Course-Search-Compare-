import { NavLink, Route, Routes, useLocation } from 'react-router-dom'
import SearchPage from './pages/SearchPage'
import ComparePage from './pages/ComparePage'
import AskAIPage from './pages/AskAIPage'

export default function App(){
  const loc = useLocation()
  return (
    <div>
      <div className="nav">
        <div className="inner">
          <div className="brand">CourseQuest Lite</div>
          <div className="tabs">
            <NavLink className={({isActive}) => 'tab'+(isActive? ' active':'')} to="/">Search</NavLink>
            <NavLink className={({isActive}) => 'tab'+(isActive? ' active':'')} to="/compare">Compare</NavLink>
            <NavLink className={({isActive}) => 'tab'+(isActive? ' active':'')} to="/ask">Ask AI</NavLink>
          </div>
        </div>
      </div>
      <div className="container">
        <Routes location={loc}>
          <Route path="/" element={<SearchPage />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/ask" element={<AskAIPage />} />
        </Routes>
      </div>
    </div>
  )
}
