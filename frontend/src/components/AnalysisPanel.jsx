import { motion } from 'framer-motion'
import { Link2, FileText, Loader2, Search } from 'lucide-react'

export default function AnalysisPanel({
  activeTab,
  setActiveTab,
  urlInput,
  setUrlInput,
  textInput,
  setTextInput,
  loading,
  onAnalyze,
  error
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl"
    >
      {/* Tab Selector */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setActiveTab('url')}
          className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${
            activeTab === 'url'
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/50'
              : 'bg-white/5 text-purple-200 hover:bg-white/10'
          }`}
        >
          <Link2 className="w-5 h-5" />
          URL Analysis
        </button>
        <button
          onClick={() => setActiveTab('text')}
          className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${
            activeTab === 'text'
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/50'
              : 'bg-white/5 text-purple-200 hover:bg-white/10'
          }`}
        >
          <FileText className="w-5 h-5" />
          Text Analysis
        </button>
      </div>

      {/* Input Area */}
      <div className="mb-6">
        {activeTab === 'url' ? (
          <div>
            <label className="block text-purple-200 font-medium mb-2">
              Article URL
            </label>
            <input
              type="url"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="https://example.com/news/article..."
              className="w-full px-4 py-4 bg-white/5 border border-white/20 rounded-xl text-white placeholder-purple-300/50 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              disabled={loading}
            />
            <p className="text-purple-300/60 text-sm mt-2">
              Paste any news article URL for instant analysis
            </p>
          </div>
        ) : (
          <div>
            <label className="block text-purple-200 font-medium mb-2">
              Article Text
            </label>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste the article text here..."
              rows={8}
              className="w-full px-4 py-4 bg-white/5 border border-white/20 rounded-xl text-white placeholder-purple-300/50 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
              disabled={loading}
            />
            <p className="text-purple-300/60 text-sm mt-2">
              Minimum 50 characters for accurate analysis
            </p>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-red-200"
        >
          {error}
        </motion.div>
      )}

      {/* Analyze Button */}
      <button
        onClick={onAnalyze}
        disabled={loading || (!urlInput && !textInput)}
        className="w-full py-4 px-6 bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 hover:from-purple-600 hover:via-pink-600 hover:to-blue-600 text-white font-bold rounded-xl shadow-lg shadow-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-3 group"
      >
        {loading ? (
          <>
            <Loader2 className="w-6 h-6 animate-spin" />
            Analyzing with BERT AI...
          </>
        ) : (
          <>
            <Search className="w-6 h-6 group-hover:scale-110 transition-transform" />
            Analyze Article
          </>
        )}
      </button>
    </motion.div>
  )
}
