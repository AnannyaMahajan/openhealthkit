export interface HealthRecord {
  id: string;
  patient_identifier: string;
  age_years?: number;
  gender?: string;
  community_id?: string;
  metadata_json?: string;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  observations: Observation[];
}

export interface Observation {
  id: string;
  health_record_id: string;
  observation_type: string;
  value_number?: number;
  value_text?: string;
  unit?: string;
  observed_at: string;
}

export interface AlertItem {
  id: string;
  rule_id?: string;
  title: string;
  description: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED';
  health_record_id?: string;
  observation_id?: string;
  created_at: string;
  updated_at: string;
}

export interface SyncItem {
  id: string;
  entity_type: string;
  entity_id: string;
  action: 'CREATE' | 'UPDATE' | 'DELETE';
  state: 'PENDING' | 'SYNCING' | 'SYNCED' | 'FAILED' | 'CONFLICT';
  client_timestamp: string;
  payload: Record<string, any>;
}

export interface AnalyticsSummary {
  total_users: number;
  total_organizations: number;
  total_communities: number;
  total_health_records: number;
  total_observations: number;
  active_alerts_count: number;
  observations_by_type: Array<{ category: string; count: number }>;
  alerts_by_severity: Array<{ severity: string; count: number }>;
  sync_metrics: {
    pending_count: number;
    synced_count: number;
    conflict_count: number;
    failed_count: number;
  };
  is_demo_data: boolean;
}
