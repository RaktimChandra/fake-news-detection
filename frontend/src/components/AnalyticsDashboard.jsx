import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertCircle, 
  CheckCircle, 
  BarChart3,
  PieChart,
  Activity,
  Clock,
  Calendar,
  Globe
} from 'lucide-react';

const AnalyticsDashboard = ({ history }) => {
  const [stats, setStats] = useState({
    total: 0,
    fake: 0,
    real: 0,
    avgConfidence: 0,
    todayAnalyses: 0,
    weekAnalyses: 0,
    fakePercentage: 0,
    realPercentage: 0,
    avgProcessingTime: 0
  });

  const [chartData, setChartData] = useState({
    daily: [],
    hourly: [],
    confidence: []
  });

  useEffect(() => {
    calculateStats();
    generateChartData();
  }, [history]);

  const calculateStats = () => {
    if (history.length === 0) return;

    const total = history.length;
    const fake = history.filter(item => item.result.prediction === 0).length;
    const real = total - fake;
    const avgConf = history.reduce((sum, item) => sum + item.result.confidence, 0) / total;
    
    // Today's analyses
    const today = new Date().toDateString();
    const todayCount = history.filter(item => 
      new Date(item.timestamp).toDateString() === today
    ).length;

    // This week's analyses
    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    const weekCount = history.filter(item => 
      new Date(item.timestamp) > weekAgo
    ).length;

    // Average processing time
    const avgTime = history.reduce((sum, item) => 
      sum + (item.result.processing_time || 0.35), 0
    ) / total;

    setStats({
      total,
      fake,
      real,
      avgConfidence: avgConf,
      todayAnalyses: todayCount,
      weekAnalyses: weekCount,
      fakePercentage: (fake / total) * 100,
      realPercentage: (real / total) * 100,
      avgProcessingTime: avgTime
    });
  };

  const generateChartData = () => {
    if (history.length === 0) return;

    // Daily data for last 7 days
    const dailyMap = {};
    const hourlyMap = {};
    const confidenceRanges = { low: 0, medium: 0, high: 0 };

    history.forEach(item => {
      const date = new Date(item.timestamp);
      const dateStr = date.toLocaleDateString();
      const hour = date.getHours();

      // Daily
      if (!dailyMap[dateStr]) {
        dailyMap[dateStr] = { fake: 0, real: 0 };
      }
      if (item.result.prediction === 0) {
        dailyMap[dateStr].fake++;
      } else {
        dailyMap[dateStr].real++;
      }

      // Hourly
      if (!hourlyMap[hour]) {
        hourlyMap[hour] = 0;
      }
      hourlyMap[hour]++;

      // Confidence ranges
      const conf = item.result.confidence;
      if (conf < 70) confidenceRanges.low++;
      else if (conf < 85) confidenceRanges.medium++;
      else confidenceRanges.high++;
    });

    setChartData({
      daily: Object.entries(dailyMap).slice(-7).map(([date, data]) => ({
        date,
        ...data
      })),
      hourly: Object.entries(hourlyMap).map(([hour, count]) => ({
        hour: parseInt(hour),
        count
      })),
      confidence: [
        { range: 'Low (<70%)', count: confidenceRanges.low },
        { range: 'Medium (70-85%)', count: confidenceRanges.medium },
        { range: 'High (>85%)', count: confidenceRanges.high }
      ]
    });
  };

  return (
    <div className="space-y-6">
      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Analyses"
          value={stats.total}
          icon={<BarChart3 className="w-6 h-6" />}
          color="blue"
        />
        <StatCard
          title="Fake News Detected"
          value={stats.fake}
          subtitle={`${stats.fakePercentage.toFixed(1)}%`}
          icon={<AlertCircle className="w-6 h-6" />}
          color="red"
        />
        <StatCard
          title="Real News Verified"
          value={stats.real}
          subtitle={`${stats.realPercentage.toFixed(1)}%`}
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
        />
        <StatCard
          title="Avg Confidence"
          value={`${stats.avgConfidence.toFixed(1)}%`}
          icon={<TrendingUp className="w-6 h-6" />}
          color="purple"
        />
      </div>

      {/* Time-based Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <TimeStatCard
          title="Today"
          value={stats.todayAnalyses}
          icon={<Clock className="w-5 h-5" />}
        />
        <TimeStatCard
          title="This Week"
          value={stats.weekAnalyses}
          icon={<Calendar className="w-5 h-5" />}
        />
        <TimeStatCard
          title="Avg Processing"
          value={`${stats.avgProcessingTime.toFixed(2)}s`}
          icon={<Activity className="w-5 h-5" />}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Distribution Chart */}
        <ChartCard title="Daily Analysis Trend (Last 7 Days)">
          <DailyChart data={chartData.daily} />
        </ChartCard>

        {/* Confidence Distribution */}
        <ChartCard title="Confidence Distribution">
          <ConfidenceChart data={chartData.confidence} />
        </ChartCard>
      </div>

      {/* Hourly Activity Chart */}
      <ChartCard title="Hourly Activity Pattern">
        <HourlyChart data={chartData.hourly} />
      </ChartCard>

      {/* Performance Metrics */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-slate-700">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Activity className="w-6 h-6 text-blue-400" />
          Performance Metrics
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricBar 
            label="Accuracy Rate" 
            value={stats.avgConfidence} 
            color="green"
          />
          <MetricBar 
            label="False Positive Rate" 
            value={100 - stats.avgConfidence} 
            color="red"
          />
          <MetricBar 
            label="Processing Speed" 
            value={(1 / stats.avgProcessingTime) * 10} 
            max={100}
            color="blue"
            suffix="x"
          />
        </div>
      </div>
    </div>
  );
};

// Stat Card Component
const StatCard = ({ title, value, subtitle, icon, color }) => {
  const colors = {
    blue: 'from-blue-500 to-blue-600',
    red: 'from-red-500 to-red-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gradient-to-br ${colors[color]} rounded-xl p-6 text-white shadow-lg`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm opacity-90 mb-1">{title}</p>
          <h3 className="text-3xl font-bold">{value}</h3>
          {subtitle && <p className="text-sm opacity-75 mt-1">{subtitle}</p>}
        </div>
        <div className="opacity-75">{icon}</div>
      </div>
    </motion.div>
  );
};

// Time Stat Card
const TimeStatCard = ({ title, value, icon }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    className="bg-slate-800 rounded-lg p-4 border border-slate-700"
  >
    <div className="flex items-center gap-3">
      <div className="text-blue-400">{icon}</div>
      <div>
        <p className="text-sm text-slate-400">{title}</p>
        <p className="text-2xl font-bold text-white">{value}</p>
      </div>
    </div>
  </motion.div>
);

// Chart Card Container
const ChartCard = ({ title, children }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-slate-800 rounded-xl p-6 border border-slate-700"
  >
    <h3 className="text-lg font-bold mb-4 text-white">{title}</h3>
    {children}
  </motion.div>
);

// Daily Chart Component (Simple Bar Chart)
const DailyChart = ({ data }) => {
  if (data.length === 0) {
    return <div className="text-slate-400 text-center py-8">No data available</div>;
  }

  const maxValue = Math.max(...data.map(d => d.fake + d.real));

  return (
    <div className="space-y-3">
      {data.map((day, idx) => (
        <div key={idx} className="space-y-1">
          <div className="flex justify-between text-sm text-slate-400">
            <span>{day.date}</span>
            <span>{day.fake + day.real} analyses</span>
          </div>
          <div className="flex gap-1 h-8">
            <div
              className="bg-red-500 rounded transition-all"
              style={{ width: `${(day.fake / maxValue) * 100}%` }}
              title={`Fake: ${day.fake}`}
            />
            <div
              className="bg-green-500 rounded transition-all"
              style={{ width: `${(day.real / maxValue) * 100}%` }}
              title={`Real: ${day.real}`}
            />
          </div>
        </div>
      ))}
      <div className="flex gap-4 text-sm pt-2">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded"></div>
          <span className="text-slate-400">Fake</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded"></div>
          <span className="text-slate-400">Real</span>
        </div>
      </div>
    </div>
  );
};

// Confidence Chart (Horizontal Bars)
const ConfidenceChart = ({ data }) => {
  if (data.length === 0) {
    return <div className="text-slate-400 text-center py-8">No data available</div>;
  }

  const total = data.reduce((sum, item) => sum + item.count, 0);
  const colors = ['text-red-400 bg-red-500', 'text-yellow-400 bg-yellow-500', 'text-green-400 bg-green-500'];

  return (
    <div className="space-y-4">
      {data.map((item, idx) => (
        <div key={idx}>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-300">{item.range}</span>
            <span className={colors[idx].split(' ')[0]}>{item.count} ({((item.count / total) * 100).toFixed(1)}%)</span>
          </div>
          <div className="bg-slate-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full ${colors[idx].split(' ')[1]} transition-all duration-500`}
              style={{ width: `${(item.count / total) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

// Hourly Chart
const HourlyChart = ({ data }) => {
  if (data.length === 0) {
    return <div className="text-slate-400 text-center py-8">No data available</div>;
  }

  const sortedData = [...data].sort((a, b) => a.hour - b.hour);
  const maxCount = Math.max(...sortedData.map(d => d.count));

  return (
    <div className="flex items-end gap-1 h-32">
      {sortedData.map((item, idx) => (
        <div
          key={idx}
          className="flex-1 flex flex-col items-center gap-1"
        >
          <div
            className="w-full bg-gradient-to-t from-blue-500 to-blue-400 rounded-t transition-all hover:from-blue-400 hover:to-blue-300"
            style={{ height: `${(item.count / maxCount) * 100}%` }}
            title={`${item.hour}:00 - ${item.count} analyses`}
          />
          <span className="text-xs text-slate-400">{item.hour}</span>
        </div>
      ))}
    </div>
  );
};

// Metric Bar
const MetricBar = ({ label, value, max = 100, color, suffix = '%' }) => {
  const colors = {
    green: 'bg-green-500',
    red: 'bg-red-500',
    blue: 'bg-blue-500'
  };

  return (
    <div>
      <div className="flex justify-between text-sm mb-2">
        <span className="text-slate-300">{label}</span>
        <span className="text-white font-bold">
          {value.toFixed(1)}{suffix}
        </span>
      </div>
      <div className="bg-slate-700 rounded-full h-2 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.min((value / max) * 100, 100)}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={`h-full ${colors[color]}`}
        />
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
