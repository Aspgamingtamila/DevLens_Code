import React, { useState } from 'react';
import {
  User as UserIcon,
  Shield,
  Trash2,
  Lock,
  Cpu,
  Database,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { User } from '../types';

interface SettingsViewProps {
  user: User | null;
  onOpenAuth: () => void;
  onDeleteAccount: () => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  user,
  onOpenAuth,
  onDeleteAccount,
}) => {
  const [provider, setProvider] = useState<'mock' | 'gemini'>('gemini');
  const [retentionEnabled, setRetentionEnabled] = useState(true);

  if (!user) {
    return (
      <div className="max-w-2xl mx-auto my-12 p-8 bg-slate-900 border border-slate-800 rounded-2xl text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center mx-auto text-indigo-400">
          <UserIcon className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-slate-100">Sign in to Access Settings</h3>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          Sign in to manage your account credentials, configure AI model providers, and customize privacy controls.
        </p>
        <div>
          <button
            onClick={onOpenAuth}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition-colors shadow-sm"
          >
            Sign In or Register
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-100 tracking-tight">Platform Settings</h2>
        <p className="text-xs text-slate-400 mt-1 font-mono">
          Manage your account profile, analysis pipeline preferences, and privacy controls
        </p>
      </div>

      {/* User Profile Card */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
        <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono flex items-center space-x-2">
          <UserIcon className="w-4 h-4 text-indigo-400" />
          <span>Account Profile</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
            <span className="text-slate-400">Email Address</span>
            <p className="font-mono font-semibold text-slate-200 mt-1">{user.email}</p>
          </div>

          <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
            <span className="text-slate-400">Full Name</span>
            <p className="font-semibold text-slate-200 mt-1">{user.full_name || 'Not provided'}</p>
          </div>

          <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
            <span className="text-slate-400">Account ID</span>
            <p className="font-mono text-slate-300 mt-1 truncate">{user.id}</p>
          </div>

          <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
            <span className="text-slate-400">Member Since</span>
            <p className="font-mono text-slate-300 mt-1">
              {new Date(user.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>

      {/* Pipeline & AI Provider Settings */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
        <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-indigo-400" />
          <span>Analysis Pipeline & Intelligence Engine</span>
        </h3>

        <div className="space-y-3">
          <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-xs font-semibold text-slate-200">Execution Safety Protocol</h4>
                <p className="text-xs text-slate-400">
                  User code is strictly analyzed via static AST parsers and constrained models. Zero host execution.
                </p>
              </div>
              <span className="px-2.5 py-1 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 text-[11px] font-mono">
                Enforced
              </span>
            </div>
          </div>

          <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-3">
            <div>
              <h4 className="text-xs font-semibold text-slate-200">AI Provider Architecture</h4>
              <p className="text-xs text-slate-400">
                Choose the model provider backing the educational explanations and test generation synthesis.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <label
                className={`p-3 rounded-lg border text-xs cursor-pointer flex-1 min-w-[200px] transition-colors ${
                  provider === 'gemini'
                    ? 'border-indigo-500 bg-indigo-950/30 text-slate-100'
                    : 'border-slate-800 bg-slate-900 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name="provider"
                    checked={provider === 'gemini'}
                    onChange={() => setProvider('gemini')}
                    className="text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="font-semibold text-slate-200">Google Gemini API</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1 pl-5">
                  High-accuracy multimodal reasoning with structured schema verification.
                </p>
              </label>

              <label
                className={`p-3 rounded-lg border text-xs cursor-pointer flex-1 min-w-[200px] transition-colors ${
                  provider === 'mock'
                    ? 'border-indigo-500 bg-indigo-950/30 text-slate-100'
                    : 'border-slate-800 bg-slate-900 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name="provider"
                    checked={provider === 'mock'}
                    onChange={() => setProvider('mock')}
                    className="text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="font-semibold text-slate-200">Hermetic Mock Engine</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1 pl-5">
                  Offline deterministic synthetic generator. Zero network calls or API token costs.
                </p>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Privacy & Retention Controls */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
        <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono flex items-center space-x-2">
          <Shield className="w-4 h-4 text-emerald-400" />
          <span>Privacy & Data Protection</span>
        </h3>

        <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
          <div>
            <h4 className="text-xs font-semibold text-slate-200">Persistent Analysis History</h4>
            <p className="text-xs text-slate-400">
              When enabled, your analysis runs are saved securely to your account for future review and export.
            </p>
          </div>
          <input
            type="checkbox"
            checked={retentionEnabled}
            onChange={(e) => setRetentionEnabled(e.target.checked)}
            className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-indigo-500 h-4 w-4"
          />
        </div>
      </div>

      {/* Danger Zone */}
      <div className="p-6 bg-rose-950/20 border border-rose-900/40 rounded-xl space-y-4">
        <h3 className="text-sm font-bold text-rose-400 uppercase tracking-wider font-mono flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4" />
          <span>Danger Zone</span>
        </h3>

        <div className="flex flex-wrap items-center justify-between gap-4 p-4 bg-slate-950 border border-rose-900/30 rounded-lg">
          <div>
            <h4 className="text-xs font-semibold text-slate-200">Delete Account & Purge Data</h4>
            <p className="text-xs text-slate-400">
              Permanently delete your user profile and cascade delete all stored analyses, findings, and metrics.
            </p>
          </div>

          <button
            onClick={onDeleteAccount}
            className="px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-sm transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Delete Account</span>
          </button>
        </div>
      </div>
    </div>
  );
};
