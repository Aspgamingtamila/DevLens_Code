export type SupportedLanguage = 'c' | 'cpp' | 'python' | 'java' | 'javascript' | 'typescript';

export type FindingSeverity = 'critical' | 'high' | 'medium' | 'low' | 'info';

export type FindingCategory = 'bug' | 'security' | 'complexity' | 'style' | 'maintainability';

export type FindingSource = 'static' | 'ai' | 'hybrid';

export interface Finding {
  id: string;
  severity: FindingSeverity;
  category: FindingCategory;
  source: FindingSource;
  title: string;
  explanation: string;
  suggestion?: string | null;
  line_start?: number | null;
  line_end?: number | null;
  column_start?: number | null;
  column_end?: number | null;
  rule_id?: string | null;
  cwe_id?: string | null;
  confidence: number;
}

export interface AnalysisMetrics {
  lines_of_code: number;
  cyclomatic_complexity: number;
  comment_ratio: number;
  maintainability_index: number;
  correctness_score: number;
  security_score: number;
  complexity_score: number;
  readability_score: number;
  testing_score: number;
}

export interface GeneratedTest {
  id: string;
  test_framework: string;
  test_code: string;
  explanation?: string | null;
}

export interface Analysis {
  id: string;
  title: string;
  language: SupportedLanguage;
  code_snippet: string;
  quality_score: number;
  summary?: string | null;
  time_complexity?: string | null;
  space_complexity?: string | null;
  created_at: string;
  findings: Finding[];
  metrics?: AnalysisMetrics | null;
  generated_tests: GeneratedTest[];
}

export interface AnalysisSummary {
  id: string;
  title: string;
  language: string;
  quality_score: number;
  created_at: string;
  findings_count: number;
}

export interface AnalysisListResponse {
  items: AnalysisSummary[];
  total: number;
  page: number;
  page_size: number;
}

export interface User {
  id: string;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  expires_in: number;
}
