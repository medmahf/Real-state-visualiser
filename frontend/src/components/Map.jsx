import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet'

// TODO:
//  - colorer chaque commune selon prix_m2_median (echelle de couleurs)
//  - style des communes selectionnees (surbrillance)
//  - onEachFeature: click -> onToggle(code_commune), tooltip avec nom + €/m2
export default function MapView({ geojson, communes, selected, onToggle }) {
  if (!geojson) return <div style={{ padding: 16 }}>Chargement de la carte…</div>
  return (
    <MapContainer center={[48.79, 2.45]} zoom={11} style={{ height: '100%' }}>
      <TileLayer
        attribution='&copy; OpenStreetMap'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <GeoJSON data={geojson} />
    </MapContainer>
  )
}
