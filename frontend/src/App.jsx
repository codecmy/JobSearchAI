import { useEffect, useState } from 'react'
import axios from 'axios'
import './App.css'

const api = axios.create({ baseURL: 'http://localhost:8000/api/v1' })

function App() {
  const [token, setToken] = useState(localStorage.getItem('careeros_token'))
  const [view, setView] = useState('discover')
  const [jobs, setJobs] = useState([])
  const [profile, setProfile] = useState({ headline: '', summary: '', skills: '', location: '', target_role: '' })
  const [chat, setChat] = useState([])
  const [message, setMessage] = useState('')
  const [applications, setApplications] = useState([])

  useEffect(() => {
    if (token) {
      api.defaults.headers.common.Authorization = `Bearer ${token}`
      loadData()
    }
  }, [token])

  async function loadData() {
    const [jobRes, profileRes, appRes] = await Promise.all([
      api.get('/jobs'),
      api.get('/candidates/me'),
      api.get('/applications'),
    ])
    setJobs(jobRes.data)
    setProfile(profileRes.data)
    setApplications(appRes.data)
  }

  async function login(mode, event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const payload = { email: form.get('email'), password: form.get('password'), full_name: form.get('name') || '' }
    try {
      const res = await api.post(`/auth/${mode}`, payload)
      localStorage.setItem('careeros_token', res.data.access_token)
      setToken(res.data.access_token)
    } catch (error) {
      alert(error.response?.data?.detail || 'Unable to continue')
    }
  }

  async function saveJob(jobId) {
    await api.post('/applications', { job_id: jobId })
    const res = await api.get('/applications')
    setApplications(res.data)
  }

  async function sendMessage(event) {
    event.preventDefault()
    if (!message.trim()) return
    const text = message
    setMessage('')
    setChat((items) => [...items, { role: 'user', text }])
    const res = await api.post('/agent/chat', { message: text })
    setChat((items) => [...items, { role: 'agent', text: res.data.response }])
  }

  async function saveProfile(event) {
    event.preventDefault()
    await api.put('/candidates/me', profile)
    alert('Profile saved')
  }

  if (!token) {
    return (
      <main className="auth-page">
        <nav className="auth-nav"><div className="brand">Career<span>OS</span></div></nav>
        <section className="auth-card">
          <div className="auth-copy">
            <p className="eyebrow">YOUR CAREER, PERSONALLY ENGINEERED</p>
            <h1>Find work that<br/><em>fits your life.</em></h1>
            <p>CareerOS learns your experience, goals, and preferences to surface opportunities worth pursuing.</p>
          </div>
          <AuthForm onLogin={login} />
        </section>
      </main>
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">Career<span>OS</span></div>
        <nav>
          {['discover', 'agent', 'profile', 'applications'].map((item) => (
            <button key={item} className={view === item ? 'active' : ''} onClick={() => setView(item)}>
              {item === 'discover' ? 'Discover' : item === 'agent' ? 'Career Agent' : item === 'profile' ? 'My Profile' : 'Applications'}
            </button>
          ))}
        </nav>
        <button className="logout" onClick={() => { localStorage.removeItem('careeros_token'); setToken(null) }}>Sign out</button>
      </aside>
      <main className="main">
        {view === 'discover' && <Discover jobs={jobs} saveJob={saveJob} />}
        {view === 'agent' && <Agent chat={chat} message={message} setMessage={setMessage} sendMessage={sendMessage} />}
        {view === 'profile' && <Profile profile={profile} setProfile={setProfile} saveProfile={saveProfile} />}
        {view === 'applications' && <Applications applications={applications} />}
      </main>
    </div>
  )
}

function AuthForm({ onLogin }) {
  const [mode, setMode] = useState('login')
  return (
    <form className="auth-form" onSubmit={(event) => onLogin(mode, event)}>
      <h2>{mode === 'login' ? 'Welcome back' : 'Create your CareerOS'}</h2>
      {mode === 'register' && <label>Full name<input name="name" required /></label>}
      <label>Email address<input type="email" name="email" required placeholder="you@example.com" /></label>
      <label>Password<input type="password" name="password" required minLength="6" /></label>
      <button className="primary" type="submit">{mode === 'login' ? 'Sign in' : 'Create account'}</button>
      <button type="button" className="text-button" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
        {mode === 'login' ? 'New here? Create an account' : 'Already have an account? Sign in'}
      </button>
    </form>
  )
}

function Discover({ jobs, saveJob }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(jobs)
  useEffect(() => setResults(jobs), [jobs])

  async function runSearch(event) {
    event.preventDefault()
    const res = await api.post('/jobs/search', { query })
    setResults(res.data)
  }

  return (
    <section>
      <header className="page-header"><div><p className="eyebrow">OPPORTUNITY FEED</p><h1>Discover roles</h1></div></header>
      <form className="search-bar" onSubmit={runSearch}>
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Try backend engineering, Kafka, AI..." />
        <button className="primary">Search</button>
      </form>
      <div className="job-grid">
        {results.map((job) => (
          <article className="job-card" key={job.id}>
            <div className="job-top"><div className="company-mark">{job.company[0]}</div><div><h3>{job.title}</h3><p>{job.company}</p></div><strong>{job.score ? `${Math.round(job.score * 100)}%` : 'New'}</strong></div>
            <p className="meta">{job.location} · {job.employment_type}</p>
            <p className="job-description">{job.description}</p>
            <div className="chips">{job.skills?.split(',').slice(0, 5).map((skill) => <span key={skill}>{skill.trim()}</span>)}</div>
            {job.explanation && <p className="explanation">{job.explanation}</p>}
            <button className="save-button" onClick={() => saveJob(job.id)}>Save role</button>
          </article>
        ))}
      </div>
    </section>
  )
}

function Agent({ chat, message, setMessage, sendMessage }) {
  return (
    <section className="agent-page">
      <header className="page-header"><div><p className="eyebrow">YOUR CAREER COPILOT</p><h1>Career Agent</h1></div></header>
      <div className="chat-window">
        {chat.length === 0 && <div className="chat-empty"><h2>What should we work on?</h2><p>Ask about matches, preferences, your resume, or next steps.</p></div>}
        {chat.map((item, index) => <div key={index} className={`bubble ${item.role}`}>{item.text}</div>)}
      </div>
      <form className="chat-form" onSubmit={sendMessage}><input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Ask your career agent..." /><button className="primary">Send</button></form>
    </section>
  )
}

function Profile({ profile, setProfile, saveProfile }) {
  return (
    <section>
      <header className="page-header"><div><p className="eyebrow">CANDIDATE PROFILE</p><h1>Build your career profile</h1></div></header>
      <form className="profile-form" onSubmit={saveProfile}>
        <label>Professional headline<input value={profile.headline || ''} onChange={(e) => setProfile({...profile, headline: e.target.value})} placeholder="Backend engineer | Python | Distributed systems" /></label>
        <label>Target role<input value={profile.target_role || ''} onChange={(e) => setProfile({...profile, target_role: e.target.value})} /></label>
        <label>Location<input value={profile.location || ''} onChange={(e) => setProfile({...profile, location: e.target.value})} placeholder="Bangalore, India" /></label>
        <label>Skills<textarea value={profile.skills || ''} onChange={(e) => setProfile({...profile, skills: e.target.value})} /></label>
        <label>Profile summary<textarea value={profile.summary || ''} onChange={(e) => setProfile({...profile, summary: e.target.value})} /></label>
        <button className="primary" type="submit">Save profile</button>
      </form>
    </section>
  )
}

function Applications({ applications }) {
  return (
    <section>
      <header className="page-header"><div><p className="eyebrow">APPLICATION PIPELINE</p><h1>Your opportunities</h1></div></header>
      {applications.length === 0 ? <div className="empty-state">Save a role to begin tracking it.</div> :
        <div className="application-list">{applications.map((item) => <article key={item.id}><div className="company-mark">{item.job.company[0]}</div><div><h3>{item.job.title}</h3><p>{item.job.company}</p></div><span className="status">{item.status}</span></article>)}</div>}
    </section>
  )
}

export default App
