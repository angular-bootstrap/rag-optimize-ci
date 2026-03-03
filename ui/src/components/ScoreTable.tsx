import type { CandidateResult } from '../types';
import { formatCost, formatMs, formatPct } from '../utils';

type Props = {
  candidates: CandidateResult[];
  onSelect: (name: string) => void;
  selected: string;
};

export function ScoreTable({ candidates, onSelect, selected }: Props) {
  return (
    <div className="card">
      <h2>Candidate Scorecard</h2>
      <table>
        <thead>
          <tr>
            <th>Candidate</th>
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
          {candidates.map((c) => (
            <tr
              key={c.name}
              className={selected === c.name ? 'selected-row' : ''}
              onClick={() => onSelect(c.name)}
            >
              <td>{c.name}</td>
              <td>{formatPct(c.aggregate.quality)}</td>
              <td>{formatPct(c.aggregate.groundedness)}</td>
              <td>{formatPct(c.aggregate.citation)}</td>
              <td>{formatMs(c.aggregate.latency_ms)}</td>
              <td>{formatCost(c.aggregate.cost)}</td>
              <td>{c.aggregate.score.toFixed(3)}</td>
              <td>
                <span className={c.aggregate.passed_hard_constraints ? 'pill pass' : 'pill fail'}>
                  {c.aggregate.passed_hard_constraints ? 'PASS' : 'FAIL'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
