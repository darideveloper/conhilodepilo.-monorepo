import { apiClient } from "../client";

export interface BookingPayload {
  clientName: string;
  clientEmail: string;
  clientPhone: string;
  service_ids: number[];
  date: string;
  startTime: string;
  specialRequests: string;
}

export async function submitBooking(payload: BookingPayload): Promise<any> {
  return await apiClient<any>("bookings/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
