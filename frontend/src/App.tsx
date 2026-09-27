import { useState, useEffect } from 'react';
import { MantineProvider, Title, Group, Badge, Container, Grid, Card, Text, Stack, Alert, Loader } from '@mantine/core';
import { ShieldAlert } from 'lucide-react';
import '@mantine/core/styles.css';

import { Incident, TimelineItem, IncidentAnalysis } from './types';
import { fetchIncidents, fetchIncidentTimeline, runInvestigation } from './api';
import { IncidentList } from './components/IncidentList';
import { IncidentTimeline } from './components/IncidentTimeline';
import { InvestigationPanel } from './components/InvestigationPanel';

export default function App() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [analysis, setAnalysis] = useState<IncidentAnalysis | null>(null);
  
  const [loadingIncidents, setLoadingIncidents] = useState<boolean>(true);
  const [loadingTimeline, setLoadingTimeline] = useState<boolean>(false);
  const [loadingInvestigation, setLoadingInvestigation] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [investigationError, setInvestigationError] = useState<string | null>(null);

  const [highlightedEvidenceId, setHighlightedEvidenceId] = useState<string | null>(null);

  useEffect(() => {
    fetchIncidents()
      .then((data) => {
        setIncidents(data);
        if (data.length > 0) {
          setSelectedId(data[0].id);
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoadingIncidents(false));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setLoadingTimeline(true);
    setAnalysis(null);
    setInvestigationError(null);

    fetchIncidentTimeline(selectedId)
      .then((data) => setTimeline(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoadingTimeline(false));
  }, [selectedId]);

  const handleInvestigate = async () => {
    if (!selectedId) return;
    setLoadingInvestigation(true);
    setInvestigationError(null);

    try {
      const result = await runInvestigation(selectedId);
      setAnalysis(result);
    } catch (err: any) {
      setInvestigationError(err.message || 'Investigation failed');
    } finally {
      setLoadingInvestigation(false);
    }
  };

  const selectedIncident = incidents.find((i) => i.id === selectedId);

  return (
    <MantineProvider>
      <div style={{ backgroundColor: '#f8f9fa', minHeight: '100vh', padding: '16px' }}>
        <Container fluid>
          <Group justify="space-between" mb="md">
            <Group gap="xs">
              <ShieldAlert color="var(--mantine-color-red-6)" size={28} />
              <Title order={2}>AI SRE Incident Intelligence Platform</Title>
            </Group>
            <Badge color="blue" variant="light" size="lg">
              POC Environment
            </Badge>
          </Group>

          {error && (
            <Alert title="API Error" color="red" mb="md">
              {error}
            </Alert>
          )}

          <Grid>
            {/* Sidebar: Incident List */}
            <Grid.Col span={{ base: 12, md: 3 }}>
              {loadingIncidents ? (
                <Group justify="center" p="xl"><Loader /></Group>
              ) : (
                <IncidentList
                  incidents={incidents}
                  selectedId={selectedId}
                  onSelect={(id) => setSelectedId(id)}
                />
              )}
            </Grid.Col>

            {/* Main Content Area */}
            <Grid.Col span={{ base: 12, md: 9 }}>
              {selectedIncident ? (
                <Stack gap="md">
                  {/* Incident Header Card */}
                  <Card withBorder padding="md" radius="md">
                    <Group justify="space-between">
                      <div>
                        <Group gap="xs" mb={4}>
                          <Badge color="red">{selectedIncident.severity}</Badge>
                          <Badge color="blue" variant="light">{selectedIncident.status}</Badge>
                          <Text size="xs" c="dimmed">
                            Started: {new Date(selectedIncident.started_at).toLocaleString()}
                          </Text>
                        </Group>
                        <Title order={3}>{selectedIncident.id}: {selectedIncident.title}</Title>
                        <Text size="sm" c="dimmed" mt={4}>{selectedIncident.summary}</Text>
                      </div>

                      <Group gap="xs">
                        {selectedIncident.affected_services.map((svc) => (
                          <Badge key={svc.id} variant="filled" color="gray" size="md">
                            {svc.id}
                          </Badge>
                        ))}
                      </Group>
                    </Group>
                  </Card>

                  {/* Investigation + Timeline Layout */}
                  <Grid>
                    <Grid.Col span={{ base: 12, lg: 6 }}>
                      {loadingTimeline ? (
                        <Group justify="center" p="xl"><Loader /></Group>
                      ) : (
                        <IncidentTimeline
                          timeline={timeline}
                          highlightedIds={highlightedEvidenceId ? [highlightedEvidenceId] : []}
                        />
                      )}
                    </Grid.Col>

                    <Grid.Col span={{ base: 12, lg: 6 }}>
                      <InvestigationPanel
                        analysis={analysis}
                        loading={loadingInvestigation}
                        error={investigationError}
                        onInvestigate={handleInvestigate}
                        onHoverEvidence={(id) => setHighlightedEvidenceId(id)}
                      />
                    </Grid.Col>
                  </Grid>
                </Stack>
              ) : (
                <Card withBorder padding="xl" radius="md" style={{ textAlign: 'center' }}>
                  <Text c="dimmed">Select an incident from the sidebar to start investigating.</Text>
                </Card>
              )}
            </Grid.Col>
          </Grid>
        </Container>
      </div>
    </MantineProvider>
  );
}
