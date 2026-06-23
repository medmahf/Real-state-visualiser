// Segmented control Appartement / Maison.
const OPTIONS = ['Appartement', 'Maison']

export default function TypeToggle({ value, onChange }) {
  return (
    <div className="inline-flex rounded-lg border border-slate-200 bg-white p-0.5 text-sm">
      {OPTIONS.map((opt) => {
        const active = opt === value
        return (
          <button
            key={opt}
            type="button"
            onClick={() => onChange(opt)}
            className={
              'px-3 py-1.5 rounded-md transition ' +
              (active
                ? 'bg-slate-900 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900')
            }
          >
            {opt}
          </button>
        )
      })}
    </div>
  )
}
