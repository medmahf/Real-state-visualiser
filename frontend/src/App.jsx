import { useEffect, useState } from 'react'
import MapView from './components/Map.jsx'
import ComparePanel from './components/ComparePanel.jsx'
import { getCommunes, getGeojson } from './api.js'

const MAX_SELECTION = 3

export default function App() {
  const [geojson, setGeojson] = useState(null)
  const [communes, setCommunes] = useState([])
  const [selected, setSelected] = useState([]) // codes INSEE

  useEffect(() => {
    getGeojson().then(setGeojson)
    getCommunes().then(setCommunes)
  }, [])

  function toggle(code) {
    setSelected((prev) =>
      prev.includes(code)
        ? prev.filter((c) => c !== code)
        : prev.length < MAX_SELECTION
          ? [...prev, code]
          : prev,
    )
  }

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ flex: 1 }}>
        {/* TODO: choroplethe coloree par prix_m2_median, clic -> toggle(code) */}
        <MapView geojson={geojson} communes={communes} selected={selected} onToggle={toggle} />
      </div>
      <aside style={{ width: 420, overflowY: 'auto', borderLeft: '1px solid #eee', padding: 16 }}>
        {/* TODO: comparaison des communes selectionnees */}
        <ComparePanel selected={selected} />
      </aside>
    </div>
  )
}
