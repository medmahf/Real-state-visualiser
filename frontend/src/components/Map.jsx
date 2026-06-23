import { useMemo } from 'react'
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet'
import { colorScale, pickPrice, isReliable } from '../lib/format.js'
import Legend from './Legend.jsx'

// Carte choroplèthe : une couleur par quantile sur €/m² du type courant.
// Les communes sous le seuil de fiabilité sont rendues en opacité réduite.
export default function MapView({
  geojson,
  communeByCode,
  selected,
  onToggle,
  typeBien,
  bins,
}) {
  // Re-clé pour forcer react-leaflet à recalculer styles et tooltips.
  // `communeByCode.size` est inclus : si les communes arrivent après le geojson,
  // on remonte la couche pour binder les tooltips avec les vraies données.
  const renderKey = `${typeBien}-${communeByCode.size}-${selected.join(',')}`

  const style = useMemo(
    () => (feature) => {
      const code = feature.properties.code_commune
      const c = communeByCode.get(code)
      const { value, nb } = pickPrice(c, typeBien)
      const fill = colorScale(value, bins)
      const reliable = isReliable(nb)
      const isSelected = selected.includes(code)
      return {
        color: isSelected ? '#0f172a' : '#ffffff',
        weight: isSelected ? 2.5 : 1,
        opacity: 1,
        fillColor: fill,
        fillOpacity: reliable ? 0.75 : 0.35,
      }
    },
    [communeByCode, typeBien, bins, selected],
  )

  function onEachFeature(feature, layer) {
    const code = feature.properties.code_commune
    const c = communeByCode.get(code)
    const { value, isThreeYear, nb } = pickPrice(c, typeBien)
    const nom = c?.nom_commune ?? code
    const priceLabel =
      value != null
        ? `${Math.round(value).toLocaleString('fr-FR')} €/m²${isThreeYear ? ' (3 ans)' : ''}`
        : 'pas de donnée'
    const nbLabel = nb != null ? `${nb} ventes` : '—'
    layer.bindTooltip(
      `<strong>${nom}</strong><br/>${priceLabel}<br/><span style="color:#64748b">${nbLabel}</span>`,
      { sticky: true },
    )
    layer.on({
      click: () => onToggle(code),
      mouseover: (e) => e.target.setStyle({ weight: 2.5, color: '#0f172a' }),
      mouseout: (e) => {
        const sel = selected.includes(code)
        e.target.setStyle({ weight: sel ? 2.5 : 1, color: sel ? '#0f172a' : '#ffffff' })
      },
    })
  }

  if (!geojson || communeByCode.size === 0)
    return <div className="p-4 text-slate-500">Chargement de la carte…</div>

  return (
    <div className="relative h-full w-full">
      <MapContainer center={[48.79, 2.45]} zoom={11} className="h-full w-full">
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <GeoJSON
          key={renderKey}
          data={geojson}
          style={style}
          onEachFeature={onEachFeature}
        />
      </MapContainer>
      <Legend bins={bins} />
    </div>
  )
}
