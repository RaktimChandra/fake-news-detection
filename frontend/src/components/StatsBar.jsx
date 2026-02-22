import { motion } from 'framer-motion'
import { Target, Zap, Database } from 'lucide-react'

export default function StatsBar() {
  const stats = [
    { label: 'Accuracy', value: '94.2%', icon: Target },
    { label: 'Processing', value: '<1s', icon: Zap },
    { label: 'Training Data', value: '50K+', icon: Database }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8"
    >
      <div className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {stats.map((stat, idx) => (
            <div key={idx} className="flex items-center gap-4">
              <div className="p-3 bg-purple-500/20 rounded-xl">
                <stat.icon className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
                <p className="text-purple-200/60 text-sm">{stat.label}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
