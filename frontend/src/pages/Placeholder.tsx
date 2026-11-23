export function Placeholder({ name }: { name: string }) {
  return (
    <div>
      <h1 className="text-2xl font-semibold mb-2">{name}</h1>
      <div className="glass rounded-2xl p-10 text-center text-slate-300">
        <p>This page is coming in the next round.</p>
        <p className="text-xs mt-2">The backend for it is already built and tested.</p>
      </div>
    </div>
  )
}

