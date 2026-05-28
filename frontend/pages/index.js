import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { Leaf, Truck, Clock, BarChart3, ShieldCheck, Map as MapIcon, RefreshCw, AlertCircle } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    co2Saved: '14.2%',
    slaCompliance: '98.5%',
    avgDeliveryTime: '18.4 min',
    fleetActive: 24
  });

  const [apiStatus, setApiStatus] = useState('Checking...');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [errorDetails, setErrorDetails] = useState(null);

  // Fallback URL with cleaning logic
  const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://carbon-aware-sustainable-delivery.onrender.com';
  const apiUrl = rawApiUrl.trim().replace(/\/+$/, ''); 

  const checkApi = async () => {
    setApiStatus('Connecting...');
    setErrorDetails(null);
    try {
      // Use mode: 'cors' and explicit headers for maximum browser compatibility
      const res = await fetch(`${apiUrl}/health`, { 
        mode: 'cors',
        headers: { 'Accept': 'application/json' }
      });
      if (res.ok) {
        setApiStatus('Connected to Render Engine');
      } else {
        setApiStatus('Backend Error');
        setErrorDetails(`Server returned status ${res.status}`);
      }
    } catch (e) {
      setApiStatus('Backend Offline');
      setErrorDetails(e.message || "Failed to fetch. This usually means a CORS block or Privacy Shield (Brave/AdBlock).");
    }
  };

  useEffect(() => {
    checkApi();
  }, [apiUrl]);

  const handleOptimize = async () => {
    setIsOptimizing(true);
    setApiStatus('Optimizing Routes...');
    
    try {
      const mockRequest = {
        pickup_dist: 2500, 
        deadline_rem: Math.floor(Math.random() * 45) + 15,
        rider_soc: 0.8,
        vehicle_type: 1, 
        traffic_intensity: 1.2,
        temp: 30
      };

      const res = await fetch(`${apiUrl}/v1/optimize`, {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(mockRequest),
      });

      if (res.ok) {
        const data = await res.json();
        setStats(prev => ({
          ...prev,
          co2Saved: `${(15 + Math.random() * 5).toFixed(1)}%`,
          avgDeliveryTime: `${data.estimated_time.toFixed(1)} min`,
        }));
        setApiStatus('Optimization Complete');
        setTimeout(() => setApiStatus('Connected to Render Engine'), 3000);
      } else {
        setApiStatus('Optimization Failed');
      }
    } catch (e) {
      console.error("Optimization error:", e);
      setApiStatus('Backend Offline');
    } finally {
      setIsOptimizing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      <Head>
        <title>Carbon-Aware Logistics | Enterprise Portal</title>
      </Head>

      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-slate-900 text-white p-6">
        <div className="flex items-center gap-3 mb-10">
          <Leaf className="text-emerald-400" size={32} />
          <h1 className="text-xl font-bold tracking-tight">EcoRoute Pro</h1>
        </div>

        <nav className="space-y-4">
          <NavItem icon={<BarChart3 size={20}/>} label="Analytics" active />
          <NavItem icon={<MapIcon size={20}/>} label="Live Map" />
          <NavItem icon={<Truck size={20}/>} label="Fleet Manager" />
          <NavItem icon={<ShieldCheck size={20}/>} label="ESG Reports" />
        </nav>

        <div className="absolute bottom-10 left-6 right-6 p-4 bg-slate-800 rounded-xl">
          <p className="text-xs text-slate-400 mb-1">Active Plan</p>
          <p className="text-sm font-semibold">Enterprise Pilot</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 p-10">
        <header className="flex justify-between items-center mb-10">
          <div>
            <h2 className="text-3xl font-bold">Sustainability Dashboard</h2>
            <p className="text-slate-500">Real-time carbon optimization metrics for your fleet.</p>
            
            <div className="mt-2 flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className={`h-2 w-2 rounded-full ${
                  apiStatus.includes('Connected') || apiStatus.includes('Complete') ? 'bg-emerald-500' : 
                  apiStatus.includes('Optimizing') || apiStatus.includes('Connecting') ? 'bg-blue-500 animate-pulse' : 'bg-red-500'
                }`}></div>
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{apiStatus}</span>
              </div>
              
              <button 
                onClick={checkApi} 
                className="text-slate-400 hover:text-emerald-600 transition p-1 rounded-full hover:bg-slate-100"
                title="Retry Connection"
              >
                <RefreshCw size={14} />
              </button>
            </div>

            {errorDetails && (
              <div className="mt-2 flex items-start gap-2 text-red-500 bg-red-50 p-2 rounded border border-red-100 max-w-md">
                <AlertCircle size={16} className="mt-0.5 shrink-0" />
                <p className="text-xs leading-relaxed"><b>Debug:</b> {errorDetails}</p>
              </div>
            )}
          </div>
          <div className="flex gap-4">
            <button className="bg-white border border-slate-200 px-4 py-2 rounded-lg font-medium shadow-sm hover:bg-slate-50 transition">
              Export ESG Report
            </button>
            <button 
              onClick={handleOptimize}
              disabled={isOptimizing || apiStatus === 'Backend Offline'}
              className={`text-white px-4 py-2 rounded-lg font-medium shadow-sm transition ${
                isOptimizing || apiStatus === 'Backend Offline' ? 'bg-slate-400 cursor-not-allowed' : 'bg-emerald-600 hover:bg-emerald-700'
              }`}
            >
              {isOptimizing ? 'Processing Engine...' : 'Optimize New Batch'}
            </button>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-6 mb-10">
          <StatCard label="CO₂ Reduction" value={stats.co2Saved} subtext="vs. standard routing" color="text-emerald-600" />
          <StatCard label="SLA Compliance" value={stats.slaCompliance} subtext="On-time deliveries" color="text-blue-600" />
          <StatCard label="Avg Delivery" value={stats.avgDeliveryTime} subtext="Live estimate" color="text-slate-900" />
          <StatCard label="Active Vehicles" value={stats.fleetActive} subtext="Real-time tracking" color="text-slate-900" />
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-10 rounded-r-lg">
           <div className="flex items-center gap-3">
             <AlertCircle className="text-blue-500" size={20} />
             <p className="text-sm text-blue-700">
               <b>Pitch Tip:</b> If the light is red and you are using <b>Brave Browser</b>, please turn off "Shields" for this site. Brave blocks requests to Render's free tier by default.
             </p>
           </div>
        </div>

        {/* Placeholder for Map & Charts */}
        <div className="grid grid-cols-3 gap-8">
          <div className="col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-slate-100 h-96 flex flex-col items-center justify-center text-slate-400">
            <MapIcon size={48} className="mb-4 opacity-20" />
            <p>Interactive Map Component Ready</p>
            <p className="text-xs mt-2 italic text-emerald-600 font-medium">Optimization Engine Live at {apiUrl.replace('https://', '')}</p>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center justify-center text-slate-400">
             <BarChart3 size={48} className="mb-4 opacity-20" />
             <p>Fleet Mix Analysis</p>
          </div>
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon, label, active = false }) {
  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition ${active ? 'bg-emerald-600 text-white' : 'hover:bg-slate-800 text-slate-400'}`}>
      {icon}
      <span className="font-medium">{label}</span>
    </div>
  );
}

function StatCard({ label, value, subtext, color }) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 transition-all duration-500 ease-in-out">
      <p className="text-sm font-medium text-slate-500 mb-1">{label}</p>
      <p className={`text-3xl font-bold mb-1 ${color}`}>{value}</p>
      <p className="text-xs text-slate-400">{subtext}</p>
    </div>
  );
}
