import { useEffect, useState } from 'react'
import { compare } from '../api.js'
// import { LineChart, Line, XAxis, YAxis, Tooltip, BarChart, Bar } from 'recharts'

// TODO:
//  - charger compare(selected)
//  - cartes d'indicateurs (IndicatorCard) par commune
//  - LineChart: evolution €/m2 par annee, une serie par commune
//  - BarChart: €/m2 par type de bien (appartement vs maison)
export default function ComparePanel({ selected }) {
  const [data, setData] = useState(null)

  useEffect(() => {
    if (selected.length) compare(selected).then(setData)
  }, [selected])

  if (!selected.length)
    return <p>Sélectionne 1 à 3 communes sur la carte pour les comparer.</p>

  return (
    <div>
      <h2 style={{ fontWeight: 500 }}>Comparaison</h2>
      <p>Communes : {selected.join(', ')}</p>
      <pre style={{ fontSize: 11 }}>{JSON.stringify(data, null, 2)}</pre>
    </div>
  )
}
