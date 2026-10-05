import React, { useState, useEffect, useRef } from 'react';
import {
  Play,
  RotateCcw,
  Sparkles,
  FileCode2,
  Trash,
  CheckCircle,
} from 'lucide-react';
import { SupportedLanguage } from '../types';
import { SAMPLE_SNIPPETS } from './sampleCodes';

interface CodeEditorProps {
  code: string;
  setCode: (code: string) => void;
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
  enableAi: boolean;
  setEnableAi: (enable: boolean) => void;
  onAnalyze: () => void;
  isLoading: boolean;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  setCode,
  language,
  setLanguage,
  enableAi,
  setEnableAi,
  onAnalyze,
  isLoading,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [lineCount, setLineCount] = useState(1);

  useEffect(() => {
    const lines = code.split('\n').length;
    setLineCount(Math.max(1, lines));
  }, [code]);

  // Handle Tab key to insert 2 spaces
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = textareaRef.current;
      if (!textarea) return;

      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;

      const newCode = code.substring(0, start) + '  ' + code.substring(end);
      setCode(newCode);

      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 2;
      }, 0);
    } else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      if (!isLoading && code.trim().length > 0) {
        onAnalyze();
      }
    }
  };

  const handleLoadSample = (sampleName: string) => {
    const sample = SAMPLE_SNIPPETS.find((s) => s.name === sampleName);
    if (sample) {
      setLanguage(sample.language);
      setCode(sample.code);
    }
  };

  const handleClear = () => {
    setCode('');
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
      {/* Editor Toolbar */}
      <div className="px-4 py-2.5 bg-slate-950/70 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          {/* Language Selector */}
          <div className="flex items-center space-x-1.5">
            <span className="text-xs text-slate-400 font-medium">Lang:</span>
            <select
              value={language}
              aria-label="Target Programming Language"
              onChange={(e) => setLanguage(e.target.value as SupportedLanguage)}
              className="bg-slate-800 text-slate-200 border border-slate-700 text-xs rounded-md px-2.5 py-1 focus:ring-1 focus:ring-indigo-500 focus:outline-none font-mono font-medium"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="c">C</option>
              <option value="cpp">C++</option>
              <option value="java">Java</option>
            </select>
          </div>

          {/* Load Sample Presets */}
          <div className="flex items-center space-x-1.5">
            <FileCode2 className="w-3.5 h-3.5 text-slate-400" />
            <select
              defaultValue=""
              aria-label="Load Example Snippet"
              onChange={(e) => {
                if (e.target.value) {
                  handleLoadSample(e.target.value);
                  e.target.value = '';
                }
              }}
              className="bg-slate-800 text-slate-300 border border-slate-700 text-xs rounded-md px-2 py-1 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
            >
              <option value="" disabled>
                Load Example Snippet...
              </option>
              {SAMPLE_SNIPPETS.map((s) => (
                <option key={s.name} value={s.name}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* AI synthesis toggle and clear */}
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-1.5 text-xs text-slate-300 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={enableAi}
              onChange={(e) => setEnableAi(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-indigo-500 h-3.5 w-3.5"
            />
            <span className="flex items-center space-x-1 text-slate-300">
              <Sparkles className="w-3 h-3 text-indigo-400" />
              <span>AI Explanations</span>
            </span>
          </label>

          <button
            onClick={handleClear}
            className="text-xs text-slate-400 hover:text-slate-200 flex items-center space-x-1 transition-colors px-2 py-1 rounded hover:bg-slate-800"
            title="Clear Editor"
          >
            <Trash className="w-3 h-3" />
            <span>Clear</span>
          </button>
        </div>
      </div>

      {/* Editor Body with Gutter */}
      <div className="relative flex-1 flex overflow-hidden font-mono text-xs sm:text-sm bg-slate-950">
        {/* Line Numbers Gutter */}
        <div className="py-3 px-2 bg-slate-900/60 border-r border-slate-800/80 text-slate-600 select-none text-right font-mono min-w-[2.75rem] overflow-hidden">
          {Array.from({ length: lineCount }).map((_, i) => (
            <div key={i} className="leading-6">
              {i + 1}
            </div>
          ))}
        </div>

        {/* Text Area */}
        <div className="relative flex-1 h-full overflow-hidden">
          <textarea
            ref={textareaRef}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`// Paste your ${language.toUpperCase()} code here, or select an example above...`}
            spellCheck={false}
            className="w-full h-full p-3 bg-transparent text-slate-200 resize-none font-mono focus:outline-none leading-6 overflow-y-auto"
          />
        </div>
      </div>

      {/* Editor Footer / Action Bar */}
      <div className="px-4 py-2.5 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-4 text-xs font-mono text-slate-400">
          <span>{lineCount} lines</span>
          <span>{code.length} chars</span>
          <span className="hidden sm:inline text-slate-500">
            Press <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">Ctrl</kbd> + <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">Enter</kbd> to analyze
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setCode('')}
            disabled={isLoading || !code}
            className="px-3 py-1.5 rounded-md text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800 disabled:opacity-40 transition-colors"
          >
            Reset
          </button>

          <button
            onClick={onAnalyze}
            disabled={isLoading || code.trim().length === 0}
            className="px-4 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white text-xs font-semibold flex items-center space-x-2 shadow-md transition-all active:scale-[0.98]"
          >
            {isLoading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                <span>Analyzing Pipeline...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Analyze Code</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
