import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';
import { IncidentList } from '../components/IncidentList';
import { IncidentTimeline } from '../components/IncidentTimeline';
import { InvestigationPanel } from '../components/InvestigationPanel';
import { Incident, TimelineItem, IncidentAnalysis } from '../types';

const mockIncidents: Incident[] = [
  {
    id: 'INC-1042',
    title: 'Checkout API elevated latency',
    status: 'INVESTIGATING',
    severity: 'SEV-2',
    started_at: '2026-09-20T14:31:00Z',
    summary: 'Database connection pool reached capacity.',
    affected_services: [{ id: 'checkout-api', name: 'Checkout API' }],
  },
  {
    id: 'INC-1017',
    title: 'Payment service connection error',
    status: 'RESOLVED',
    severity: 'SEV-3',
    started_at: '2026-09-15T10:00:00Z',
    summary: 'Third-party gateway timeout.',
    affected_services: [{ id: 'payments-api', name: 'Payments API' }],
  },
];

const mockTimeline: TimelineItem[] = [
  {
    id: 'dep-1',
    timestamp: '2026-09-20T14:15:00Z',
    type: 'deployment',
    service_id: 'checkout-api',
    title: 'Deployment v1.8.2 (checkout-api)',
    description: 'Deployed v1.8.2 by deployment pipeline',
  },
  {
    id: 'evt-101',
    timestamp: '2026-09-20T14:31:00Z',
    type: 'event',
    service_id: 'postgres-primary',
    title: 'Event: database_connection_exhaustion',
    description: 'PostgreSQL connection pool reached 200 active connections',
    severity: 'CRITICAL',
  },
];

const mockAnalysis: IncidentAnalysis = {
  summary: 'PostgreSQL connection exhaustion caused elevated latency on checkout-api.',
  likely_root_cause: 'Deployment v1.8.2 introduced connection leaks.',
  confidence: 0.88,
  root_cause_evidence_ids: ['dep-1', 'evt-101'],
  timeline: [
    {
      timestamp: '2026-09-20 14:15',
      description: 'v1.8.2 deployed',
      evidence_ids: ['dep-1'],
    },
  ],
  evidence: [
    {
      evidence_id: 'dep-1',
      description: 'Deployment v1.8.2 record',
    },
  ],
  related_incidents: ['INC-1017'],
  uncertainties: ['Exact commit author unknown.'],
};

const renderWithMantine = (component: React.ReactNode) => {
  return render(<MantineProvider>{component}</MantineProvider>);
};

describe('IncidentList Component', () => {
  it('renders list of incidents with severity and title', () => {
    renderWithMantine(<IncidentList incidents={mockIncidents} selectedId="INC-1042" onSelect={() => {}} />);
    expect(screen.getByText(/INC-1042: Checkout API elevated latency/i)).toBeInTheDocument();
    expect(screen.getByText(/INC-1017: Payment service connection error/i)).toBeInTheDocument();
    expect(screen.getByText('SEV-2')).toBeInTheDocument();
  });

  it('calls onSelect when an incident card is clicked', () => {
    const handleSelect = vi.fn();
    renderWithMantine(<IncidentList incidents={mockIncidents} selectedId="INC-1042" onSelect={handleSelect} />);
    
    fireEvent.click(screen.getByText(/INC-1017: Payment service connection error/i));
    expect(handleSelect).toHaveBeenCalledWith('INC-1017');
  });
});

describe('IncidentTimeline Component', () => {
  it('renders timeline events and deployment items', () => {
    renderWithMantine(<IncidentTimeline timeline={mockTimeline} />);
    expect(screen.getByText('Deployment v1.8.2 (checkout-api)')).toBeInTheDocument();
    expect(screen.getByText('Event: database_connection_exhaustion')).toBeInTheDocument();
    expect(screen.getByText(/PostgreSQL connection pool reached 200 active connections/i)).toBeInTheDocument();
  });

  it('highlights cited evidence items', () => {
    renderWithMantine(<IncidentTimeline timeline={mockTimeline} highlightedIds={['dep-1']} />);
    expect(screen.getByText('Cited Evidence')).toBeInTheDocument();
  });
});

describe('InvestigationPanel Component', () => {
  it('renders prompt when no analysis is present', () => {
    renderWithMantine(
      <InvestigationPanel analysis={null} loading={false} error={null} onInvestigate={() => {}} />
    );
    expect(screen.getByText(/No AI Analysis Generated Yet/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Investigate Incident/i })).toBeInTheDocument();
  });

  it('renders AI analysis, root cause, and citations when present', () => {
    renderWithMantine(
      <InvestigationPanel analysis={mockAnalysis} loading={false} error={null} onInvestigate={() => {}} />
    );
    expect(screen.getByText(/Deployment v1.8.2 introduced connection leaks./i)).toBeInTheDocument();
    expect(screen.getByText('88%')).toBeInTheDocument();
    expect(screen.getAllByText('dep-1')[0]).toBeInTheDocument();
    expect(screen.getByText('INC-1017')).toBeInTheDocument();
  });

  it('triggers onInvestigate when button is clicked', () => {
    const handleInvestigate = vi.fn();
    renderWithMantine(
      <InvestigationPanel analysis={null} loading={false} error={null} onInvestigate={handleInvestigate} />
    );
    fireEvent.click(screen.getByRole('button', { name: /Investigate Incident/i }));
    expect(handleInvestigate).toHaveBeenCalledOnce();
  });
});
