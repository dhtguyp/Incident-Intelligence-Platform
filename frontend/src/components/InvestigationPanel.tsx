import React from 'react';
import { Card, Text, Badge, Button, Group, Stack, Accordion, List, Alert, ThemeIcon } from '@mantine/core';
import { Sparkles, AlertCircle, HelpCircle, FileText, Link2 } from 'lucide-react';
import { IncidentAnalysis } from '../types';

interface InvestigationPanelProps {
  analysis: IncidentAnalysis | null;
  loading: boolean;
  error: string | null;
  onInvestigate: () => void;
  onHoverEvidence?: (id: string | null) => void;
}

export const InvestigationPanel: React.FC<InvestigationPanelProps> = ({
  analysis,
  loading,
  error,
  onInvestigate,
  onHoverEvidence,
}) => {
  return (
    <Card withBorder padding="md" radius="md">
      <Group justify="space-between" mb="md">
        <Group gap="xs">
          <ThemeIcon color="grape" variant="light" size="lg">
            <Sparkles size={20} />
          </ThemeIcon>
          <div>
            <Text fw={700} size="md">AI Investigation Engine</Text>
            <Text size="xs" c="dimmed">Grounding telemetry & semantic retrieval context</Text>
          </div>
        </Group>

        <Button
          leftSection={<Sparkles size={16} />}
          color="grape"
          loading={loading}
          onClick={onInvestigate}
        >
          {analysis ? 'Re-investigate' : 'Investigate Incident'}
        </Button>
      </Group>

      {error && (
        <Alert icon={<AlertCircle size={16} />} title="Investigation Failed" color="red" mb="md">
          {error}
        </Alert>
      )}

      {!analysis && !loading && !error && (
        <Card bg="gray.0" padding="lg" radius="md" style={{ textAlign: 'center' }}>
          <Sparkles size={32} style={{ opacity: 0.4, margin: '0 auto 8px auto' }} />
          <Text size="sm" fw={500}>No AI Analysis Generated Yet</Text>
          <Text size="xs" c="dimmed" mt={4}>
            Click "Investigate Incident" to run hybrid SQL + Qdrant evidence retrieval and LLM reasoning.
          </Text>
        </Card>
      )}

      {analysis && (
        <Stack gap="md">
          {/* Summary & Cause (AI Inference) */}
          <Card bg="violet.0" padding="sm" radius="md" withBorder style={{ borderColor: 'var(--mantine-color-violet-3)' }}>
            <Group justify="space-between" mb="xs">
              <Badge color="violet" variant="filled">AI Inference</Badge>
              <Group gap="xs">
                <Text size="xs" fw={500}>Confidence:</Text>
                <Badge color={analysis.confidence > 0.7 ? 'green' : 'orange'}>
                  {Math.round(analysis.confidence * 100)}%
                </Badge>
              </Group>
            </Group>

            <Text size="sm" fw={600} mb={4}>Likely Root Cause:</Text>
            <Text size="sm" mb="sm">{analysis.likely_root_cause}</Text>

            <Text size="xs" fw={600} c="dimmed">Summary:</Text>
            <Text size="xs" c="dimmed">{analysis.summary}</Text>
          </Card>

          {/* Key Supporting Evidence Citations */}
          <div>
            <Group justify="space-between" mb="xs">
              <Text fw={600} size="sm">Grounding Evidence Citations</Text>
              <Badge variant="light" color="teal">Observed Evidence</Badge>
            </Group>
            <Stack gap="xs">
              {analysis.evidence.map((item) => (
                <Card
                  key={item.evidence_id}
                  padding="xs"
                  withBorder
                  radius="sm"
                  onMouseEnter={() => onHoverEvidence?.(item.evidence_id)}
                  onMouseLeave={() => onHoverEvidence?.(null)}
                  style={{ cursor: 'pointer' }}
                >
                  <Group justify="space-between">
                    <Group gap="xs">
                      <FileText size={14} color="var(--mantine-color-teal-6)" />
                      <Badge size="xs" variant="outline" color="teal">{item.evidence_id}</Badge>
                    </Group>
                  </Group>
                  <Text size="xs" mt={4}>{item.description}</Text>
                </Card>
              ))}
            </Stack>
          </div>

          {/* AI Reconstructed Timeline */}
          {analysis.timeline.length > 0 && (
            <div>
              <Text fw={600} size="sm" mb="xs">Reconstructed Incident Sequence</Text>
              <Accordion variant="separated">
                {analysis.timeline.map((entry, idx) => (
                  <Accordion.Item key={idx} value={`item-${idx}`}>
                    <Accordion.Control icon={<ClockIcon size={14} />}>
                      <Group justify="space-between">
                        <Text size="xs" fw={500}>{entry.description}</Text>
                        <Text size="xs" c="dimmed">{entry.timestamp}</Text>
                      </Group>
                    </Accordion.Control>
                    <Accordion.Panel>
                      <Text size="xs" c="dimmed" mb={4}>Cited Evidence IDs:</Text>
                      <Group gap={4}>
                        {entry.evidence_ids.map((id) => (
                          <Badge key={id} size="xs" color="blue" variant="light">
                            {id}
                          </Badge>
                        ))}
                      </Group>
                    </Accordion.Panel>
                  </Accordion.Item>
                ))}
              </Accordion>
            </div>
          )}

          {/* Related Historical Incidents */}
          {analysis.related_incidents.length > 0 && (
            <div>
              <Text fw={600} size="sm" mb="xs">Related Historical Incidents</Text>
              <Group gap="xs">
                {analysis.related_incidents.map((incId) => (
                  <Badge key={incId} variant="outline" color="indigo" leftSection={<Link2 size={12} />}>
                    {incId}
                  </Badge>
                ))}
              </Group>
            </div>
          )}

          {/* Identified Uncertainties */}
          {analysis.uncertainties.length > 0 && (
            <Alert icon={<HelpCircle size={16} />} title="Uncertainties & Knowledge Gaps" color="gray" variant="light">
              <List size="xs" spacing={2}>
                {analysis.uncertainties.map((u, i) => (
                  <List.Item key={i}>{u}</List.Item>
                ))}
              </List>
            </Alert>
          )}
        </Stack>
      )}
    </Card>
  );
};

const ClockIcon = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
);
