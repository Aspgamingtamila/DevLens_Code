import React, { useState } from 'react';
import {
  Check,
  Copy,
  Terminal,
  FlaskConical,
  ExternalLink,
  ShieldAlert,
} from 'lucide-react';
import { GeneratedTest, SupportedLanguage } from '../types';

interface TestViewerProps {
  tests: GeneratedTest[];
  language: SupportedLanguage;
}

export const TestViewer: React.FC<TestViewerProps> = ({ tests, language }) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (id: string, code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getRunnerInstructions = (framework: string) => {
    switch (framework.toLowerCase()) {
      case 'pytest':
        return 'python -m pytest -v test_snippet.py';
      case 'vitest':
        return 'npx vitest run test_snippet.test.ts';
      case 'junit':
      case 'junit5':
        return 'mvn test  # or gradle test';
      case 'gtest':
      case 'googletest':
        return 'g++ -std=c++17 test_snippet.cpp -lgtest -lpthread && ./a.out';
      default:
        return 'Run in your local testing framework';
    }
  };

  return (
    <div className="space-y-4">
      {/* Test Intro Banner */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl flex items-start space-x-3">
        <FlaskConical className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300">
          <p className="font-semibold text-slate-100">
            Automated Unit Test Suite Generator
          </p>
          <p className="mt-1 leading-relaxed">
            The following unit tests were synthesised to target identified edge cases, error conditions,
            and nominal execution paths for the analyzed {language.toUpperCase()} code.
          </p>
        </div>
      </div>

      {tests.length === 0 ? (
        <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-xl">
          <FlaskConical className="w-8 h-8 text-slate-500 mx-auto mb-2" />
          <h4 className="text-sm font-semibold text-slate-300">No generated tests available</h4>
          <p className="text-xs text-slate-400 mt-1">
            Ensure the code snippet defines a callable function or class to generate framework-specific test suites.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {tests.map((test) => (
            <div
              key={test.id}
              className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow"
            >
              {/* Test Header */}
              <div className="px-4 py-2.5 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold uppercase bg-indigo-950/60 text-indigo-300 border border-indigo-700/50">
                    {test.test_framework}
                  </span>
                  {test.explanation && (
                    <span className="text-xs text-slate-400 truncate max-w-sm hidden sm:inline">
                      {test.explanation}
                    </span>
                  )}
                </div>

                <button
                  onClick={() => handleCopy(test.id, test.test_code)}
                  className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-white text-xs font-mono flex items-center space-x-1.5 transition-colors border border-slate-700"
                >
                  {copiedId === test.id ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy Test Code</span>
                    </>
                  )}
                </button>
              </div>

              {/* Test Code Body */}
              <div className="p-4 bg-slate-950 font-mono text-xs text-slate-200 overflow-x-auto leading-relaxed">
                <pre>{test.test_code}</pre>
              </div>

              {/* Execution Command Instruction */}
              <div className="px-4 py-2 bg-slate-900 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <div className="flex items-center space-x-2">
                  <Terminal className="w-3.5 h-3.5 text-slate-400" />
                  <span>Run Command:</span>
                  <code className="text-indigo-300 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                    {getRunnerInstructions(test.test_framework)}
                  </code>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
