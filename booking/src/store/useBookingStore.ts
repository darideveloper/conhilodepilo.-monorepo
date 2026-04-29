import { create } from 'zustand';
import { persist, type StateStorage, createJSONStorage } from 'zustand/middleware';
import { fetchAvailability, fetchSlots } from '../lib/api/availability';
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
  privacy_policy_url: string;
  booking_cooldown_minutes: number;
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
  selectedTime: string | undefined;
  currentStep: number;
  config: AppConfig | null;
  isConfigLoading: boolean;
  services: ServiceCategory[];
  isServicesLoading: boolean;
  formData: {
    fullName: string;
    email: string;
    phone: string;
    selectedServices: SelectedService[];
    serviceGroup: string | null;
    lockedGroupId: string | null;
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
  availableSlots: string[];
  isSlotsLoading: boolean;
  setLanguage: (language: Language) => void;
  setTheme: (theme: Theme) => void;
  setVisibility: (visibility: Partial<BookingState['visibility']>) => void;
  setSelectedDate: (date: Date | undefined) => void;
  setSelectedTime: (time: string | undefined) => void;
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  updateFormData: (data: Partial<BookingState['formData']>) => void;
  fetchAvailability: (selectedServices: SelectedService[], signal: AbortSignal) => Promise<void>;
  fetchSlots: (selectedServices: SelectedService[], date: string, signal?: AbortSignal) => Promise<void>;
  resetBooking: () => void;
  fetchConfig: () => Promise<void>;
  fetchServices: () => Promise<void>;
  setAvailability: (availability: Availability) => void;
  setAvailabilityLoading: (isLoading: boolean) => void;
  setAvailabilityError: (error: string | null) => void;
}

const hybridStorage: StateStorage = {
  getItem: (name) => {
    const localStr = localStorage.getItem(`${name}-local`);
    const sessionStr = sessionStorage.getItem(`${name}-session`);
    
    if (!localStr && !sessionStr) return null;

    const localParsed = localStr ? JSON.parse(localStr) : { state: {} };
    const sessionParsed = sessionStr ? JSON.parse(sessionStr) : { state: {} };
    
    const mergedState = {
      ...localParsed.state,
      ...sessionParsed.state,
      formData: {
        ...(localParsed.state?.formData || {}),
        ...(sessionParsed.state?.formData || {}),
      }
    };
    
    return JSON.stringify({
      state: mergedState,
      version: sessionParsed.version ?? localParsed.version
    });
  },
  setItem: (name, value) => {
    const parsed = JSON.parse(value);
    const { state, version } = parsed;
    
    const localPart = {
      state: {
        language: state.language,
        theme: state.theme,
        formData: {
          fullName: state.formData.fullName,
          email: state.formData.email,
          phone: state.formData.phone,
        }
      },
      version
    };
    
    const sessionPart = { 
      state: {
        ...state,
      },
      version
    };
    
    // Remove local fields from sessionPart to avoid duplication
    if (sessionPart.state) {
      delete (sessionPart.state as any).language;
      delete (sessionPart.state as any).theme;
      if (sessionPart.state.formData) {
        sessionPart.state.formData = { ...state.formData };
        delete (sessionPart.state.formData as any).fullName;
        delete (sessionPart.state.formData as any).email;
        delete (sessionPart.state.formData as any).phone;
      }
    }
    
    localStorage.setItem(`${name}-local`, JSON.stringify(localPart));
    sessionStorage.setItem(`${name}-session`, JSON.stringify(sessionPart));
  },
  removeItem: (name) => {
    localStorage.removeItem(`${name}-local`);
    sessionStorage.removeItem(`${name}-session`);
  }
};

export const useBookingStore = create<BookingState>()(
  persist<BookingState>(
    (set, get) => ({
      language: 'es',
      theme: 'light',
      selectedDate: undefined,
      selectedTime: undefined,
      currentStep: 1,
      formData: {
        fullName: '',
        email: '',
        phone: '',
        selectedServices: [],
        serviceGroup: null,
        lockedGroupId: null,
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
      availableSlots: [],
      isSlotsLoading: false,
      config: null,
      isConfigLoading: false,
      services: [],
      isServicesLoading: false,
      setLanguage: (language) => set({ language }),
      setTheme: (theme) => set({ theme }),
      setVisibility: (visibility) => set((state) => ({ 
        visibility: { ...state.visibility, ...visibility } 
      })),
      setSelectedDate: (date) => set({ selectedDate: date, selectedTime: undefined }),
      setSelectedTime: (time) => set({ selectedTime: time }),
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
      fetchSlots: async (selectedServices: SelectedService[], date: string, signal?: AbortSignal) => {
        set({ isSlotsLoading: true, availableSlots: [] });
        try {
          const slots = await fetchSlots(
            selectedServices.map(s => s.serviceId),
            date,
            signal
          );
          set({ availableSlots: slots, isSlotsLoading: false });
        } catch (error: any) {
          if (error.name !== 'CanceledError') {
            set({ isSlotsLoading: false });
          }
        }
      },
      setAvailability: (availability) => set({ availability }),
      setAvailabilityLoading: (isAvailabilityLoading) => set({ isAvailabilityLoading }),
      setAvailabilityError: (availabilityError) => set({ availabilityError }),
      resetBooking: () => set((state) => ({
        selectedDate: undefined,
        selectedTime: undefined,
        currentStep: 1,
        formData: {
          ...state.formData,
          selectedServices: [],
          serviceGroup: null,
          lockedGroupId: null,
          specialRequests: '',
          privacyAccepted: false,
        },
        visibility: {
          lang: true,
          theme: true,
          service: true,
        },
        availability: { available: [], limited: [], booked: [] },
        availableSlots: [],
      })),


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
      name: 'booking-hybrid-storage',
      storage: createJSONStorage(() => hybridStorage),
      partialize: (state) => {
        const { 
          visibility, 
          config, 
          isConfigLoading, 
          services, 
          isServicesLoading,
          isAvailabilityLoading,
          isSlotsLoading,
          availabilityError,
          ...rest 
        } = state;
        return rest as BookingState;
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

        // Revive selectedDate (ensure local day integrity)
        if (state.selectedDate && typeof state.selectedDate === 'string') {
          const d = new Date(state.selectedDate);
          state.selectedDate = new Date(d.getFullYear(), d.getMonth(), d.getDate());
        }
        
        // Revive availability dates (ensure local day integrity)
        if (state.availability) {
          const reviveDate = (d: any) => {
            if (typeof d !== 'string') return d;
            const date = new Date(d);
            return new Date(date.getFullYear(), date.getMonth(), date.getDate());
          };

          if (Array.isArray(state.availability.available)) {
            state.availability.available = state.availability.available.map(reviveDate);
          }
          if (Array.isArray(state.availability.limited)) {
            state.availability.limited = state.availability.limited.map(reviveDate);
          }
          if (Array.isArray(state.availability.booked)) {
            state.availability.booked = state.availability.booked.map(reviveDate);
          }
        }
      },
    }
  )
);
