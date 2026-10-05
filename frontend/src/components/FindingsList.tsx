import React, { useState } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  Info,
  ShieldAlert,
  Bug,
  Code,
  CheckCircle2,
  Filter,
} from 'lucide-react';
import { Finding, FindingSeverity, FindingCategory } from '../types';

interface FindingsListProps {
  findings: Finding[];
}

export const FindingsList: React.FC<FindingsListProps> = ({ findings }) => {
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterCategory, setFilterCategory] = useState<string>('all');

  const getSeverityBadge = (severity: FindingSeverity) => {
    switch (severity) {
      case 'critical':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-rose-950/60 text-rose-300 border border-rose-800/60 flex items-center space-x-1">
            <AlertCircle className="w-3 h-3" />
            <span>Critical</span>
          </span>
        );
      case 'high':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-amber-950/60 text-amber-300 border border-amber-800/60 flex items-center space-x-1">
            <AlertTriangle className="w-3 h-3" />
            <span>High</span>
          </span>
        );
      case 'medium':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase bg-yellow-950/60 text-yellow-300 border border-yellow-800/60">
            Medium
          </span>
        );
      case 'low':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-sky-950/60 text-sky-300 border border-sky-800/60">
            Low
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-slate-800 text-slate-300 border border-slate-700">
            Info
          </span>
        );
    }
  };

  const getProvenanceBadge = (source: string) => {
    if (source === 'static') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-slate-800/80 text-slate-300 border border-slate-700">
          Deterministic Rule
        </span>
      );
    } else if (source === 'ai') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-indigo-950/70 text-indigo-300 border border-indigo-700/50">
          AI Suggestion
        </span>
      );
    } else {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-purple-950/70 text-purple-300 border border-purple-700/50">
          Hybrid Finding
        </span>
      );
    }
  };

  const filteredFindings = findings.filter((f) => {
    if (filterSeverity !== 'all' && f.severity !== filterSeverity) return false;
    if (filterCategory !== 'all' && f.category !== filterCategory) return false;
    return true;
  });

  return (
    <div className="space-y-4">
      {/* Filters Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs">
        <div className="flex items-center space-x-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-400 font-medium">Filter Issues:</span>

          <select
            value={filterSeverity}
            aria-label="Filter by Severity"
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-slate-800 text-slate-200 border border-slate-700 rounded px-2 py-1 text-xs focus:outline-none"
          >
            <option value="all">All Severities ({findings.length})</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
            <option value="info">Info</option>
          </select>

          <select
            value={filterCategory}
            aria-label="Filter by Category"
            onChange={(e) => setFilterCategory(e.target.value)}
            className="bg-slate-800 text-slate-200 border border-slate-700 rounded px-2 py-1 text-xs focus:outline-none"
          >
            <option value="all">All Categories</option>
            <option value="bug">Bugs</option>
            <option value="security">Security</option>
            <option value="complexity">Complexity</option>
            <option value="maintainability">Maintainability</option>
            <option value="style">Style</option>
          </select>
        </div>

        <div className="text-slate-400 font-mono text-[11px]">
          Showing {filteredFindings.length} of {findings.length} findings
        </div>
      </div>

      {/* Findings List Items */}
      {filteredFindings.length === 0 ? (
        <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-xl">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
          <h4 className="text-sm font-semibold text-slate-200">No issues found matching criteria</h4>
          <p className="text-xs text-slate-400 mt-1">
            {findings.length === 0
              ? 'Static parsers and heuristic models detected zero major vulnerabilities in this snippet.'
              : 'Try changing your severity or category filter settings.'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredFindings.map((finding) => (
            <div
              key={finding.id}
              className="p-4 bg-slate-900 border border-slate-800 rounded-xl hover:border-slate-700 transition-colors"
            >
              {/* Card Header */}
              <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                <div className="flex items-center space-x-2">
                  {getSeverityBadge(finding.severity)}
                  {getProvenanceBadge(finding.source)}
                  {finding.cwe_id && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-950/40 text-rose-300 border border-rose-800/40">
                      {finding.cwe_id}
                    </span>
                  )}
                  {finding.rule_id && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700">
                      {finding.rule_id}
                    </span>
                  )}
                </div>

                <div className="text-xs font-mono text-slate-400">
                  {finding.line_start ? (
                    <span className="bg-slate-800 px-2 py-0.5 rounded border border-slate-700 text-slate-300">
                      Line {finding.line_start}
                      {finding.line_end && finding.line_end !== finding.line_start
                        ? `-${finding.line_end}`
                        : ''}
                    </span>
                  ) : (
                    <span>Global scope</span>
                  )}
                </div>
              </div>

              {/* Title & Explanation */}
              <h4 className="text-sm font-semibold text-slate-100 mb-1">{finding.title}</h4>
              <p className="text-xs text-slate-300 leading-relaxed font-sans mb-3">
                {finding.explanation}
              </p>

              {/* Remediation Suggestion */}
              {finding.suggestion && (
                <div className="p-3 bg-slate-950 border border-slate-800/80 rounded-lg text-xs">
                  <div className="text-[11px] font-mono uppercase text-indigo-400 font-semibold mb-1 flex items-center space-x-1.5">
                    <Code className="w-3 h-3" />
                    <span>Recommended Remediation</span>
                  </div>
                  <div className="font-mono text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {finding.suggestion}
                  </div>
                </div>
              )}

              {/* Confidence footer */}
              <div className="mt-2.5 flex items-center justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/60">
                <span>Category: {finding.category}</span>
                <span>Confidence: {Math.round(finding.confidence * 100)}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
