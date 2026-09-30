export interface Student {
  id: string;
  name?: string;
  education_level: string;
  course: string;
  percentage?: number;
  cgpa?: number;
  annual_family_income?: number;
  category?: string;
  gender?: string;
  domicile?: string;
}

export interface Opportunity {
  id: string;
  name: string;
  provider: string;
  description: string;
  opportunity_type: string;
  education_level: string[];
  course?: string[];
  field_of_study?: string[];
  minimum_cgpa?: number;
  minimum_percentage?: number;
  maximum_income?: number;
  minimum_income?: number;
  age_limit_max?: number;
  category?: string[];
  gender?: string;
  state?: string[];
  domicile_requirement?: string;
  institution_type?: string[];
  nationality_requirement?: string;
  benefit_description?: string;
  amount?: number;
  duration?: string;
  opening_date?: string;
  closing_date?: string;
  renewal_info?: string;
  required_documents?: string[];
  application_process?: string;
  official_url?: string;
  academic_year?: string;
  last_verified_date?: string;
  status: string;
  source_document_id?: string;
}

export interface DocumentChunk {
  id: string;
  source_document_id: string;
  content: string;
  chunk_index: number;
  section_title?: string;
  page_number?: number;
  chunk_metadata: Record<string, any>;
  created_at?: string;
}

export interface RuleResult {
  rule_name: string;
  condition: string;
  student_value?: any;
  required_value: string;
  result: string; // PASS, FAIL, WARN, UNKNOWN
  detail: string;
}

export interface EligibilityResult {
  opportunity_id: string;
  overall_status: string;
  rule_results: RuleResult[];
  summary: string;
}

export interface EligibilityCheckResponse {
  student_id: string;
  evaluations: EligibilityResult[];
}

export interface OpportunityScoreDetail {
  deadline_score: number;
  financial_need_score: number;
  academic_merit_score: number;
  demographic_match_score: number;
  total_score: number;
  reasons: string[];
}

export interface RankedOpportunity {
  rank: number;
  opportunity: Opportunity;
  eligibility: EligibilityResult;
  score: OpportunityScoreDetail;
}

export interface SourceAttribution {
  chunk_id: string;
  document_id?: string;
  opportunity_id?: string;
  opportunity_name?: string;
  similarity_score?: number;
  source_title?: string;
  page_number?: number;
  source_url?: string;
}

export interface AnswerResponse {
  answer: string;
  sources: SourceAttribution[];
}

export interface AskRequest {
  query: string;
  opportunity_id?: string;
  top_k?: number;
}
