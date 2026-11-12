import { useCallback, useEffect, useRef, useState } from 'react'

// Runs an async loader, exposing {data, loading, error, reload}. Re-runs when deps change.
export function useFetch(loader, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: null })
  const seq = useRef(0)
  const run = useCallback(() => {
    const id = ++seq.current
    setState((s) => ({ ...s, loading: true, error: null }))
    return loader()
      .then((data) => { if (id === seq.current) setState({ data, loading: false, error: null }) })
      .catch((error) => { if (id === seq.current) setState({ data: null, loading: false, error }) })
  }, deps) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { run() }, [run])
  return { ...state, reload: run }
}

export function useDebounce(value, delay = 350) {
  const [v, setV] = useState(value)
  useEffect(() => { const t = setTimeout(() => setV(value), delay); return () => clearTimeout(t) }, [value, delay])
  return v
}
