import React, { useState, useEffect } from 'react';
import {
  History,
  FileCode,
  Download,
  Trash2,
  ExternalLink,
  RefreshCw,
  Lock,
  ArrowRight,
} from 'lucide-react';
import { AnalysisSummary, User } from '../types';
import { api } from '../services/api';

interface HistoryViewProps {
  user: User | null;
  onOpenAuth: () => void;
  onSelectAnalysis: (id: string) => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({
  user,
  onOpenAuth,
  onSelectAnalysis,
}) => {
  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = async () => {
    if (!user) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.listAnalyses(1, 50);
      setAnalyses(data.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load analysis history');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchHistory();
    }
  }, [user]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this analysis record? This cannot be undone.')) {
      return;
    }
    try {
      await api.deleteAnalysis(id);
      setAnalyses(analyses.filter((a) => a.id !== id));
    } catch (err: any) {
      alert(err.message || 'Failed to delete analysis');
    }
  };

  const handleExport = async (id: string, format: 'json' | 'markdown', e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const blob = await api.exportAnalysis(id, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `devlens_analysis_${id}.${format === 'json' ? 'json' : 'md'}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(err.message || 'Export failed');
    }
  };

  const getScoreBadge = (score: number) => {
    if (score >= 80) return 'text-emerald-400 bg-emerald-950/40 border-emerald-800/50';
    if (score >= 60) return 'text-amber-400 bg-amber-950/40 border-amber-800/50';
    return 'text-rose-400 bg-rose-950/40 border-rose-800/50';
  };

  if (!user) {
    return (
      <div className="max-w-2xl mx-auto my-12 p-8 bg-slate-900 border border-slate-800 rounded-2xl text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center mx-auto text-indigo-400">
          <Lock className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-slate-100">Sign in to Access Your History</h3>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          Create a free account or sign in to persist your code analyses, track quality scores over time,
          and securely export reports.
        </p>
        <div>
          <button
            onClick={onOpenAuth}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition-colors shadow-sm inline-flex items-center space-x-2"
          >
            <span>Sign In or Register</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight">Analysis History</h2>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            {analyses.length} total reports saved under {user.email}
          </p>
        </div>

        <button
          onClick={fetchHistory}
          disabled={isLoading}
          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono flex items-center space-x-2 border border-slate-700 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-950/40 border border-rose-800/60 rounded-xl text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Analyses Table */}
      {analyses.length === 0 ? (
        <div className="p-12 text-center bg-slate-900 border border-slate-800 rounded-2xl">
          <FileCode className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h4 className="text-sm font-semibold text-slate-200">No analyses recorded yet</h4>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Run an analysis in the Code Analyzer to automatically save your results here.
          </p>
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 border-b border-slate-800 text-slate-400 font-mono uppercase text-[11px]">
                <tr>
                  <th className="py-3 px-4">Title / Snippet</th>
                  <th className="py-3 px-4">Language</th>
                  <th className="py-3 px-4">Quality Score</th>
                  <th className="py-3 px-4">Findings</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-200">
                {analyses.map((item) => (
                  <tr
                    key={item.id}
                    onClick={() => onSelectAnalysis(item.id)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 font-medium text-slate-100 flex items-center space-x-2">
                      <FileCode className="w-4 h-4 text-indigo-400 shrink-0" />
                      <span className="truncate max-w-[200px]">{item.title}</span>
                    </td>
                    <td className="py-3 px-4 font-mono uppercase text-[11px] text-slate-300">
                      {item.language}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-mono font-bold border ${getScoreBadge(
                          item.quality_score
                        )}`}
                      >
                        {Math.round(item.quality_score)} / 100
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300">
                      {item.findings_count} {item.findings_count === 1 ? 'issue' : 'issues'}
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <button
                        onClick={(e) => handleExport(item.id, 'markdown', e)}
                        title="Export as Markdown"
                        className="p-1 rounded hover:bg-slate-700 text-slate-400 hover:text-slate-200"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => handleDelete(item.id, e)}
                        title="Delete Analysis"
                        className="p-1 rounded hover:bg-rose-950/50 text-slate-400 hover:text-rose-400"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
