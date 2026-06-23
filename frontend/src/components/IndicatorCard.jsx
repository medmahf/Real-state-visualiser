// Carte d'un indicateur cle pour une commune (ex. €/m2 median dernier millesime).
export default function IndicatorCard({ label, value, unit }) {
  return (
    <div style={{ border: '1px solid #eee', borderRadius: 8, padding: 12 }}>
      <div style={{ fontSize: 12, color: '#666' }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 500 }}>
        {value ?? '—'} {unit}
      </div>
    </div>
  )
}
