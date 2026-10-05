import React from 'react';
import {
  Sparkles,
  ArrowRight,
  Code2,
  CheckCircle2,
  Lightbulb,
} from 'lucide-react';
import { Analysis } from '../types';

interface SuggestionsViewProps {
  analysis: Analysis;
}

export const SuggestionsView: React.FC<SuggestionsViewProps> = ({ analysis }) => {
  const suggestions = analysis.findings.filter((f) => f.suggestion && f.suggestion.trim().length > 0);

  return (
    <div className="space-y-4">
      {/* Intro Banner */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl flex items-start space-x-3">
        <Lightbulb className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300">
          <p className="font-semibold text-slate-100">
            Intelligent Refactoring & Modernization Recommendations
          </p>
          <p className="mt-1 leading-relaxed">
            The recommendations below identify idiomatic design patterns, security hardenings, and performance
            optimizations tailored to your code snippet.
          </p>
        </div>
      </div>

      {suggestions.length === 0 ? (
        <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-xl">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
          <h4 className="text-sm font-semibold text-slate-300">No pending refactoring recommendations</h4>
          <p className="text-xs text-slate-400 mt-1">
            Your code follows current standard best practices with no critical structural remediations detected.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {suggestions.map((item, index) => (
            <div
              key={item.id}
              className="p-5 bg-slate-900 border border-slate-800 rounded-xl space-y-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-full bg-indigo-950 border border-indigo-700/60 text-indigo-400 text-xs font-mono font-bold flex items-center justify-center">
                    {index + 1}
                  </span>
                  <h4 className="text-sm font-semibold text-slate-100">{item.title}</h4>
                </div>
                <span className="text-[11px] font-mono text-slate-400">
                  {item.line_start ? `Affects Line ${item.line_start}` : 'Global design'}
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed font-sans">
                {item.explanation}
              </p>

              {/* Proposed Solution Box */}
              <div className="p-3 bg-slate-950 border border-slate-800/80 rounded-lg">
                <div className="text-[10px] font-mono uppercase text-emerald-400 font-semibold mb-1.5 flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Proposed Clean Implementation</span>
                </div>
                <pre className="font-mono text-xs text-slate-200 leading-relaxed overflow-x-auto whitespace-pre-wrap">
                  {item.suggestion}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
