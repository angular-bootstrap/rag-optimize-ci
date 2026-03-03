import type { CandidateResult } from '../types';
import { formatCost, formatMs, formatPct } from '../utils';

type Props = {
  candidate: CandidateResult | undefined;
};

export function CaseTable({ candidate }: Props) {
  if (!candidate) return null;

  return (
    <div className="card">
      <h2>Per-Case Results: {candidate.name}</h2>
      <table>
        <thead>
          <tr>
            <th>Record</th>
            <th>Quality</th>
            <th>Grounded</th>
            <th>Citation</th>
            <th>Latency</th>
            <th>Cost</th>
            <th>Score</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {candidate.cases.map((row) => (
            <tr key={row.record_id}>
              <td>{row.record_id}</td>
              <td>{formatPct(row.metrics.quality)}</td>
              <td>{formatPct(row.metrics.groundedness)}</td>
              <td>{formatPct(row.metrics.citation)}</td>
              <td>{formatMs(row.metrics.latency_ms)}</td>
              <td>{formatCost(row.metrics.cost)}</td>
              <td>{row.metrics.score.toFixed(3)}</td>
              <td>
                <span className={row.metrics.passed_hard_constraints ? 'pill pass' : 'pill fail'}>
                  {row.metrics.passed_hard_constraints ? 'PASS' : 'FAIL'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
