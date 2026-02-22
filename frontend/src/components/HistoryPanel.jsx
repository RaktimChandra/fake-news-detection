import { motion } from 'framer-motion'
import { History, AlertTriangle, CheckCircle2, Clock } from 'lucide-react'

export default function HistoryPanel({ history, onSelect }) {
  if (history.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10"
      >
        <div className="flex items-center gap-3 mb-4">
          <History className="w-6 h-6 text-purple-400" />
          <h3 className="text-xl font-semibold text-white">Recent Analysis</h3>
        </div>
        <p className="text-purple-200/60 text-center py-8">
          No analysis history yet
        </p>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10"
    >
      <div className="flex items-center gap-3 mb-6">
        <History className="w-6 h-6 text-purple-400" />
        <h3 className="text-xl font-semibold text-white">Recent Analysis</h3>
      </div>

      <div className="space-y-3 max-h-[600px] overflow-y-auto custom-scrollbar">
        {history.map((item, idx) => (
          <motion.button
            key={item.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            onClick={() => onSelect(item)}
            className="w-full text-left p-4 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 transition-all duration-200 group"
          >
            <div className="flex items-start justify-between mb-2">
              {item.prediction === 'FAKE' ? (
                <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
              ) : (
                <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0" />
              )}
              <span className={`text-xs px-2 py-1 rounded-full ${
                item.prediction === 'FAKE'
                  ? 'bg-red-500/20 text-red-300'
                  : 'bg-green-500/20 text-green-300'
              }`}>
                {item.confidence}%
              </span>
            </div>

            <p className="text-white text-sm font-medium mb-2 line-clamp-2 group-hover:text-purple-300 transition-colors">
              {item.source && item.source !== 'Direct input' 
                ? new URL(item.source).hostname 
                : 'Text input'
              }
            </p>

            <div className="flex items-center gap-2 text-purple-200/60 text-xs">
              <Clock className="w-3 h-3" />
              {new Date(item.timestamp).toLocaleTimeString()}
            </div>
          </motion.button>
        ))}
      </div>
    </motion.div>
  )
}
