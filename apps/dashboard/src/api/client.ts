import axios from 'axios';
import { AnalyticsSummary, AlertItem, HealthRecord } from '../types';

const API_BASE = '/api/v1';

export const isDemoMode = (import.meta as any).env?.VITE_DEMO_MODE === 'true';


export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auto attach token if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('ohk_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const fetchHealthStatus = async () => {
  try {
    const res = await api.get('/health');
    return res.data;
  } catch (err) {
    if (isDemoMode) {
      return { status: 'demo', service: 'openhealthkit-demo-mode' };
    }
    throw err;
  }
};

export const fetchAnalyticsSummary = async (): Promise<AnalyticsSummary> => {
  try {
    const res = await api.get('/analytics/summary');
    return res.data;
  } catch (err) {
    if (isDemoMode) {
      return {
        total_users: 4,
        total_organizations: 1,
        total_communities: 4,
        total_health_records: 25,
        total_observations: 58,
        active_alerts_count: 5,
        observations_by_type: [
          { category: 'water_turbidity_ntu', count: 18 },
          { category: 'fever_body_temp_c', count: 15 },
          { category: 'systolic_bp_mmHg', count: 14 },
          { category: 'blood_glucose_mg_dl', count: 11 },
        ],
        alerts_by_severity: [
          { severity: 'CRITICAL', count: 2 },
          { severity: 'HIGH', count: 3 },
          { severity: 'MEDIUM', count: 4 },
          { severity: 'LOW', count: 1 },
        ],
        sync_metrics: {
          pending_count: 3,
          synced_count: 42,
          conflict_count: 1,
          failed_count: 0,
        },
        is_demo_data: true,
      };
    }
    throw err;
  }
};

export const fetchRecords = async (): Promise<HealthRecord[]> => {
  const res = await api.get('/records');
  return res.data;
};

export const createRecord = async (data: Partial<HealthRecord>) => {
  const res = await api.post('/records', data);
  return res.data;
};

export const fetchAlerts = async (): Promise<AlertItem[]> => {
  const res = await api.get('/alerts');
  return res.data;
};

export const updateAlertStatus = async (alertId: string, status: string) => {
  const res = await api.put(`/alerts/${alertId}/status`, { status });
  return res.data;
};
