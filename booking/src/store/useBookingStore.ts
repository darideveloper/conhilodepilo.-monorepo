import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { fetchAvailability } from '../lib/api/availability';
import { fetchConfig as fetchAppConfig } from '../lib/api/endpoints/config';
import { fetchServices as fetchAppServices, type ServiceCategory } from '../lib/api/endpoints/services';

export type Language = 'es' | 'en';
export type Theme = 'light' | 'dark';

export interface AppConfig {
  brand_color: string;
  logo: string;
  currency: string;
  contact_email: string;
  contact_phone: string;
  company_name: string;
  timezone: string;
  event_type_label: string;
  event_label: string;
  availability_free_label: string;
  availability_regular_label: string;
  availability_no_free_label: string;
  extras_label: string;
}

interface Availability {
  available: Date[];
  limited?: Date[];
  booked?: Date[];
}

export interface SelectedService {
  serviceTypeId: string;
  serviceId: string;
}

interface BookingState {
  language: Language;
  theme: Theme;
  selectedDate: Date | undefined;
  currentStep: number;
  config: AppConfig | null;
  isConfigLoading: boolean;
  services: ServiceCategory[];
  isServicesLoading: boolean;
  formData: {
    fullName: string;
    email: string;
    selectedServices: SelectedService[];
    serviceGroup: string | null;
    lockedGroupId: string | null;
    guests: number;
    specialRequests: string;
    privacyAccepted: boolean;
  };
  visibility: {
    lang: boolean;
    theme: boolean;
    service: boolean;
  };
  availability: Availability;
  isAvailabilityLoading: boolean;
  availabilityError: string | null;
  setLanguage: (language: Language) => void;
  setTheme: (theme: Theme) => void;
  setVisibility: (visibility: Partial<BookingState['visibility']>) => void;
  setSelectedDate: (date: Date | undefined) => void;
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  updateFormData: (data: Partial<BookingState['formData']>) => void;
  fetchAvailability: (selectedServices: SelectedService[], signal: AbortSignal) => Promise<void>;
  resetBooking: () => void;
  fetchConfig: () => Promise<void>;
  fetchServices: () => Promise<void>;
  setAvailability: (availability: Availability) => void;
  setAvailabilityLoading: (isLoading: boolean) => void;
  setAvailabilityError: (error: string | null) => void;
}


export const useBookingStore = create<BookingState>()(
  persist(
    (set) => ({
      language: 'es',
      theme: 'light',
      selectedDate: undefined,
      currentStep: 1,
      formData: {
        fullName: '',
        email: '',
        selectedServices: [],
        serviceGroup: null,
        lockedGroupId: null,
        guests: 1,
        specialRequests: '',
        privacyAccepted: false,
      },
      visibility: {
        lang: true,
        theme: true,
        service: true,
      },
      availability: { available: [] },
      isAvailabilityLoading: false,
      availabilityError: null,
      config: null,
      isConfigLoading: false,
      services: [],
      isServicesLoading: false,
      setLanguage: (language) => set({ language }),
      setTheme: (theme) => set({ theme }),
      setVisibility: (visibility) => set((state) => ({ 
        visibility: { ...state.visibility, ...visibility } 
      })),
      setSelectedDate: (date) => set({ selectedDate: date }),
      setStep: (step) => set({ currentStep: step }),
      nextStep: () => set((state) => ({ currentStep: state.currentStep + 1 })),
      prevStep: () => set((state) => ({ currentStep: Math.max(1, state.currentStep - 1) })),
      updateFormData: (data) => set((state) => ({ 
        formData: { ...state.formData, ...data } 
      })),
      fetchAvailability: async (selectedServices: SelectedService[], signal: AbortSignal) => {
        set({ isAvailabilityLoading: true, availabilityError: null });
        try {
          const availability = await fetchAvailability(
            selectedServices.map(s => s.serviceId),
            signal
          );
          set({ availability, isAvailabilityLoading: false });
        } catch (error: any) {
          if (error.name !== 'CanceledError') {
            set({ availabilityError: 'Failed to fetch availability', isAvailabilityLoading: false });
          }
        }
      },
      setAvailability: (availability) => set({ availability }),
      setAvailabilityLoading: (isAvailabilityLoading) => set({ isAvailabilityLoading }),
      setAvailabilityError: (availabilityError) => set({ availabilityError }),
      resetBooking: () => set({
        selectedDate: undefined,
        currentStep: 1,
        formData: {
          fullName: '',
          email: '',
          selectedServices: [],
          serviceGroup: null,
          lockedGroupId: null,
          guests: 1,
          specialRequests: '',
          privacyAccepted: false,
        },
        visibility: {
          lang: true,
          theme: true,
          service: true,
        },
        availability: { available: [], limited: [], booked: [] },
      }),


      fetchConfig: async () => {
        set({ isConfigLoading: true });
        try {
          const config = await fetchAppConfig();
          set({ config, isConfigLoading: false });
        } catch (error) {
          console.error('Error fetching config:', error);
          set({ isConfigLoading: false });
        }
      },
      fetchServices: async () => {
        set({ isServicesLoading: true });
        try {
          const services = await fetchAppServices();
          set({ services, isServicesLoading: false });
        } catch (error) {
          console.error('Error fetching services:', error);
          set({ isServicesLoading: false });
        }
      },
    }),
    {
      name: 'booking-storage',
      partialize: (state) => {
        const { visibility, config, isConfigLoading, services, isServicesLoading, ...rest } = state;
        return rest;
      },
      onRehydrateStorage: () => (state) => {
        if (!state) return;
        
        // --- Legacy State Migration ---
        const anyState = state as any;
        if (anyState.formData && !anyState.formData.selectedServices) {
          anyState.formData.selectedServices = [];
          if (anyState.formData.serviceId && anyState.formData.serviceTypeId) {
            anyState.formData.selectedServices.push({
              serviceId: anyState.formData.serviceId,
              serviceTypeId: anyState.formData.serviceTypeId
            });
          }
          // Clean up legacy fields
          delete anyState.formData.serviceId;
          delete anyState.formData.serviceTypeId;
        }
        // ------------------------------

        // Revive selectedDate
        if (state.selectedDate && typeof state.selectedDate === 'string') {
          state.selectedDate = new Date(state.selectedDate);
        }
        
        // Revive availability dates
        if (state.availability) {
          if (Array.isArray(state.availability.limited)) {
            state.availability.limited = state.availability.limited.map(d => 
              typeof d === 'string' ? new Date(d) : d
            );
          }
          if (Array.isArray(state.availability.booked)) {
            state.availability.booked = state.availability.booked.map(d => 
              typeof d === 'string' ? new Date(d) : d
            );
          }
        }
      },
    }
  )
);
