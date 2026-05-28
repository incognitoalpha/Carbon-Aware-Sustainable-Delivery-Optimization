import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { Leaf, Truck, Clock, BarChart3, ShieldCheck, Map as MapIcon } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    co2Saved: '14.2%',
    slaCompliance: '98.5%',
    avgDeliveryTime: '18.4 min',
    fleetActive: 24
  });

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
          </div>
          <div className="flex gap-4">
            <button className="bg-white border border-slate-200 px-4 py-2 rounded-lg font-medium shadow-sm hover:bg-slate-50 transition">
              Export ESG Report
            </button>
            <button className="bg-emerald-600 text-white px-4 py-2 rounded-lg font-medium shadow-sm hover:bg-emerald-700 transition">
              Optimize New Batch
            </button>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-6 mb-10">
          <StatCard label="CO₂ Reduction" value={stats.co2Saved} subtext="vs. standard routing" color="text-emerald-600" />
          <StatCard label="SLA Compliance" value={stats.slaCompliance} subtext="On-time deliveries" color="text-blue-600" />
          <StatCard label="Avg Delivery" value={stats.avgDeliveryTime} subtext="-2.1 min from last week" color="text-slate-900" />
          <StatCard label="Active Vehicles" value={stats.fleetActive} subtext="Real-time tracking" color="text-slate-900" />
        </div>

        {/* Placeholder for Map & Charts */}
        <div className="grid grid-cols-3 gap-8">
          <div className="col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-slate-100 h-96 flex flex-col items-center justify-center text-slate-400">
            <MapIcon size={48} className="mb-4 opacity-20" />
            <p>Interactive Map Component Loading...</p>
            <p className="text-xs mt-2 italic">Connect to Leaflet in next step</p>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center justify-center text-slate-400">
             <BarChart3 size={48} className="mb-4 opacity-20" />
             <p>Fleet Mix Analysis</p>
          </div>
        </div>
      </main>

      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
      `}</style>
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
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
      <p className="text-sm font-medium text-slate-500 mb-1">{label}</p>
      <p className={`text-3xl font-bold mb-1 ${color}`}>{value}</p>
      <p className="text-xs text-slate-400">{subtext}</p>
    </div>
  );
}
