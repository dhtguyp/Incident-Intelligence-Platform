export interface Service {
  id: string;
  name: string;
  description?: string;
  owner_team?: string;
}

export interface Incident {
  id: string;
  title: string;
  status: 'OPEN' | 'INVESTIGATING' | 'RESOLVED';
  severity: 'SEV-1' | 'SEV-2' | 'SEV-3';
  started_at: string;
  resolved_at?: string;
  summary?: string;
  affected_services: Service[];
}

export interface TimelineItem {
  id: string;
  timestamp: string;
  type: 'event' | 'deployment' | 'metric';
  service_id?: string;
  title: string;
  description: string;
  severity?: string;
  details?: Record<string, any>;
}

export interface EvidenceCitation {
  evidence_id: string;
  description: string;
}

export interface TimelineAnalysisItem {
  timestamp: string;
  description: string;
  evidence_ids: string[];
}

export interface IncidentAnalysis {
  summary: string;
  likely_root_cause: string;
  confidence: number;
  root_cause_evidence_ids: string[];
  timeline: TimelineAnalysisItem[];
  evidence: EvidenceCitation[];
  related_incidents: string[];
  uncertainties: string[];
}
