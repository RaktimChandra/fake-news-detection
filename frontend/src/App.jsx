import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {  
  Shield, 
  AlertTriangle, 
  CheckCircle2, 
  Zap, 
  TrendingUp,
  Search,
  Link2,
  FileText,
  BarChart3,
  Clock,
  Target
} from 'lucide-react'
import axios from 'axios'
import AnalysisPanel from './components/AnalysisPanel'
import ResultCard from './components/ResultCard'
import StatsBar from './components/StatsBar'
import HistoryPanel from './components/HistoryPanel'
import AnalyticsDashboard from './components/AnalyticsDashboard'

function App() {
  const [activeTab, setActiveTab] = useState('url')
  const [urlInput, setUrlInput] = useState('')
  const [textInput, setTextInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [activeView, setActiveView] = useState('analysis') // 'analysis' or 'analytics'

  const handleAnalyze = async () => {
    setError(null)
    setLoading(true)
    
    try {
      const payload = {
        url: activeTab === 'url' ? urlInput : '',
        text: activeTab === 'text' ? textInput : ''
      }
      
      const response = await axios.post('/analyze', payload)
      
      const newResult = {
        ...response.data,
        id: Date.now(),
        timestamp: new Date().toISOString()
      }
      
      setResult(newResult)
      setHistory(prev => [newResult, ...prev.slice(0, 9)]) // Keep last 10
      
    } catch (err) {
      setError(err.response?.data?.error || 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse-slow delay-1000" />
      </div>

      {/* Main Content */}
      <div className="relative z-10">
        {/* Header */}
        <motion.header 
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          className="pt-8 pb-6"
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", duration: 0.6 }}
                className="inline-block"
              >
                <Shield className="w-20 h-20 text-purple-400 mx-auto mb-4 drop-shadow-2xl animate-float" />
              </motion.div>
              
              <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 animate-gradient">
                  Fake News Detector
                </span>
              </h1>
              
              <p className="text-xl text-purple-200/80 max-w-2xl mx-auto">
                Powered by BERT AI • 2015-2025 Data • Real-Time Analysis • Advanced Analytics
              </p>
            </div>
          </div>
        </motion.header>

        {/* Stats Bar */}
        <StatsBar />

        {/* View Toggle */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-4">
          <div className="flex justify-center gap-4">
            <button
              onClick={() => setActiveView('analysis')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center gap-2 ${
                activeView === 'analysis'
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/50'
                  : 'bg-white/5 text-purple-200 hover:bg-white/10'
              }`}
            >
              <Search className="w-5 h-5" />
              Analysis
            </button>
            <button
              onClick={() => setActiveView('analytics')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center gap-2 ${
                activeView === 'analytics'
                  ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/50'
                  : 'bg-white/5 text-purple-200 hover:bg-white/10'
              }`}
            >
              <BarChart3 className="w-5 h-5" />
              Analytics
            </button>
          </div>
        </div>

        {/* Main Content Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {activeView === 'analysis' ? (
            /* Analysis View */
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Analysis Panel - Left/Center */}
              <div className="lg:col-span-2">
                <AnalysisPanel 
                  activeTab={activeTab}
                  setActiveTab={setActiveTab}
                  urlInput={urlInput}
                  setUrlInput={setUrlInput}
                  textInput={textInput}
                  setTextInput={setTextInput}
                  loading={loading}
                  onAnalyze={handleAnalyze}
                  error={error}
                />
                
                {/* Result Card */}
                <AnimatePresence mode="wait">
                  {result && (
                    <ResultCard result={result} />
                  )}
                </AnimatePresence>
              </div>

              {/* Sidebar - Right */}
              <div className="lg:col-span-1">
                <HistoryPanel history={history} onSelect={(item) => setResult(item)} />
              </div>
            </div>
          ) : (
            /* Analytics View */
            <AnalyticsDashboard history={history} />
          )}
        </div>

        {/* Features Section */}
        <motion.section 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { icon: Zap, title: 'Lightning Fast', desc: 'Results in under 1 second' },
              { icon: Target, title: 'Highly Accurate', desc: '94.2% precision rate' },
              { icon: TrendingUp, title: 'Always Learning', desc: 'Updated with 2024-2025 data' }
            ].map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 + idx * 0.1 }}
                className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10 hover:border-purple-400/50 transition-all duration-300"
              >
                <feature.icon className="w-12 h-12 text-purple-400 mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-purple-200/60">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Footer */}
        <footer className="border-t border-white/10 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <p className="text-center text-purple-200/60">
              Built with React • Powered by BERT AI • © 2024
            </p>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default App
