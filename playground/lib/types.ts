/**
 * Mirrors job_matcher/schemas.py exactly (backend/job_matcher/schemas.py) —
 * the discriminated JobOutcome union `/analyze` returns. Kept in sync by
 * hand (small, stable contract); the backend's OpenAPI document is the
 * source of truth if these ever drift.
 */

export type ExperienceAlignment = "exact" | "close" | "partial" | "far";
export type DomainAlignment = "exact" | "related" | "transferable" | "none";
export type MatchStatus =
  | "strong_match"
  | "good_match"
  | "moderate_match"
  | "weak_match"
  | "no_match";

export interface SkillMatch {
  skill: string;
  matched: boolean;
  evidence: string;
}

export interface JobAnalysis {
  job_title: string;
  company_name: string | null;
  required_skills: SkillMatch[];
  preferred_skills: SkillMatch[];
  experience_alignment: ExperienceAlignment;
  experience_years_context: string;
  domain_alignment: DomainAlignment;
  strengths: string[];
  gaps: string[];
  resume_improvements: string[];
  ats_keywords_missing: string[];
  cover_letter_angle: string;
  cover_letter_paragraphs: string[];
  summary: string;
}

export interface ScoreBreakdown {
  required_skills_score: number; // 0-60 (60 when the preferred budget reallocates)
  preferred_skills_score: number; // 0-20
  experience_score: number; // 0-20
  domain_score: number; // 0-20
  total_score: number; // 0-100
}

export interface JobReport {
  run_id: string;
  generated_at: string;
  job_source: string;
  fetch_status: "ok";
  resume_file: string;
  models: Record<string, string>;
  analysis: JobAnalysis;
  cover_letter_text: string;
  score_breakdown: ScoreBreakdown;
  match_status: MatchStatus;
  recommendation: string;
}

export interface JobFetchFailure {
  run_id: string;
  generated_at: string;
  job_source: string;
  fetch_status: "failed";
  reason: string;
  attempted_at: string;
}

export type JobOutcome = JobReport | JobFetchFailure;

export const MATCH_STATUS_LABEL: Record<MatchStatus, string> = {
  strong_match: "Strong match",
  good_match: "Good match",
  moderate_match: "Moderate match",
  weak_match: "Weak match",
  no_match: "No match",
};

// Industry-standard green->amber->red grading scale (credit-score / ATS
// convention — best is always green, never the brand color). Brand purple
// is reserved for chrome (header, sidebar accents), never a quality signal.
// 1:1 with the five MatchStatus literal values the backend actually emits.
export const MATCH_STATUS_CLASSES: Record<MatchStatus, string> = {
  strong_match: "bg-emerald-600 text-white",
  good_match: "bg-lime-500 text-white",
  moderate_match: "bg-amber-500 text-white",
  weak_match: "bg-orange-500 text-white",
  no_match: "bg-red-500 text-white",
};
