import { motion } from 'framer-motion'
import { AlertTriangle, CheckCircle2, Clock, FileText, TrendingUp, Zap } from 'lucide-react'

export default function ResultCard({ result }) {
  const isFake = result.prediction === 'FAKE'

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: -20 }}
      transition={{ type: "spring", duration: 0.6 }}
      className="mt-8"
    >
      <div
        className={`rounded-3xl p-8 border-2 ${
          isFake
            ? 'bg-gradient-to-br from-red-500/20 to-orange-500/20 border-red-500/50'
            : 'bg-gradient-to-br from-green-500/20 to-emerald-500/20 border-green-500/50'
        } backdrop-blur-xl shadow-2xl`}
      >
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          {isFake ? (
            <AlertTriangle className="w-16 h-16 text-red-400 animate-pulse" />
          ) : (
            <CheckCircle2 className="w-16 h-16 text-green-400" />
          )}
          <div>
            <h2 className="text-3xl font-bold text-white mb-1">
              {isFake ? 'Likely Fake News' : 'Likely Real News'}
            </h2>
            <p className={`text-lg ${
              isFake ? 'text-red-200' : 'text-green-200'
            }`}>
              {isFake 
                ? 'This article shows signs of misinformation'
                : 'This article appears to be credible'
              }
            </p>
          </div>
        </div>

        {/* Confidence Bar */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-white font-medium">Confidence Score</span>
            <span className="text-2xl font-bold text-white">{result.confidence}%</span>
          </div>
          <div className="h-4 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${result.confidence}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className={`h-full rounded-full ${
                isFake
                  ? 'bg-gradient-to-r from-red-500 to-orange-500'
                  : 'bg-gradient-to-r from-green-500 to-emerald-500'
              }`}
            />
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/10 rounded-xl p-4 backdrop-blur-sm"
          >
            <div className="flex items-center gap-3 mb-2">
              <Zap className="w-5 h-5 text-purple-400" />
              <span className="text-purple-200 text-sm">Processing Time</span>
            </div>
            <p className="text-2xl font-bold text-white">{result.processing_time}s</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white/10 rounded-xl p-4 backdrop-blur-sm"
          >
            <div className="flex items-center gap-3 mb-2">
              <FileText className="w-5 h-5 text-purple-400" />
              <span className="text-purple-200 text-sm">Word Count</span>
            </div>
            <p className="text-2xl font-bold text-white">{result.word_count?.toLocaleString()}</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white/10 rounded-xl p-4 backdrop-blur-sm"
          >
            <div className="flex items-center gap-3 mb-2">
              <Clock className="w-5 h-5 text-purple-400" />
              <span className="text-purple-200 text-sm">Analyzed At</span>
            </div>
            <p className="text-lg font-bold text-white">
              {new Date(result.timestamp).toLocaleTimeString()}
            </p>
          </motion.div>
        </div>

        {/* Source Info */}
        {result.source && result.source !== 'Direct input' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="mt-6 p-4 bg-white/5 rounded-xl"
          >
            <p className="text-purple-200 text-sm mb-1">Source</p>
            <p className="text-white text-sm truncate">{result.source}</p>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
