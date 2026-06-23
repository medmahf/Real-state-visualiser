import { useCallback, useEffect, useMemo, useState } from 'react'
import MapView from './components/Map.jsx'
import ComparePanel from './components/ComparePanel.jsx'
import TypeToggle from './components/TypeToggle.jsx'
import { getCommunes, getGeojson } from './api.js'
import { quantileBins, pickPrice } from './lib/format.js'

const MAX_SELECTION = 3

export default function App() {
  const [geojson, setGeojson] = useState(null)
  const [communes, setCommunes] = useState([])
  const [selected, setSelected] = useState([])
  const [typeBien, setTypeBien] = useState('Appartement')

  useEffect(() => {
    getGeojson().then(setGeojson)
    getCommunes().then(setCommunes)
  }, [])

  const communeByCode = useMemo(() => {
    const m = new Map()
    for (const c of communes) m.set(c.code_commune, c)
    return m
  }, [communes])

  // Bins quantiles sur la valeur affichable (annuelle si fiable sinon 3 ans)
  // pour le type courant. Recalcul à chaque changement de type.
  const bins = useMemo(() => {
    const values = communes
      .map((c) => pickPrice(c, typeBien).value)
      .filter((v) => v != null)
    return quantileBins(values, 5)
  }, [communes, typeBien])

  const toggle = useCallback((code) => {
    setSelected((prev) =>
      prev.includes(code)
        ? prev.filter((c) => c !== code)
        : prev.length < MAX_SELECTION
          ? [...prev, code]
          : prev,
    )
  }, [])

  return (
    <div className="flex flex-col h-screen bg-slate-50 text-slate-900">
      <header className="flex items-center justify-between px-5 py-3 bg-white border-b border-slate-200">
        <div>
          <h1 className="text-base font-semibold leading-tight">
            Comparateur de territoires — Val-de-Marne
          </h1>
          <p className="text-xs text-slate-500">
            Médiane €/m² · DVF géolocalisé 2021–2025 · {communes.length} communes
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500 hidden sm:inline">Type de bien :</span>
          <TypeToggle value={typeBien} onChange={setTypeBien} />
        </div>
      </header>

      <main className="flex-1 flex flex-col md:flex-row min-h-0">
        <section className="flex-1 min-h-[320px] md:min-h-0 relative">
          <MapView
            geojson={geojson}
            communeByCode={communeByCode}
            selected={selected}
            onToggle={toggle}
            typeBien={typeBien}
            bins={bins}
          />
        </section>
        <aside className="w-full md:w-[420px] md:flex-none overflow-y-auto border-t md:border-t-0 md:border-l border-slate-200 bg-slate-50">
          <ComparePanel
            selected={selected}
            communeByCode={communeByCode}
            typeBien={typeBien}
            onToggle={toggle}
          />
        </aside>
      </main>

      <footer className="px-5 py-2 text-[11px] text-slate-500 bg-white border-t border-slate-200">
        Source : DVF géolocalisé (data.gouv.fr) · Cadastre · Mono-bien strict, médiane bornée [800, 25 000] €/m².
        Sous 20 ventes/an, bascule auto sur médiane 3 ans glissants.
      </footer>
    </div>
  )
}
