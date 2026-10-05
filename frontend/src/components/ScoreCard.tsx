import React from 'react';
import {
  AlertTriangle,
  Clock,
  HardDrive,
  ShieldAlert,
  CheckCircle,
  HelpCircle,
  Info,
} from 'lucide-react';
import { Analysis } from '../types';

interface ScoreCardProps {
  analysis: Analysis;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({ analysis }) => {
  const { quality_score, summary, time_complexity, space_complexity, metrics } = analysis;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400 border-emerald-500/40 bg-emerald-950/20';
    if (score >= 60) return 'text-amber-400 border-amber-500/40 bg-amber-950/20';
    return 'text-rose-400 border-rose-500/40 bg-rose-950/20';
  };

  const getBarColor = (score: number) => {
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 60) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  return (
    <div className="space-y-4">
      {/* Non-negotiable Advisory Disclaimer Banner */}
      <div className="p-3 bg-slate-900/90 border border-indigo-500/30 rounded-lg flex items-start space-x-3 text-xs text-slate-300">
        <Info className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-indigo-300">Advisory Quality Notice: </span>
          The DevLens Quality Estimate (DQE) is an advisory heuristic. Static analyses and AI suggestions
          are recommendations that must be verified by developers prior to production use.
        </div>
      </div>

      {/* Main Score & Complexity Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Quality Score Dial Card */}
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl flex items-center space-x-4">
          <div
            className={`w-16 h-16 rounded-full border-2 flex flex-col items-center justify-center shrink-0 ${getScoreColor(
              quality_score
            )}`}
          >
            <span className="text-xl font-bold font-mono tracking-tight">{Math.round(quality_score)}</span>
            <span className="text-[10px] uppercase font-mono text-slate-400">/ 100</span>
          </div>
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
              Quality Estimate
            </h4>
            <p className="text-sm font-semibold text-slate-200 mt-0.5">
              {quality_score >= 80 ? 'Production Ready' : quality_score >= 60 ? 'Needs Attention' : 'Action Required'}
            </p>
            <p className="text-[11px] text-slate-400 mt-1">
              Based on 6 quality pillars
            </p>
          </div>
        </div>

        {/* Time Complexity Card */}
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl flex items-center space-x-4">
          <div className="w-12 h-12 rounded-lg bg-indigo-950/40 border border-indigo-800/40 flex items-center justify-center text-indigo-400 shrink-0">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
              Time Complexity
            </h4>
            <div className="flex items-baseline space-x-2 mt-0.5">
              <span className="text-lg font-bold font-mono text-indigo-300">
                {time_complexity || 'O(1)'}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              {metrics ? `Loop depth: ${metrics.cyclomatic_complexity}` : 'Static heuristic'}
            </p>
          </div>
        </div>

        {/* Space Complexity Card */}
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl flex items-center space-x-4">
          <div className="w-12 h-12 rounded-lg bg-sky-950/40 border border-sky-800/40 flex items-center justify-center text-sky-400 shrink-0">
            <HardDrive className="w-6 h-6" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
              Space Complexity
            </h4>
            <div className="flex items-baseline space-x-2 mt-0.5">
              <span className="text-lg font-bold font-mono text-sky-300">
                {space_complexity || 'O(1)'}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Auxiliary allocation estimate
            </p>
          </div>
        </div>
      </div>

      {/* Summary Narrative */}
      {summary && (
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold mb-1.5 flex items-center space-x-2">
            <span>Executive Analysis Summary</span>
          </h4>
          <p className="text-sm text-slate-300 leading-relaxed font-sans">
            {summary}
          </p>
        </div>
      )}

      {/* 6-Pillar DQE Breakdown Bars */}
      {metrics && (
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold mb-3">
            Six-Pillar Quality Assessment Breakdown
          </h4>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3">
            {/* Correctness */}
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Correctness & Bugs</span>
                <span className="font-mono text-slate-400">{Math.round(metrics.correctness_score)}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getBarColor(metrics.correctness_score)}`}
                  style={{ width: `${Math.max(5, metrics.correctness_score)}%` }}
                />
              </div>
            </div>

            {/* Security */}
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Security & Hardening</span>
                <span className="font-mono text-slate-400">{Math.round(metrics.security_score)}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getBarColor(metrics.security_score)}`}
                  style={{ width: `${Math.max(5, metrics.security_score)}%` }}
                />
              </div>
            </div>

            {/* Complexity */}
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Algorithmic Efficiency</span>
                <span className="font-mono text-slate-400">{Math.round(metrics.complexity_score)}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getBarColor(metrics.complexity_score)}`}
                  style={{ width: `${Math.max(5, metrics.complexity_score)}%` }}
                />
              </div>
            </div>

            {/* Readability */}
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Readability & Style</span>
                <span className="font-mono text-slate-400">{Math.round(metrics.readability_score)}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getBarColor(metrics.readability_score)}`}
                  style={{ width: `${Math.max(5, metrics.readability_score)}%` }}
                />
              </div>
            </div>

            {/* Maintainability */}
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Maintainability Index</span>
                <span className="font-mono text-slate-400">{Math.round(metrics.maintainability_index)}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getBarColor(metrics.maintainability_index)}`}
                  style={{ width: `${Math.max(5, metrics.maintainability_index)}%` }}
                />
              </div>
            </div>

            {/* Testing */}
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Testability & Verification</span>
                <span className="font-mono text-slate-400">{Math.round(metrics.testing_score)}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getBarColor(metrics.testing_score)}`}
                  style={{ width: `${Math.max(5, metrics.testing_score)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
