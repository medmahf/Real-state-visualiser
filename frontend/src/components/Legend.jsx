import { PALETTE_OUT, NO_DATA_COLOR, fmtEuro } from '../lib/format.js'

// Légende des quantiles affichée en bas à gauche de la carte.
export default function Legend({ bins }) {
  if (!bins || !bins.length) return null
  // 5 classes : ]-inf, b0], ]b0, b1], ..., ]b3, +inf[
  const labels = [
    `≤ ${fmtEuro(bins[0])}`,
    `≤ ${fmtEuro(bins[1])}`,
    `≤ ${fmtEuro(bins[2])}`,
    `≤ ${fmtEuro(bins[3])}`,
    `> ${fmtEuro(bins[3])}`,
  ]
  return (
    <div className="absolute bottom-4 left-4 z-[1000] rounded-lg bg-white/95 p-3 shadow-md text-xs border border-slate-200">
      <div className="font-medium text-slate-700 mb-1.5">€/m² médian</div>
      {PALETTE_OUT.map((c, i) => (
        <div key={c} className="flex items-center gap-2 py-0.5">
          <span
            className="inline-block w-4 h-4 rounded-sm border border-slate-300"
            style={{ background: c }}
          />
          <span className="text-slate-600">{labels[i]}</span>
        </div>
      ))}
      <div className="flex items-center gap-2 py-0.5 mt-1 border-t border-slate-100 pt-1.5">
        <span
          className="inline-block w-4 h-4 rounded-sm border border-slate-300"
          style={{ background: NO_DATA_COLOR }}
        />
        <span className="text-slate-500">données limitées</span>
      </div>
    </div>
  )
}
