import { useMemo, useState } from 'react';
import { CaseTable } from './components/CaseTable';
import { ScoreTable } from './components/ScoreTable';
import type { RunResult } from './types';
import { sortCandidates } from './utils';
import './styles.css';

function App() {
  const [run, setRun] = useState<RunResult | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<string>('');
  const [error, setError] = useState<string>('');

  const candidates = useMemo(() => (run ? sortCandidates(run) : []), [run]);
  const selected = candidates.find((c) => c.name === selectedCandidate) ?? candidates[0];

  const onUpload = async (file: File | null) => {
    if (!file) return;
    try {
      const text = await file.text();
      const parsed = JSON.parse(text) as RunResult;
      if (!parsed.run_id || !parsed.candidates) {
        throw new Error('Invalid run JSON format');
      }
      setRun(parsed);
      setSelectedCandidate(parsed.candidates[0]?.name ?? '');
      setError('');
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to parse file';
      setError(message);
      setRun(null);
    }
  };

  const loadSample = async () => {
    try {
      const res = await fetch('/sample-run.json');
      const parsed = (await res.json()) as RunResult;
      setRun(parsed);
      setSelectedCandidate(parsed.candidates[0]?.name ?? '');
      setError('');
    } catch {
      setError('Could not load sample-run.json.');
    }
  };

  return (
    <main className="page">
      <section className="hero">
        <h1>RAG Optimize Dashboard</h1>
        <p>Inspect run artifacts, compare candidates, and explain recommendation decisions.</p>
      </section>

      <section className="toolbar card">
        <label className="upload">
          Upload run JSON
          <input
            type="file"
            accept="application/json"
            onChange={(e) => onUpload(e.target.files?.[0] ?? null)}
          />
        </label>
        <button type="button" onClick={loadSample}>
          Load sample
        </button>
      </section>

      {error && <p className="error">{error}</p>}

      {run && (
        <>
          <section className="meta card">
            <div><strong>Run ID:</strong> {run.run_id}</div>
            <div><strong>Dataset:</strong> {run.dataset_path}</div>
            <div><strong>Generated:</strong> {new Date(run.generated_at).toLocaleString()}</div>
          </section>

          <ScoreTable
            candidates={candidates}
            selected={selected?.name ?? ''}
            onSelect={setSelectedCandidate}
          />
          <CaseTable candidate={selected} />
        </>
      )}
    </main>
  );
}

export default App;
