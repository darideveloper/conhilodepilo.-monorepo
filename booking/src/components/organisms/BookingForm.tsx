import React, { useState } from "react"
import { useBookingStore } from "../../store/useBookingStore"
import { useTranslation } from "@/lib/i18n/useTranslation"
import { Button } from "@/components/atoms/ui/button"
import { Input } from "@/components/atoms/ui/input"
import { Label } from "@/components/atoms/ui/label"
import { Textarea } from "@/components/atoms/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/atoms/ui/card"
import { BookingHeader } from "@/components/molecules/BookingHeader"
import { Send, Calendar, MapPin, CheckCircle2, AlertCircle, Phone, User, Mail, Clock } from "lucide-react"

import { Checkbox } from "@/components/atoms/ui/checkbox"
import { submitBooking } from "@/lib/api/endpoints/booking"

export function BookingForm() {
  const { t, language } = useTranslation()
  const formData = useBookingStore((state: any) => state.formData)
  const config = useBookingStore((state: any) => state.config)
  const updateFormData = useBookingStore((state: any) => state.updateFormData)
  const selectedDate = useBookingStore((state: any) => state.selectedDate)
  const selectedTime = useBookingStore((state: any) => state.selectedTime)
  const prevStep = useBookingStore((state: any) => state.prevStep)
  
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const servicesData = useBookingStore((state: any) => state.services)

  const selectedTours = servicesData
    .flatMap((category: any) => category.services)
    .filter((s: any) => formData.selectedServices.some((ss: any) => ss.serviceId === s.id))


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)
    
    if (!selectedDate || !selectedTime) {
        setError(language === 'es' ? 'Falta fecha u hora' : 'Missing date or time')
        setIsSubmitting(false)
        return
    }

    const year = selectedDate.getFullYear();
    const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
    const day = String(selectedDate.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;

    try {
      await submitBooking({
        clientName: formData.fullName,
        clientEmail: formData.email,
        clientPhone: formData.phone,
        service_ids: formData.selectedServices.map((s: any) => parseInt(s.serviceId)),
        date: dateStr,
        startTime: selectedTime,
        specialRequests: formData.specialRequests,
      })
      setIsSubmitted(true)
    } catch (err: any) {
      console.error('Error submitting booking:', err)
      setError(err.message || (language === 'es' ? 'Error al procesar la reserva' : 'Error processing booking'))
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSubmitted) {
    return (
      <Card className="w-full max-w-md shadow-2xl border-none bg-background rounded-3xl overflow-hidden animate-in fade-in zoom-in duration-500">
        <BookingHeader />
        <CardContent className="flex flex-col items-center justify-center py-12 px-8 text-center space-y-6">
          <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mb-2">
            <CheckCircle2 className="w-10 h-10 text-primary" />
          </div>
          <div className="space-y-2">
            <h2 className="text-3xl font-serif font-bold text-foreground">{t.form.successTitle}</h2>
            <p className="text-muted-foreground">{t.form.successMessage}</p>
          </div>
          <div className="w-full p-4 bg-muted rounded-2xl text-left space-y-3 border border-border">
            <div className="flex items-center gap-3 text-sm">
              <div className="w-8 h-8 rounded-lg bg-background flex items-center justify-center border border-border">
                <User className="w-4 h-4 text-primary" />
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold">{t.form.fullName}</p>
                <p className="font-medium">{formData.fullName}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-8 h-8 rounded-lg bg-background flex items-center justify-center border border-border">
                <Calendar className="w-4 h-4 text-primary" />
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold">{t.stripe.date}</p>
                <p className="font-medium">{selectedDate?.toLocaleDateString(language === 'es' ? 'es-ES' : 'en-US')} - {selectedTime}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-8 h-8 rounded-lg bg-background flex items-center justify-center border border-border">
                <MapPin className="w-4 h-4 text-primary" />
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold">{t.calendar.tourLabel}</p>
                <div className="space-y-1">
                  {selectedTours.length > 0 ? (
                    selectedTours.map((tour: any) => (
                      <p key={tour.id} className="font-medium leading-tight text-sm">
                        • {typeof tour.title === 'string' ? tour.title : (tour.title[language] || tour.title.es)}
                      </p>
                    ))
                  ) : (
                    <p className="font-medium">{config?.event_label || t.calendar.tourLabel}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
          <Button 
            variant="outline" 
            className="rounded-xl px-8"
            onClick={() => window.location.reload()}
          >
            {t.form.close}
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-md shadow-2xl border-none bg-background rounded-3xl overflow-hidden relative">
      <BookingHeader 
        showBack={true} 
        onBack={prevStep} 
        showStep={true} 
        stepText={t.form.step3Of3 || "Step 3 of 3"} 
      />

      <CardHeader className="pb-4">
        <CardTitle className="text-2xl font-serif font-bold tracking-tight">{t.form.title}</CardTitle>
        <CardDescription className="text-muted-foreground/80">
          {selectedTours.length > 0
            ? selectedTours.map((t: any) => typeof t.title === 'string' ? t.title : (t.title[language] || t.title.es)).join(', ')
            : t.form.description
          }
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-xl flex items-center gap-3 text-destructive animate-in fade-in slide-in-from-top-1">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <p className="text-xs font-medium">{error}</p>
            </div>
          )}

          <div className="grid gap-4">
            <div className="space-y-2 group">
              <Label htmlFor="fullName" className="text-xs font-bold uppercase tracking-wider text-muted-foreground group-focus-within:text-primary transition-colors">
                {t.form.fullName}
              </Label>
              <div className="relative">
                <Input
                  id="fullName"
                  placeholder={t.form.fullNamePlaceholder}
                  value={formData.fullName}
                  onChange={(e) => updateFormData({ fullName: e.target.value })}
                  className="rounded-xl border-border bg-muted/30 focus:bg-background transition-all h-11 pl-10"
                  required
                />
                <User className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
              </div>
            </div>

            <div className="space-y-2 group">
              <Label htmlFor="email" className="text-xs font-bold uppercase tracking-wider text-muted-foreground group-focus-within:text-primary transition-colors">
                {t.form.email}
              </Label>
              <div className="relative">
                <Input
                  id="email"
                  type="email"
                  placeholder={t.form.emailPlaceholder}
                  value={formData.email}
                  onChange={(e) => updateFormData({ email: e.target.value })}
                  className="rounded-xl border-border bg-muted/30 focus:bg-background transition-all h-11 pl-10"
                  required
                />
                <Mail className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
              </div>
            </div>

            <div className="space-y-2 group">
              <Label htmlFor="phone" className="text-xs font-bold uppercase tracking-wider text-muted-foreground group-focus-within:text-primary transition-colors">
                {(t.form as any).phone}
              </Label>
              <div className="relative">
                <Input
                  id="phone"
                  type="tel"
                  placeholder={(t.form as any).phonePlaceholder}
                  value={formData.phone}
                  onChange={(e) => updateFormData({ phone: e.target.value })}
                  className="rounded-xl border-border bg-muted/30 focus:bg-background transition-all h-11 pl-10"
                  required
                />
                <Phone className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  {t.stripe.date}
                </Label>
                <div className="h-11 rounded-xl bg-muted/50 border border-border flex items-center px-3 gap-2.5 text-sm font-medium text-foreground">
                  <Calendar className="w-4 h-4 text-primary" />
                  {selectedDate?.toLocaleDateString(language === 'es' ? 'es-ES' : 'en-US')}
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Hora
                </Label>
                <div className="h-11 rounded-xl bg-muted/50 border border-border flex items-center px-3 gap-2.5 text-sm font-medium text-foreground">
                  <Clock className="w-4 h-4 text-primary" />
                  {selectedTime}
                </div>
              </div>
            </div>

            <div className="space-y-2 group">
              <Label htmlFor="specialRequests" className="text-xs font-bold uppercase tracking-wider text-muted-foreground group-focus-within:text-primary transition-colors">
                {t.form.specialRequests}
              </Label>
              <Textarea
                id="specialRequests"
                placeholder={t.form.specialRequestsPlaceholder}
                value={formData.specialRequests}
                onChange={(e) => updateFormData({ specialRequests: e.target.value })}
                className="rounded-xl border-border bg-muted/30 focus:bg-background transition-all resize-none min-h-[80px]"
              />
            </div>

            <div className="flex items-center space-x-3 p-4 bg-muted/20 rounded-2xl border border-border/50 transition-colors hover:bg-muted/30">
              <Checkbox 
                id="privacy" 
                checked={formData.privacyAccepted}
                onCheckedChange={(checked) => updateFormData({ privacyAccepted: !!checked })}
                required
              />
              <div className="grid gap-1.5 leading-none">
                <label
                  htmlFor="privacy"
                  className="text-xs font-medium leading-normal text-muted-foreground cursor-pointer"
                >
                  {(() => {
                    const policyText = language === 'es' ? 'política de privacidad' : 'privacy policy';
                    const parts = t.form.privacyPolicy.split(policyText);
                    const privacyUrl = config?.privacy_policy_url || "/privacy";
                    return (
                      <>
                        {parts[0]}
                        <a href={privacyUrl} className="text-primary hover:underline font-bold" target="_blank" rel="noopener noreferrer">
                          {policyText}
                        </a>
                        {parts[1]}
                      </>
                    );
                  })()}
                </label>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 p-3 bg-primary/5 rounded-xl border border-primary/10">
            <AlertCircle className="w-4 h-4 text-primary shrink-0" />
            <p className="text-[10px] text-muted-foreground italic leading-tight">
              {t.form.requiredFields}
            </p>
          </div>

          <Button 
            type="submit" 
            className="w-full py-7 text-lg font-serif rounded-2xl shadow-lg shadow-primary/20 relative overflow-hidden group"
            disabled={isSubmitting || !formData.privacyAccepted}
          >
            {isSubmitting ? (
              <span className="flex items-center gap-2">
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                {t.form.submitting}
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Send className="w-5 h-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                {t.form.submit}
              </span>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
