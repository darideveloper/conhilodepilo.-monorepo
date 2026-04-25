import React, { useEffect } from "react"
import { useBookingStore, type Language, type Theme } from "../../store/useBookingStore"
import { BookingCalendar } from "./BookingCalendar"
import { BookingForm } from "./BookingForm"
import { BookingServiceSelection } from "./BookingServiceSelection"


export default function BookingFlow() {
  const currentStep = useBookingStore((state: any) => state.currentStep)
  const updateFormData = useBookingStore((state: any) => state.updateFormData)
  const setLanguage = useBookingStore((state: any) => state.setLanguage)
  const setTheme = useBookingStore((state: any) => state.setTheme)
  const setVisibility = useBookingStore((state: any) => state.setVisibility)
  const fetchConfig = useBookingStore((state: any) => state.fetchConfig)
  const config = useBookingStore((state: any) => state.config)
  const servicesData = useBookingStore((state: any) => state.services)
  const fetchServices = useBookingStore((state: any) => state.fetchServices)

  useEffect(() => {
    // 0. Handle Config (Branding) and Services
    fetchConfig();
    fetchServices();
  }, [fetchConfig, fetchServices]);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    
    // 1. Handle Language
    const langQuery = urlParams.get('lang') as Language | null;
    if (langQuery && (langQuery === 'es' || langQuery === 'en')) {
      setLanguage(langQuery);
      setVisibility({ lang: false });
    }

    // 2. Handle Theme
    const themeQuery = urlParams.get('theme') as Theme | null;
    if (themeQuery && (themeQuery === 'light' || themeQuery === 'dark')) {
      setTheme(themeQuery);
      setVisibility({ theme: false });
    }

    // 3. Handle Service (formerly tour)
    const serviceQuery = urlParams.get('service') || urlParams.get('tour');
    if (serviceQuery) {
      // Find the category for this service to pre-fill Step 1
      const category = servicesData.find((cat: any) => 
        cat.services.some((s: any) => s.id === serviceQuery)
      );

      // Set lockedGroupId if category has a group_id
      if (category && category.group_id) {
        updateFormData({ lockedGroupId: category.group_id });
      }

      const isAlreadyAdded = (useBookingStore.getState() as any).formData.selectedServices.some(
        (s: any) => s.serviceId === serviceQuery
      );

      if (!isAlreadyAdded) {
        const currentServices = (useBookingStore.getState() as any).formData.selectedServices;

        updateFormData({ 
          selectedServices: [
            ...currentServices,
            { 
              serviceId: serviceQuery,
              serviceTypeId: category ? category.id : (null as any)
            }
          ]
        });
      }
      
      if (urlParams.get('service') || urlParams.get('tour')) {
        setVisibility({ service: false });
      }
    }

    // 4. Handle Service Group (Ignored per requirements)
  }, [updateFormData, setLanguage, setTheme, setVisibility, servicesData])

  // Apply brand color
  useEffect(() => {
    if (config?.brand_color) {
      // Basic validation for color string
      const isValidColor = (color: string) => {
        return color.startsWith('#') || color.startsWith('rgb') || color.startsWith('oklch');
      };

      if (isValidColor(config.brand_color)) {
        document.documentElement.style.setProperty('--color-brand-red', config.brand_color);
        document.documentElement.style.setProperty('--primary', config.brand_color);
      }
    }
  }, [config])

  return (
    <div className="w-full h-full mx-auto flex flex-col items-center relative z-10 p-4 bg-muted/30 space-y-4 rounded-3xl border border-border h-full">
      {currentStep === 1 && <BookingServiceSelection />}
      {currentStep === 2 && <BookingCalendar />}
      {currentStep === 3 && <BookingForm />}
    </div>
  )
}

