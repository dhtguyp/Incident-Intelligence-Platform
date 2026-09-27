import { Incident, TimelineItem, IncidentAnalysis } from './types';

const API_BASE = '/api';

export async function fetchIncidents(): Promise<Incident[]> {
  const res = await fetch(`${API_BASE}/incidents`);
  if (!res.ok) {
    throw new Error(`Failed to fetch incidents: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchIncident(id: string): Promise<Incident> {
  const res = await fetch(`${API_BASE}/incidents/${id}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch incident ${id}: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchIncidentTimeline(id: string): Promise<TimelineItem[]> {
  const res = await fetch(`${API_BASE}/incidents/${id}/timeline`);
  if (!res.ok) {
    throw new Error(`Failed to fetch timeline for ${id}: ${res.statusText}`);
  }
  return res.json();
}

export async function runInvestigation(id: string): Promise<IncidentAnalysis> {
  const res = await fetch(`${API_BASE}/incidents/${id}/investigate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || `Investigation failed: ${res.statusText}`);
  }
  return res.json();
}
