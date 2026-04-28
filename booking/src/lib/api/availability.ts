export interface Availability {
  available: Date[];
}

export const fetchAvailability = async (serviceIds: string[], signal: AbortSignal): Promise<Availability> => {
  const url = `${import.meta.env.PUBLIC_API_URL}availability/days/?service_ids=${serviceIds.join(',')}`;
  const response = await fetch(url, { signal });

  if (!response.ok) {
    throw new Error('Failed to fetch availability');
  }

  const availableDates: string[] = await response.json();

  return {
    available: availableDates.map((d: string) => {
      const [year, month, day] = d.split('-').map(Number);
      return new Date(year, month - 1, day);
    }),
  };
};

export const fetchSlots = async (serviceIds: string[], date: string, signal?: AbortSignal): Promise<string[]> => {
  const url = `${import.meta.env.PUBLIC_API_URL}availability/slots/?service_ids=${serviceIds.join(',')}&date=${date}`;
  const response = await fetch(url, { signal });

  if (!response.ok) {
    throw new Error('Failed to fetch slots');
  }

  return await response.json();
};
