// Thin REST wrappers around the Dashboard API for programmatic test data management.
// Functions accept Playwright's APIRequestContext so they automatically inherit
// ignoreHTTPSErrors: true from playwright.config.ts (portless uses self-signed certs).

import type { APIRequestContext } from '@playwright/test';

const dashboardUrl = () =>
  process.env['DASHBOARD_URL'] ?? 'https://dashboard.conhilodepilo';

export interface CreateBookingPayload {
  clientName: string;
  clientEmail: string;
  clientPhone?: string;
  service_ids: number[];
  date: string;       // YYYY-MM-DD
  startTime: string;  // HH:MM
  specialRequests?: string;
}

export interface BookingResponse {
  id: number;
  client_name: string;
  client_email: string;
  start_time: string;
  payment_required?: boolean;
  checkout_url?: string;
}

export async function createBooking(
  request: APIRequestContext,
  payload: CreateBookingPayload,
): Promise<{ id: number }> {
  const res = await request.post(`${dashboardUrl()}/api/bookings/`, {
    data: payload,
  });

  if (!res.ok()) {
    const body = await res.text();
    throw new Error(`createBooking failed (${res.status()}): ${body}`);
  }

  const data = (await res.json()) as BookingResponse;
  return { id: data.id };
}

export interface ServiceCategory {
  id: number;
  name: string;
  services: Array<{ id: number; title: string }>;
}

export async function fetchServices(
  request: APIRequestContext,
): Promise<ServiceCategory[]> {
  const res = await request.get(`${dashboardUrl()}/api/services/`);
  if (!res.ok()) throw new Error(`fetchServices failed (${res.status()})`);
  return res.json() as Promise<ServiceCategory[]>;
}

export async function fetchAvailableSlots(
  request: APIRequestContext,
  serviceIds: number[],
  date: string,
): Promise<string[]> {
  const res = await request.get(`${dashboardUrl()}/api/availability/slots/`, {
    params: {
      service_ids: serviceIds.join(','),
      date,
    },
  });
  if (!res.ok()) throw new Error(`fetchAvailableSlots failed (${res.status()})`);
  return res.json() as Promise<string[]>;
}
