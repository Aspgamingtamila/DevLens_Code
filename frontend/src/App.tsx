import React, { useState, useEffect } from 'react';
import {
  Code2,
  Bug,
  ShieldAlert,
  Clock,
  FlaskConical,
  Sparkles,
  BarChart3,
  Layers,
  AlertCircle,
  FileCode2,
} from 'lucide-react';
import { Navbar } from './components/Navbar';
import { CodeEditor } from './components/CodeEditor';
import { ScoreCard } from './components/ScoreCard';
import { FindingsList } from './components/FindingsList';
import { ComplexityCard } from './components/ComplexityCard';
import { TestViewer } from './components/TestViewer';
import { SuggestionsView } from './components/SuggestionsView';
import { HistoryView } from './components/HistoryView';
import { DocsView } from './components/DocsView';
import { SettingsView } from './components/SettingsView';
import { AuthModal } from './components/AuthModal';
import { SAMPLE_SNIPPETS } from './components/sampleCodes';
import { Analysis, SupportedLanguage, User } from './types';
import { api } from './services/api';
import * as ts from 'typescript';

export function App() {
  const [currentNav, setCurrentNav] = useState<'analyzer' | 'history' | 'docs' | 'settings'>('analyzer');
  const [user, setUser] = useState<User | null>(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  // Analyzer States
  const [code, setCode] = useState<string>(SAMPLE_SNIPPETS[0].code);
  const [language, setLanguage] = useState<SupportedLanguage>('python');
  const [enableAi, setEnableAi] = useState<boolean>(true);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [activeAnalysisTab, setActiveAnalysisTab] = useState<
    'overview' | 'bugs' | 'security' | 'complexity' | 'tests' | 'suggestions'
  >('overview');

  // Verify auth on mount
  useEffect(() => {
    if (api.isAuthenticated()) {
      api
        .getMe()
        .then((userData) => setUser(userData))
        .catch(() => {
          api.clearTokens();
          setUser(null);
        });
    }
  }, []);

  const handleAnalyze = async () => {
    if (!code || code.trim().length === 0) return;
    setIsLoading(true);
    setAnalysisError(null);
    try {
      if (language === 'typescript') {
        const syntaxError = ts.transpileModule(code, {
          fileName: 'snippet.ts',
          reportDiagnostics: true,
          compilerOptions: { target: ts.ScriptTarget.Latest },
        }).diagnostics?.find((diagnostic) => diagnostic.category === ts.DiagnosticCategory.Error);
        if (syntaxError) {
          const position = syntaxError.file?.getLineAndCharacterOfPosition(syntaxError.start ?? 0);
          const message = ts.flattenDiagnosticMessageText(syntaxError.messageText, '\n');
          setAnalysis(null);
          setAnalysisError(
            `Syntax error at line ${(position?.line ?? 0) + 1}, column ${(position?.character ?? 0) + 1}: ${message}`
          );
          return;
        }
      }

      const result = await api.analyzeCode(
        code,
        language,
        `${language.toUpperCase()} Analysis`,
        enableAi
      );
      setAnalysis(result);
      setActiveAnalysisTab(
        result.findings.some((finding) => finding.rule_id?.includes('SYNTAX') || finding.rule_id?.includes('COMPILER'))
          ? 'bugs'
          : 'overview'
      );
    } catch (err: any) {
      setAnalysisError(err.message || 'Analysis pipeline encountered an error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectHistoryAnalysis = async (id: string) => {
    try {
      setIsLoading(true);
      const data = await api.getAnalysis(id);
      setAnalysis(data);
      setCode(data.code_snippet);
      setLanguage(data.language);
      setCurrentNav('analyzer');
      setActiveAnalysisTab('overview');
    } catch (err: any) {
      alert(err.message || 'Failed to fetch analysis details');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
  };

  const handleDeleteAccount = async () => {
    if (confirm('Are you sure you want to delete your account? All history will be permanently erased.')) {
      try {
        await api.deleteAccount();
        setUser(null);
        alert('Account and all associated analyses have been permanently deleted.');
      } catch (err: any) {
        alert(err.message || 'Failed to delete account');
      }
    }
  };

  const bugFindings = analysis?.findings.filter((f) => f.category === 'bug') || [];
  const securityFindings = analysis?.findings.filter((f) => f.category === 'security') || [];
  const suggestionFindings = analysis?.findings.filter((f) => f.suggestion) || [];

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans">
      <Navbar
        currentTab={currentNav}
        setCurrentTab={setCurrentNav}
        user={user}
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
        onDeleteAccount={handleDeleteAccount}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col">
        {currentNav === 'analyzer' && (
          <div className="flex-1 flex flex-col space-y-4">
            {/* Header intro / tagline */}
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-100">
                  Code analyzer
                </h1>
                <p className="text-sm text-slate-400 mt-1">
                  Check your code for errors and get practical suggestions.
                </p>
              </div>

              {analysis && (
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono text-slate-400">
                    Analysis ID: <span className="text-indigo-400">{analysis.id.slice(0, 8)}</span>
                  </span>
                </div>
              )}
            </div>

            {analysisError && (
              <div className="p-3 bg-rose-950/50 border border-rose-800/80 rounded-xl text-rose-300 text-xs flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{analysisError}</span>
              </div>
            )}

            {/* Dual-Pane Code Analyzer Grid */}
            <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-[580px]">
              {/* Left Pane: Code Editor */}
              <div className="h-full min-h-[460px]">
                <CodeEditor
                  code={code}
                  setCode={setCode}
                  language={language}
                  setLanguage={setLanguage}
                  enableAi={enableAi}
                  setEnableAi={setEnableAi}
                  onAnalyze={handleAnalyze}
                  isLoading={isLoading}
                />
              </div>

              {/* Right Pane: Analysis Results */}
              <div className="flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg h-full min-h-[460px]">
                {/* Result Tabs Navigation */}
                <div className="px-3 bg-slate-950/80 border-b border-slate-800 flex items-center space-x-1 overflow-x-auto text-xs font-mono">
                  <button
                    onClick={() => setActiveAnalysisTab('overview')}
                    className={`py-3 px-3 border-b-2 font-medium flex items-center space-x-1.5 transition-colors whitespace-nowrap ${
                      activeAnalysisTab === 'overview'
                        ? 'border-indigo-500 text-indigo-400 bg-slate-900/60'
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <BarChart3 className="w-3.5 h-3.5" />
                    <span>Overview</span>
                  </button>

                  <button
                    onClick={() => setActiveAnalysisTab('bugs')}
                    className={`py-3 px-3 border-b-2 font-medium flex items-center space-x-1.5 transition-colors whitespace-nowrap ${
                      activeAnalysisTab === 'bugs'
                        ? 'border-indigo-500 text-indigo-400 bg-slate-900/60'
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Bug className="w-3.5 h-3.5" />
                    <span>Bugs ({bugFindings.length})</span>
                  </button>

                  <button
                    onClick={() => setActiveAnalysisTab('security')}
                    className={`py-3 px-3 border-b-2 font-medium flex items-center space-x-1.5 transition-colors whitespace-nowrap ${
                      activeAnalysisTab === 'security'
                        ? 'border-indigo-500 text-indigo-400 bg-slate-900/60'
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                    <span>Security ({securityFindings.length})</span>
                  </button>

                  <button
                    onClick={() => setActiveAnalysisTab('complexity')}
                    className={`py-3 px-3 border-b-2 font-medium flex items-center space-x-1.5 transition-colors whitespace-nowrap ${
                      activeAnalysisTab === 'complexity'
                        ? 'border-indigo-500 text-indigo-400 bg-slate-900/60'
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Clock className="w-3.5 h-3.5" />
                    <span>Complexity</span>
                  </button>

                  <button
                    onClick={() => setActiveAnalysisTab('tests')}
                    className={`py-3 px-3 border-b-2 font-medium flex items-center space-x-1.5 transition-colors whitespace-nowrap ${
                      activeAnalysisTab === 'tests'
                        ? 'border-indigo-500 text-indigo-400 bg-slate-900/60'
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <FlaskConical className="w-3.5 h-3.5 text-sky-400" />
                    <span>Tests ({analysis?.generated_tests.length || 0})</span>
                  </button>

                  <button
                    onClick={() => setActiveAnalysisTab('suggestions')}
                    className={`py-3 px-3 border-b-2 font-medium flex items-center space-x-1.5 transition-colors whitespace-nowrap ${
                      activeAnalysisTab === 'suggestions'
                        ? 'border-indigo-500 text-indigo-400 bg-slate-900/60'
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                    <span>Suggestions ({suggestionFindings.length})</span>
                  </button>
                </div>

                {/* Right Pane Content Body */}
                <div className="flex-1 p-4 overflow-y-auto bg-slate-950/40">
                  {analysis ? (
                    <>
                      {activeAnalysisTab === 'overview' && <ScoreCard analysis={analysis} />}
                      {activeAnalysisTab === 'bugs' && (
                        <FindingsList
                          findings={analysis.findings.filter((f) => f.category === 'bug')}
                        />
                      )}
                      {activeAnalysisTab === 'security' && (
                        <FindingsList
                          findings={analysis.findings.filter((f) => f.category === 'security')}
                        />
                      )}
                      {activeAnalysisTab === 'complexity' && <ComplexityCard analysis={analysis} />}
                      {activeAnalysisTab === 'tests' && (
                        <TestViewer
                          tests={analysis.generated_tests}
                          language={analysis.language}
                        />
                      )}
                      {activeAnalysisTab === 'suggestions' && (
                        <SuggestionsView analysis={analysis} />
                      )}
                    </>
                  ) : (
                    <div className="h-full flex flex-col items-center justify-center p-8 text-center space-y-4">
                      <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-indigo-400">
                        <FileCode2 className="w-6 h-6" />
                      </div>
                      <div className="max-w-sm space-y-1">
                        <h3 className="text-sm font-bold text-slate-200">
                          Awaiting Code Submission
                        </h3>
                        <p className="text-xs text-slate-400 leading-relaxed">
                          Paste your code into the editor or pick an example preset on the left, then click
                          <span className="text-indigo-400 font-mono font-semibold"> Analyze Code</span> to generate
                          the complete report.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {currentNav === 'history' && (
          <HistoryView
            user={user}
            onOpenAuth={() => setIsAuthOpen(true)}
            onSelectAnalysis={handleSelectHistoryAnalysis}
          />
        )}

        {currentNav === 'docs' && <DocsView />}

        {currentNav === 'settings' && (
          <SettingsView
            user={user}
            onOpenAuth={() => setIsAuthOpen(true)}
            onDeleteAccount={handleDeleteAccount}
          />
        )}
      </main>

      {/* Global Footer */}
      <footer className="border-t border-slate-800 bg-slate-950 py-4 text-center text-xs text-slate-500 font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-wrap items-center justify-between gap-2">
          <span>DevLens · Clear feedback for better code</span>
          <span>Your code is analyzed, never run</span>
        </div>
      </footer>

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onSuccess={(loggedUser) => setUser(loggedUser)}
      />
    </div>
  );
}
export default App;
