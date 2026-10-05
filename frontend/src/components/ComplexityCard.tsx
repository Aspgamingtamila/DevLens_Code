import React from 'react';
import {
  Clock,
  HardDrive,
  GitBranch,
  Layers,
  FileText,
  Percent,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { Analysis } from '../types';

interface ComplexityCardProps {
  analysis: Analysis;
}

export const ComplexityCard: React.FC<ComplexityCardProps> = ({ analysis }) => {
  const { time_complexity, space_complexity, metrics } = analysis;

  const getComplexityColor = (comp?: string | null) => {
    if (!comp) return 'text-indigo-400';
    if (comp.includes('O(1)') || comp.includes('O(log N)')) return 'text-emerald-400';
    if (comp.includes('O(N)')) return 'text-sky-400';
    if (comp.includes('O(N log N)')) return 'text-yellow-400';
    return 'text-rose-400';
  };

  return (
    <div className="space-y-4">
      {/* Big-O Complexity Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Time Complexity */}
        <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl">
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2 rounded-lg bg-indigo-950/50 border border-indigo-800/40 text-indigo-400">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-mono uppercase text-slate-400 font-semibold">
                Time Complexity
              </span>
              <div className={`text-2xl font-mono font-bold ${getComplexityColor(time_complexity)}`}>
                {time_complexity || 'O(1)'}
              </div>
            </div>
          </div>
          <p className="text-xs text-slate-300 mt-2 leading-relaxed">
            Theoretical execution bound evaluated via deterministic AST loop traversal and recursion heuristics.
          </p>
        </div>

        {/* Space Complexity */}
        <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl">
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2 rounded-lg bg-sky-950/50 border border-sky-800/40 text-sky-400">
              <HardDrive className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-mono uppercase text-slate-400 font-semibold">
                Space Complexity
              </span>
              <div className={`text-2xl font-mono font-bold ${getComplexityColor(space_complexity)}`}>
                {space_complexity || 'O(1)'}
              </div>
            </div>
          </div>
          <p className="text-xs text-slate-300 mt-2 leading-relaxed">
            Auxiliary memory allocation required by local data structures, buffers, or recursion stack frames.
          </p>
        </div>
      </div>

      {/* Deep Code Metrics Grid */}
      {metrics && (
        <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold mb-4">
            Static Structural & Maintainability Metrics
          </h4>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {/* Cyclomatic Complexity */}
            <div className="p-3 bg-slate-950 border border-slate-800/80 rounded-lg">
              <div className="flex items-center space-x-2 text-slate-400 mb-1">
                <GitBranch className="w-4 h-4 text-indigo-400" />
                <span className="text-[11px] font-mono">Cyclomatic</span>
              </div>
              <div className="text-xl font-bold font-mono text-slate-100">
                {metrics.cyclomatic_complexity}
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                {metrics.cyclomatic_complexity <= 5
                  ? 'Low risk (Simple)'
                  : metrics.cyclomatic_complexity <= 10
                  ? 'Moderate risk'
                  : 'High complexity'}
              </div>
            </div>

            {/* Maintainability Index */}
            <div className="p-3 bg-slate-950 border border-slate-800/80 rounded-lg">
              <div className="flex items-center space-x-2 text-slate-400 mb-1">
                <Layers className="w-4 h-4 text-emerald-400" />
                <span className="text-[11px] font-mono">Maintainability</span>
              </div>
              <div className="text-xl font-bold font-mono text-slate-100">
                {Math.round(metrics.maintainability_index)} / 100
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Composite Halstead
              </div>
            </div>

            {/* Lines of Code */}
            <div className="p-3 bg-slate-950 border border-slate-800/80 rounded-lg">
              <div className="flex items-center space-x-2 text-slate-400 mb-1">
                <FileText className="w-4 h-4 text-sky-400" />
                <span className="text-[11px] font-mono">Total LOC</span>
              </div>
              <div className="text-xl font-bold font-mono text-slate-100">
                {metrics.lines_of_code}
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Physical lines
              </div>
            </div>

            {/* Comment Density */}
            <div className="p-3 bg-slate-950 border border-slate-800/80 rounded-lg">
              <div className="flex items-center space-x-2 text-slate-400 mb-1">
                <Percent className="w-4 h-4 text-amber-400" />
                <span className="text-[11px] font-mono">Comment Ratio</span>
              </div>
              <div className="text-xl font-bold font-mono text-slate-100">
                {(metrics.comment_ratio * 100).toFixed(1)}%
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Documentation ratio
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
