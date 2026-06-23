// Helpers de formatage et logique métier partagée (choroplèthe + fiabilité).

export const RELIABILITY_THRESHOLD = 20

// Palette 5 paliers (bleu froid -> rouge chaud), accessible. Gris pour null.
const PALETTE = ['#2c7fb8', '#7fcdbb', '#fed976', '#fd8d3c', '#bd0026']
const NO_DATA = '#cbd5e1'

const euroFmt = new Intl.NumberFormat('fr-FR', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
})
const intFmt = new Intl.NumberFormat('fr-FR')

export function fmtEuro(n) {
  if (n == null || Number.isNaN(n)) return '—'
  return euroFmt.format(n)
}

export function fmtInt(n) {
  if (n == null || Number.isNaN(n)) return '—'
  return intFmt.format(n)
}

export function isReliable(nbVentes, seuil = RELIABILITY_THRESHOLD) {
  return typeof nbVentes === 'number' && nbVentes >= seuil
}

// Renvoie n-1 bornes de quantiles découpant `values` (non-null) en n classes.
// Ex. n=5 → 4 bornes (q20, q40, q60, q80).
export function quantileBins(values, n = 5) {
  const sorted = values
    .filter((v) => v != null && !Number.isNaN(v))
    .slice()
    .sort((a, b) => a - b)
  if (!sorted.length) return []
  const bins = []
  for (let i = 1; i < n; i++) {
    const idx = Math.floor((sorted.length * i) / n)
    bins.push(sorted[Math.min(idx, sorted.length - 1)])
  }
  return bins
}

export function colorScale(value, bins) {
  if (value == null || Number.isNaN(value) || !bins.length) return NO_DATA
  let i = 0
  while (i < bins.length && value > bins[i]) i++
  return PALETTE[i] ?? PALETTE[PALETTE.length - 1]
}

export const PALETTE_OUT = PALETTE
export const NO_DATA_COLOR = NO_DATA

// Choix de la valeur €/m² affichée pour une commune et un type donné.
// Préfère l'annuel si fiable, sinon le 3 ans glissants. Marque l'origine.
export function pickPrice(commune, type) {
  if (!commune) return { value: null, isThreeYear: false, nb: null }
  const suffix = type === 'Maison' ? 'maison' : 'appartement'
  const annual = commune[`prix_m2_median_${suffix}`]
  const annualNb = commune[`nb_ventes_${suffix}`]
  const threeYear = commune[`prix_m2_3ans_${suffix}`]
  const threeYearNb = commune[`nb_ventes_3ans_${suffix}`]
  if (isReliable(annualNb)) {
    return { value: annual, isThreeYear: false, nb: annualNb }
  }
  if (threeYear != null) {
    return { value: threeYear, isThreeYear: true, nb: threeYearNb }
  }
  return { value: annual ?? null, isThreeYear: false, nb: annualNb }
}
