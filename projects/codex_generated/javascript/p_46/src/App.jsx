import React, { useEffect, useMemo, useState } from 'react';
import { Line, Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend);

const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:4000';

function App() {
  const [metrics, setMetrics] = useState(() => ({
    timestamps: [],
    values: [],
    categories: { A: 0, B: 0, C: 0 }
  }));

  useEffect(() => {
    const socket = new WebSocket(wsUrl);
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setMetrics((prev) => {
          const newTimestamps = [...prev.timestamps, data.timestamp].slice(-20);
          const newValues = [...prev.values, data.value].slice(-20);
          const newCategories = { ...prev.categories };
          if (data.category && newCategories[data.category] !== undefined) {
            newCategories[data.category] += 1;
          }
          return {
            timestamps: newTimestamps,
            values: newValues,
            categories: newCategories
          };
        });
      } catch (error) {
        console.error('Failed to parse data', error);
      }
    };
    socket.onopen = () => console.log('WebSocket connected');
    socket.onerror = (err) => console.error('WebSocket error', err);
    socket.onclose = () => console.log('WebSocket disconnected');
    return () => socket.close();
  }, []);

  const lineData = useMemo(
    () => ({
      labels: metrics.timestamps,
      datasets: [
        {
          label: 'Real-time Metric',
          data: metrics.values,
          borderColor: '#3b82f6',
          fill: false,
          tension: 0.3
        }
      ]
    }),
    [metrics.timestamps, metrics.values]
  );

  const barData = useMemo(
    () => ({
      labels: ['A', 'B', 'C'],
      datasets: [
        {
          label: 'Category Counts',
          data: ['A', 'B', 'C'].map((key) => metrics.categories[key]),
          backgroundColor: ['#1d4ed8', '#10b981', '#f59e0b']
        }
      ]
    }),
    [metrics.categories]
  );

  const pieData = useMemo(() => {
    const values = Object.values(metrics.categories);
    const total = values.reduce((sum, item) => sum + item, 0) || 1;
    return {
      labels: ['A', 'B', 'C'],
      datasets: [
        {
          data: values,
          backgroundColor: ['#6366f1', '#ec4899', '#14b8a6']
        }
      ],
      total
    };
  }, [metrics.categories]);

  return (
    <div className="dashboard">
      <header>
        <h1>Real-time Metrics Dashboard</h1>
        <span>WebSocket Source: {wsUrl}</span>
      </header>
      <main>
        <section className="card">
          <h2>Live Line Chart</h2>
          <Line data={lineData} options={{ responsive: true, maintainAspectRatio: false }} />
        </section>
        <section className="card">
          <h2>Category Distribution</h2>
          <Bar data={barData} options={{ responsive: true, maintainAspectRatio: false }} />
        </section>
        <section className="card">
          <h2>Category Share</h2>
          <Pie data={pieData} options={{ responsive: true, maintainAspectRatio: false }} />
        </section>
      </main>
    </div>
  );
}

export default App;
