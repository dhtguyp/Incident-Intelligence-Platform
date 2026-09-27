import React from 'react';
import { Card, Text, Badge, Group, Stack, ScrollArea } from '@mantine/core';
import { Clock } from 'lucide-react';
import { Incident } from '../types';

interface IncidentListProps {
  incidents: Incident[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export const IncidentList: React.FC<IncidentListProps> = ({ incidents, selectedId, onSelect }) => {
  const getSeverityColor = (sev: string) => {
    switch (sev) {
      case 'SEV-1': return 'red';
      case 'SEV-2': return 'orange';
      case 'SEV-3': return 'yellow';
      default: return 'blue';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'OPEN': return 'red';
      case 'INVESTIGATING': return 'blue';
      case 'RESOLVED': return 'green';
      default: return 'gray';
    }
  };

  return (
    <Stack gap="xs">
      <Text fw={700} size="lg" mb="xs">Production Incidents</Text>
      <ScrollArea h="calc(100vh - 120px)">
        <Stack gap="sm">
          {incidents.map((incident) => {
            const isSelected = incident.id === selectedId;
            return (
              <Card
                key={incident.id}
                shadow={isSelected ? 'md' : 'xs'}
                padding="sm"
                radius="md"
                withBorder
                style={{
                  cursor: 'pointer',
                  borderColor: isSelected ? 'var(--mantine-color-blue-5)' : undefined,
                  backgroundColor: isSelected ? 'var(--mantine-color-blue-0)' : undefined,
                }}
                onClick={() => onSelect(incident.id)}
              >
                <Group justify="space-between" mb="xs">
                  <Badge color={getSeverityColor(incident.severity)} size="sm">
                    {incident.severity}
                  </Badge>
                  <Badge color={getStatusColor(incident.status)} variant="light" size="sm">
                    {incident.status}
                  </Badge>
                </Group>
                
                <Text fw={600} size="sm" lineClamp={2} mb={4}>
                  {incident.id}: {incident.title}
                </Text>

                <Group gap="xs" mt="xs">
                  <Clock size={12} style={{ opacity: 0.6 }} />
                  <Text size="xs" c="dimmed">
                    {new Date(incident.started_at).toLocaleString()}
                  </Text>
                </Group>

                <Group gap={4} mt="xs">
                  {incident.affected_services.map((svc) => (
                    <Badge key={svc.id} variant="outline" size="xs" color="gray">
                      {svc.id}
                    </Badge>
                  ))}
                </Group>
              </Card>
            );
          })}
        </Stack>
      </ScrollArea>
    </Stack>
  );
};
