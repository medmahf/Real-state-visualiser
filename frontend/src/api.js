// Couche d'acces a l'API. En dev, vite proxy /api -> :8000.
export async function getCommunes() {
  const r = await fetch('/api/communes')
  return r.json()
}

export async function getCommune(code) {
  const r = await fetch(`/api/communes/${code}`)
  return r.json()
}

export async function compare(codes) {
  const r = await fetch(`/api/compare?codes=${codes.join(',')}`)
  return r.json()
}

export async function getGeojson() {
  const r = await fetch('/communes_94.geojson')
  return r.json()
}
