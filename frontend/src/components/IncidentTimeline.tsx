import React from 'react';
import { Timeline, Text, Badge, Card, Group } from '@mantine/core';
import { Activity, GitCommit, AlertTriangle, Cpu } from 'lucide-react';
import { TimelineItem } from '../types';

interface IncidentTimelineProps {
  timeline: TimelineItem[];
  highlightedIds?: string[];
}

export const IncidentTimeline: React.FC<IncidentTimelineProps> = ({ timeline, highlightedIds = [] }) => {
  const getIcon = (type: string, severity?: string) => {
    if (type === 'deployment') return <GitCommit size={16} />;
    if (type === 'metric') return <Cpu size={16} />;
    if (severity === 'CRITICAL' || severity === 'ERROR') return <AlertTriangle size={16} />;
    return <Activity size={16} />;
  };

  const getColor = (type: string, severity?: string) => {
    if (type === 'deployment') return 'violet';
    if (type === 'metric') return 'cyan';
    if (severity === 'CRITICAL') return 'red';
    if (severity === 'WARNING') return 'orange';
    return 'blue';
  };

  return (
    <Card withBorder padding="md" radius="md">
      <Group justify="space-between" mb="md">
        <Text fw={700} size="md">Observed Telemetry Timeline</Text>
        <Badge variant="dot" color="teal">Observed Telemetry</Badge>
      </Group>

      {timeline.length === 0 ? (
        <Text size="sm" c="dimmed">No timeline events recorded.</Text>
      ) : (
        <Timeline active={timeline.length - 1} bulletSize={26} lineWidth={2}>
          {timeline.map((item) => {
            const isHighlighted = highlightedIds.includes(item.id);
            return (
              <Timeline.Item
                key={item.id}
                bullet={getIcon(item.type, item.severity)}
                color={getColor(item.type, item.severity)}
                title={
                  <Group gap="xs">
                    <Text size="sm" fw={600}>{item.title}</Text>
                    {item.service_id && (
                      <Badge variant="outline" size="xs" color="gray">
                        {item.service_id}
                      </Badge>
                    )}
                    {isHighlighted && (
                      <Badge color="yellow" variant="filled" size="xs">
                        Cited Evidence
                      </Badge>
                    )}
                  </Group>
                }
                style={{
                  padding: isHighlighted ? '8px' : undefined,
                  borderRadius: isHighlighted ? '6px' : undefined,
                  backgroundColor: isHighlighted ? 'var(--mantine-color-yellow-0)' : undefined,
                  transition: 'background-color 0.2s ease',
                }}
              >
                <Text color="dimmed" size="xs" mb={4}>
                  {new Date(item.timestamp).toLocaleString()}
                </Text>
                <Text size="xs">{item.description}</Text>
              </Timeline.Item>
            );
          })}
        </Timeline>
      )}
    </Card>
  );
};
