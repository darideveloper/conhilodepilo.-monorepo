import React, { useState } from 'react';
import { Card, CardContent } from '@/components/atoms/ui/card';
import { Button } from '@/components/atoms/ui/button';
import { Label } from '@/components/atoms/ui/label';
import { Select } from '@/components/atoms/ui/select';
import { BookingHeader } from '@/components/molecules/BookingHeader';
import { useBookingStore } from '../../store/useBookingStore';
import { useTranslation } from '@/lib/i18n/useTranslation';
import { Plus, Trash2, Layers } from 'lucide-react';
import { cn } from "@/lib/utils";


export function BookingServiceSelection() {
  const { t, language } = useTranslation();
  const nextStep = useBookingStore((state: any) => state.nextStep);
  const formData = useBookingStore((state: any) => state.formData);
  const updateFormData = useBookingStore((state: any) => state.updateFormData);
  const config = useBookingStore((state: any) => state.config);
  const servicesData = useBookingStore((state: any) => state.services);

  const filteredServicesData = servicesData.filter((category: any) => {
    if (!formData.lockedGroupId) return true;
    return category.group_id === formData.lockedGroupId;
  });

  const [localServiceTypeId, setLocalServiceTypeId] = useState<string>("");
  const [localServiceId, setLocalServiceId] = useState<string>("");

  const selectedCategory = servicesData.find((cat: any) => cat.id === localServiceTypeId);
  const services = selectedCategory ? selectedCategory.services : [];

  const fetchAvailability = useBookingStore((state: any) => state.fetchAvailability);

  const handleAddService = () => {
    if (!localServiceId || !localServiceTypeId) return;
    
    // Prevent duplicates
    const isAlreadyAdded = formData.selectedServices.some((s: any) => s.serviceId === localServiceId);
    if (isAlreadyAdded) return;

    updateFormData({
      selectedServices: [
        ...formData.selectedServices,
        { serviceTypeId: localServiceTypeId, serviceId: localServiceId }
      ]
    });
    
    // Reset local selection but keep category if desired, or reset both
    setLocalServiceId("");
  };

  const handleRemoveService = (serviceId: string) => {
    updateFormData({
      selectedServices: formData.selectedServices.filter((s: any) => s.serviceId !== serviceId)
    });
  };

  const onContinue = () => {
    const controller = new AbortController();
    fetchAvailability(formData.selectedServices, controller.signal);
    nextStep();
  };

  const getServiceName = (serviceId: string) => {
    const service = servicesData
      .flatMap((cat: any) => cat.services)
      .find((s: any) => s.id === serviceId);
    if (!service) return serviceId;
    return typeof service.title === 'string' ? service.title : (service.title[language] || service.title.es);
  };

  return (
    <Card className="w-full max-w-md shadow-xl border-none bg-background relative overflow-hidden rounded-3xl">
      <BookingHeader 
        showStep={true} 
        stepText={t.form?.step1Of3 || "Step 1 of 3"} 
      />
      <CardContent className="flex flex-col gap-6 pt-4 pb-8 px-6">
        
        {/* Selection Area */}
        <div className="w-full space-y-4 p-4 bg-muted/30 rounded-2xl border border-border/50">
          <div className="grid gap-1.5">
            <Label htmlFor="serviceTypeId" className="text-[10px] uppercase tracking-wider font-bold text-muted-foreground">
              {config?.event_type_label || "Tipo de Servicio"}
            </Label>
            <Select
              id="serviceTypeId"
              name="serviceTypeId"
              value={localServiceTypeId}
              onChange={(e) => {
                setLocalServiceTypeId(e.target.value);
                setLocalServiceId("");
              }}
              className="h-11 text-sm w-full rounded-xl border-border bg-background"
            >
              <option value="" disabled>{t.calendar?.selectTour || "Seleccione una categoría"}</option>
              {filteredServicesData.map((category: any) => (
                <option key={category.id} value={category.id}>
                  {typeof category.name === 'string' ? category.name : (category.name[language] || category.name.es)}
                </option>
              ))}
            </Select>
          </div>

          <div className="grid gap-1.5">
            <Label htmlFor="serviceId" className="text-[10px] uppercase tracking-wider font-bold text-muted-foreground">
              {config?.event_label || t.calendar?.tourLabel || "Servicio"}
            </Label>
            <div className="flex gap-2">
              <Select
                id="serviceId"
                name="serviceId"
                value={localServiceId}
                onChange={(e) => setLocalServiceId(e.target.value)}
                className="h-11 text-sm flex-1 rounded-xl border-border bg-background"
                disabled={!localServiceTypeId}
              >
                <option value="" disabled>{t.calendar?.selectTour || "Seleccione un servicio"}</option>
                {services.map((service: any) => (
                  <option key={service.id} value={service.id}>
                    {typeof service.title === 'string' ? service.title : (service.title[language] || service.title.es)}
                  </option>
                ))}
              </Select>
              <Button 
                size="icon" 
                className="h-11 w-11 shrink-0 rounded-xl"
                disabled={!localServiceId || formData.selectedServices.some((s: any) => s.serviceId === localServiceId)}
                onClick={handleAddService}
              >
                <Plus className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* Stack / Cart Area */}
        <div className="w-full space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-muted-foreground px-1">
            <Layers className="w-3.5 h-3.5" />
            <span>{language === 'es' ? 'Servicios seleccionados' : 'Selected Services'} ({formData.selectedServices.length})</span>
          </div>
          
          <div className={cn(
            "space-y-2 min-h-[60px] flex flex-col justify-center transition-all",
            formData.selectedServices.length === 0 && "items-center border-2 border-dashed border-border rounded-2xl py-4"
          )}>
            {formData.selectedServices.length === 0 ? (
              <p className="text-xs text-muted-foreground italic">
                {language === 'es' ? 'No hay servicios añadidos' : 'No services added yet'}
              </p>
            ) : (
              formData.selectedServices.map((item: any) => (
                <div 
                  key={item.serviceId}
                  className="flex items-center justify-between p-3 bg-primary/5 border border-primary/10 rounded-xl group animate-in slide-in-from-left-2 duration-300"
                >
                  <span className="text-sm font-medium truncate pr-2">
                    {getServiceName(item.serviceId)}
                  </span>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg shrink-0"
                    onClick={() => handleRemoveService(item.serviceId)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="w-full pt-2">
          <Button 
            className="w-full py-6 text-lg font-serif rounded-2xl shadow-lg shadow-primary/10"
            disabled={formData.selectedServices.length === 0}
            onClick={onContinue}
          >
            {t.calendar?.continue || "Continuar"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
