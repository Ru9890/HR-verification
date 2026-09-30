import {
  VerificationReportResponse,
  SampleResumeInfo,
  AppSettings
} from '../types';

const API_BASE = 'http://localhost:8000/api';

export async function uploadResumePdf(file: File): Promise<VerificationReportResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/verify/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to upload and verify resume' }));
    throw new Error(err.detail || 'Failed to upload and verify resume');
  }

  return res.json();
}

export async function verifySampleResume(sampleId: string): Promise<VerificationReportResponse> {
  const res = await fetch(`${API_BASE}/verify/sample/${sampleId}`, {
    method: 'POST',
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to verify sample resume' }));
    throw new Error(err.detail || 'Failed to verify sample resume');
  }

  return res.json();
}

export async function getReport(reportId: string): Promise<VerificationReportResponse> {
  const res = await fetch(`${API_BASE}/verify/${reportId}`);
  if (!res.ok) {
    throw new Error('Failed to fetch verification report');
  }
  return res.json();
}

export async function getRecentReports(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/reports/`);
  if (!res.ok) {
    return [];
  }
  return res.json();
}

export async function deleteReport(reportId: string): Promise<void> {
  await fetch(`${API_BASE}/reports/${reportId}`, { method: 'DELETE' });
}

export async function getSampleResumes(): Promise<SampleResumeInfo[]> {
  const res = await fetch(`${API_BASE}/samples/`);
  if (!res.ok) {
    return [];
  }
  return res.json();
}

export function getSamplePdfDownloadUrl(sampleId: string): string {
  return `${API_BASE}/samples/${sampleId}/pdf`;
}

export async function getSettings(): Promise<AppSettings> {
  const res = await fetch(`${API_BASE}/settings/`);
  if (!res.ok) {
    throw new Error('Failed to fetch settings');
  }
  return res.json();
}

export async function updateSettings(settings: Partial<AppSettings> & { github_token?: string }): Promise<any> {
  const res = await fetch(`${API_BASE}/settings/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!res.ok) {
    throw new Error('Failed to update settings');
  }
  return res.json();
}

export async function testGitHubConnection(): Promise<{ success: boolean; message: string; details?: any }> {
  const res = await fetch(`${API_BASE}/settings/test-github`, {
    method: 'POST',
  });
  if (!res.ok) {
    return { success: false, message: 'Failed to contact backend API' };
  }
  return res.json();
}
