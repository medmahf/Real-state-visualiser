import { fmtEuro, fmtInt, isReliable } from '../lib/format.js'

// Carte récapitulative d'une commune sélectionnée.
// `detail` provient de /api/compare (CommuneDetail) ; `summary` de /api/communes (CommuneListItem).
export default function IndicatorCard({ summary, detail, typeBien, onClose }) {
  const code = summary?.code_commune ?? detail?.code_commune
  const nom = summary?.nom_commune ?? detail?.nom_commune ?? code

  // Dernier millésime disponible pour le type courant, depuis le détail si présent.
  const lastByType = (type) => {
    if (!detail?.indicateurs) return null
    const rows = detail.indicateurs
      .filter((r) => r.type_bien === type)
      .sort((a, b) => b.annee - a.annee)
    return rows[0] ?? null
  }

  const apt = lastByType('Appartement')
  const mai = lastByType('Maison')
  const main = typeBien === 'Maison' ? mai : apt

  const reliable = isReliable(main?.nb_ventes)
  // Fallback 3 ans (depuis summary) si peu fiable
  const summaryKey = typeBien === 'Maison' ? 'maison' : 'appartement'
  const fallbackThreeYear = summary?.[`prix_m2_3ans_${summaryKey}`]
  const fallbackThreeYearNb = summary?.[`nb_ventes_3ans_${summaryKey}`]

  const mainPrice = reliable ? main?.prix_m2_median : fallbackThreeYear
  const mainSource = reliable ? 'annuelle' : '3 ans glissants'

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-start justify-between px-4 py-3 border-b border-slate-100">
        <div>
          <div className="font-semibold text-slate-900">{nom}</div>
          <div className="text-xs text-slate-500">
            {code} · {main?.annee ?? summary?.annee_reference ?? '—'}
          </div>
        </div>
        <button
          onClick={() => onClose?.(code)}
          className="text-slate-400 hover:text-slate-700 text-lg leading-none px-1"
          aria-label="Retirer"
        >
          ×
        </button>
      </div>

      <div className="px-4 py-3 space-y-3">
        <div>
          <div className="text-xs uppercase tracking-wide text-slate-500">
            Médiane {typeBien.toLowerCase()} ({mainSource})
          </div>
          <div className="text-2xl font-semibold text-slate-900 mt-0.5">
            {fmtEuro(mainPrice)}<span className="text-sm font-normal text-slate-500"> /m²</span>
          </div>
          {!reliable && (
            <div className="mt-1 inline-flex items-center gap-1 rounded-md bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-800">
              échantillon limité ({fmtInt(fallbackThreeYearNb ?? main?.nb_ventes ?? 0)} ventes / 3 ans)
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-2 text-sm">
          <Stat label="Appartement" value={apt?.prix_m2_median} unit="€/m²" sub={`${fmtInt(apt?.nb_ventes)} ventes`} />
          <Stat label="Maison" value={mai?.prix_m2_median} unit="€/m²" sub={`${fmtInt(mai?.nb_ventes)} ventes`} />
          <Stat label={`Surface médiane (${typeBien.toLowerCase()})`} value={main?.surface_mediane} unit="m²" />
          <Stat label="P25 — P75" value={null} unit="" sub={
            main?.prix_m2_p25 != null
              ? `${fmtEuro(main.prix_m2_p25)} — ${fmtEuro(main.prix_m2_p75)}`
              : '—'
          } />
        </div>

        {summary?.nb_parcelles && (
          <div className="text-xs text-slate-500 pt-1 border-t border-slate-100">
            {fmtInt(summary.nb_parcelles)} parcelles cadastrales
          </div>
        )}
      </div>
    </div>
  )
}

function Stat({ label, value, unit, sub }) {
  return (
    <div className="rounded-md bg-slate-50 p-2">
      <div className="text-[11px] text-slate-500">{label}</div>
      {value != null && (
        <div className="text-sm font-medium text-slate-900">
          {fmtEuro(value).replace('€', '')}
          <span className="text-xs text-slate-500 ml-0.5">{unit}</span>
        </div>
      )}
      {sub && <div className="text-[11px] text-slate-500">{sub}</div>}
    </div>
  )
}
