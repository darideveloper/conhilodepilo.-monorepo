import { format, addDays } from 'date-fns';

// Formats a Date as "YYYY-MM-DD" for use in API payloads.
export function toApiDate(date: Date): string {
  return format(date, 'yyyy-MM-dd');
}

// Formats a Date as "HH:MM" (24-hour) for use in API payloads.
export function toApiTime(date: Date): string {
  return format(date, 'HH:mm');
}

// Returns a Date N calendar days from today.
export function daysFromNow(n: number): Date {
  return addDays(new Date(), n);
}
