import { useEffect, useMemo, useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend as RcLegend,
  BarChart,
  Bar,
  ResponsiveContainer,
} from 'recharts'
import { compare } from '../api.js'
import IndicatorCard from './IndicatorCard.jsx'
import { fmtEuro } from '../lib/format.js'

const SERIES_COLORS = ['#0ea5e9', '#f59e0b', '#10b981']

export default function ComparePanel({ selected, communeByCode, typeBien, onToggle }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!selected.length) {
      setData(null)
      return
    }
    setLoading(true)
    compare(selected)
      .then(setData)
      .finally(() => setLoading(false))
  }, [selected.join(',')])

  // Tendance : pivot par année, 1 colonne par commune (pour le type courant).
  const trendData = useMemo(() => {
    if (!data?.communes) return []
    const years = new Set()
    const byCommune = {}
    for (const c of data.communes) {
      byCommune[c.code_commune] = {}
      for (const r of c.indicateurs) {
        if (r.type_bien !== typeBien) continue
        if (r.prix_m2_median == null) continue
        byCommune[c.code_commune][r.annee] = r.prix_m2_median
        years.add(r.annee)
      }
    }
    return [...years]
      .sort()
      .map((annee) => {
        const row = { annee }
        for (const c of data.communes) {
          row[c.nom_commune] = byCommune[c.code_commune]?.[annee] ?? null
        }
        return row
      })
  }, [data, typeBien])

  // Bar : dernier millésime par commune, Appart vs Maison côte-à-côte.
  const barData = useMemo(() => {
    if (!data?.communes) return []
    return data.communes.map((c) => {
      const sortedApt = c.indicateurs
        .filter((r) => r.type_bien === 'Appartement' && r.prix_m2_median != null)
        .sort((a, b) => b.annee - a.annee)
      const sortedMai = c.indicateurs
        .filter((r) => r.type_bien === 'Maison' && r.prix_m2_median != null)
        .sort((a, b) => b.annee - a.annee)
      return {
        nom: c.nom_commune,
        Appartement: sortedApt[0]?.prix_m2_median ?? null,
        Maison: sortedMai[0]?.prix_m2_median ?? null,
      }
    })
  }, [data])

  if (!selected.length) {
    return (
      <div className="p-6 text-center text-slate-500">
        <div className="text-4xl mb-2">🗺️</div>
        <p className="text-sm">
          Sélectionnez 1 à 3 communes sur la carte pour les comparer.
        </p>
      </div>
    )
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Comparaison</h2>
        <span className="text-xs text-slate-500">
          {selected.length} / 3 commune{selected.length > 1 ? 's' : ''}
        </span>
      </div>

      {loading && <div className="text-sm text-slate-500">Chargement…</div>}

      <div className="space-y-3">
        {selected.map((code) => {
          const detail = data?.communes?.find((c) => c.code_commune === code)
          const summary = communeByCode.get(code)
          return (
            <IndicatorCard
              key={code}
              summary={summary}
              detail={detail}
              typeBien={typeBien}
              onClose={onToggle}
            />
          )
        })}
      </div>

      {trendData.length > 1 && (
        <div className="rounded-xl border border-slate-200 bg-white p-3">
          <div className="text-sm font-medium text-slate-700 mb-2">
            Tendance €/m² — {typeBien.toLowerCase()}
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={trendData} margin={{ left: 0, right: 8, top: 8, bottom: 0 }}>
              <CartesianGrid stroke="#f1f5f9" />
              <XAxis dataKey="annee" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis
                tick={{ fontSize: 11, fill: '#64748b' }}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                width={40}
              />
              <Tooltip
                formatter={(v) => fmtEuro(v)}
                contentStyle={{ fontSize: 12, borderRadius: 6 }}
              />
              <RcLegend wrapperStyle={{ fontSize: 11 }} />
              {data?.communes?.map((c, i) => (
                <Line
                  key={c.code_commune}
                  type="monotone"
                  dataKey={c.nom_commune}
                  stroke={SERIES_COLORS[i % SERIES_COLORS.length]}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {barData.length > 0 && (
        <div className="rounded-xl border border-slate-200 bg-white p-3">
          <div className="text-sm font-medium text-slate-700 mb-2">
            Appartement vs Maison (dernier millésime)
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData} margin={{ left: 0, right: 8, top: 8, bottom: 0 }}>
              <CartesianGrid stroke="#f1f5f9" />
              <XAxis dataKey="nom" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis
                tick={{ fontSize: 11, fill: '#64748b' }}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                width={40}
              />
              <Tooltip
                formatter={(v) => fmtEuro(v)}
                contentStyle={{ fontSize: 12, borderRadius: 6 }}
              />
              <RcLegend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="Appartement" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Maison" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
