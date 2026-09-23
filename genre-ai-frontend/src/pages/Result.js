import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

const GENRE_COLORS = {
  blues: '#3b82f6',
  classical: '#10b981',
  country: '#84cc16',
  disco: '#f97316',
  hiphop: '#a855f7',
  jazz: '#f59e0b',
  metal: '#ef4444',
  pop: '#ec4899',
  reggae: '#22c55e',
  rock: '#ef4444',
};

const DEFAULT_COLOR = '#6366f1';

function Result() {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result;

  useEffect(() => {
    if (!result) {
      navigate('/');
    }
  }, [result, navigate]);

  if (!result) {
    return null;
  }

  const chartData = Object.entries(result.all_probabilities).map(
    ([genre, prob]) => ({
      genre,
      probability: +(prob * 100).toFixed(2),
      isPredicted: genre === result.predicted_genre,
    })
  );

  chartData.sort((a, b) => b.probability - a.probability);

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="bg-gray-800 p-8 rounded-2xl shadow-2xl w-full max-w-lg border border-gray-700">
        <h1 className="text-2xl font-bold text-white text-center mb-6">
          Resultado da Análise
        </h1>

        <div className="text-center mb-6">
          <p className="text-gray-400 text-sm mb-1">{result.filename}</p>
          <div className="inline-block bg-indigo-600 px-6 py-3 rounded-xl shadow-lg">
            <span className="text-sm text-indigo-200 block">Gênero detectado</span>
            <span className="text-4xl font-extrabold text-white uppercase">
              {result.predicted_genre}
            </span>
            <span className="text-2xl font-bold text-indigo-200 block mt-1">
              {result.confidence_percentage}
            </span>
          </div>
        </div>

        <div className="mb-6">
          <h2 className="text-sm font-medium text-gray-300 mb-3">
            Probabilidade por gênero
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ left: 10 }}>
                <XAxis
                  type="number"
                  domain={[0, 100]}
                  tick={{ fill: '#9ca3af', fontSize: 12 }}
                  unit="%"
                />
                <YAxis
                  type="category"
                  dataKey="genre"
                  tick={({ x, y, payload }) => (
                    <text
                      x={x}
                      y={y}
                      fill="#9ca3af"
                      fontSize={12}
                      textAnchor="end"
                      dominantBaseline="middle"
                    >
                      {payload.value.charAt(0).toUpperCase() + payload.value.slice(1)}
                    </text>
                  )}
                  width={90}
                />
                <Tooltip
                  formatter={(value) => [`${value}%`, 'Probabilidade']}
                  labelFormatter={(label) =>
                    label.charAt(0).toUpperCase() + label.slice(1)
                  }
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #4b5563',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#ffffff' }}
                  itemStyle={{ color: '#ffffff' }}
                />
                <Bar dataKey="probability" radius={[0, 6, 6, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell
                      key={index}
                      fill={
                        entry.isPredicted
                          ? '#6366f1'
                          : GENRE_COLORS[entry.genre] || DEFAULT_COLOR
                      }
                      stroke={entry.isPredicted ? '#818cf8' : 'none'}
                      strokeWidth={entry.isPredicted ? 2 : 0}
                      opacity={entry.isPredicted ? 1 : 0.5}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <button
          onClick={() => navigate('/')}
          className="w-full bg-gray-700 hover:bg-gray-600
            text-white font-bold py-3 px-4 rounded-lg
            transition duration-200 ease-in-out
            focus:outline-none focus:ring-2 focus:ring-gray-500"
        >
          ← Voltar
        </button>
      </div>
    </div>
  );
}

export default Result;
