import React, { useState } from 'react';
import {
  Code2,
  Cpu,
  History,
  Settings as SettingsIcon,
  BookOpen,
  User as UserIcon,
  LogOut,
  Trash2,
  CheckCircle2,
} from 'lucide-react';
import { User } from '../types';

interface NavbarProps {
  currentTab: 'analyzer' | 'history' | 'docs' | 'settings';
  setCurrentTab: (tab: 'analyzer' | 'history' | 'docs' | 'settings') => void;
  user: User | null;
  onOpenAuth: () => void;
  onLogout: () => void;
  onDeleteAccount: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  user,
  onOpenAuth,
  onLogout,
  onDeleteAccount,
}) => {
  const [showUserMenu, setShowUserMenu] = useState(false);

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand / Logo */}
        <div className="flex items-center space-x-8">
          <button
            onClick={() => setCurrentTab('analyzer')}
            className="flex items-center space-x-3 group focus:outline-none"
          >
            <div className="w-9 h-9 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 group-hover:bg-indigo-600/30 transition-colors">
              <Code2 className="w-5 h-5" />
            </div>
            <div className="text-left">
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-slate-100 tracking-tight">DevLens</span>
                <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400">
                  v1.0
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Code review, made clear
              </p>
            </div>
          </button>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            <button
              onClick={() => setCurrentTab('analyzer')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center space-x-2 ${
                currentTab === 'analyzer'
                  ? 'bg-slate-800 text-indigo-400 border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Cpu className="w-4 h-4" />
              <span>Analyzer</span>
            </button>

            <button
              onClick={() => setCurrentTab('history')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center space-x-2 ${
                currentTab === 'history'
                  ? 'bg-slate-800 text-indigo-400 border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <History className="w-4 h-4" />
              <span>History</span>
            </button>

            <button
              onClick={() => setCurrentTab('docs')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center space-x-2 ${
                currentTab === 'docs'
                  ? 'bg-slate-800 text-indigo-400 border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>Guide</span>
            </button>

            <button
              onClick={() => setCurrentTab('settings')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center space-x-2 ${
                currentTab === 'settings'
                  ? 'bg-slate-800 text-indigo-400 border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <SettingsIcon className="w-4 h-4" />
              <span>Settings</span>
            </button>
          </nav>
        </div>

        {/* Right side status & user profile */}
        <div className="flex items-center space-x-4">
          {/* Engine status indicator */}
          <div className="hidden lg:flex items-center space-x-2 px-2.5 py-1 rounded-full bg-slate-950 border border-slate-800 text-xs font-mono text-slate-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Ready for analysis</span>
          </div>

          {user ? (
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 p-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-750 text-slate-200 text-sm focus:outline-none"
              >
                <div className="w-7 h-7 rounded bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 flex items-center justify-center font-bold text-xs uppercase">
                  {user.email[0]}
                </div>
                <span className="max-w-[120px] truncate hidden sm:inline text-xs font-mono">
                  {user.email}
                </span>
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-56 rounded-lg bg-slate-900 border border-slate-700 shadow-xl py-1.5 z-50 text-xs">
                  <div className="px-3 py-2 border-b border-slate-800">
                    <p className="font-semibold text-slate-200">{user.full_name || 'Developer'}</p>
                    <p className="text-slate-400 font-mono truncate">{user.email}</p>
                  </div>

                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      setCurrentTab('settings');
                    }}
                    className="w-full text-left px-3 py-2 text-slate-300 hover:bg-slate-800 flex items-center space-x-2"
                  >
                    <SettingsIcon className="w-3.5 h-3.5 text-slate-400" />
                    <span>Account Settings</span>
                  </button>

                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      onLogout();
                    }}
                    className="w-full text-left px-3 py-2 text-slate-300 hover:bg-slate-800 flex items-center space-x-2"
                  >
                    <LogOut className="w-3.5 h-3.5 text-amber-400" />
                    <span>Sign Out</span>
                  </button>

                  <div className="border-t border-slate-800 mt-1 pt-1">
                    <button
                      onClick={() => {
                        setShowUserMenu(false);
                        onDeleteAccount();
                      }}
                      className="w-full text-left px-3 py-2 text-rose-400 hover:bg-rose-950/40 flex items-center space-x-2"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Delete Account (Purge Data)</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="px-3 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors flex items-center space-x-1.5 shadow-sm"
            >
              <UserIcon className="w-3.5 h-3.5" />
              <span>Sign In / Register</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
