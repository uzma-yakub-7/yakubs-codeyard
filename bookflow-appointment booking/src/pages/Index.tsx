import { useState } from "react";
import { format } from "date-fns";
import { CalendarIcon, ArrowLeft, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import ServiceCard, { type Service } from "@/components/ServiceCard";
import TimeSlotPicker from "@/components/TimeSlotPicker";
import BookingForm, { type ContactInfo } from "@/components/BookingForm";
import BookingConfirmation from "@/components/BookingConfirmation";
import StepIndicator from "@/components/StepIndicator";
import { services } from "@/data/services";
import { toast } from "sonner";

const STEPS = ["Service", "Date & Time", "Details", "Confirm"];

const Index = () => {
  const [step, setStep] = useState(0);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>();
  const [selectedTime, setSelectedTime] = useState<string | null>(null);
  const [contact, setContact] = useState<ContactInfo>({
    name: "",
    email: "",
    phone: "",
    notes: "",
  });
  const [confirmed, setConfirmed] = useState(false);

  const canProceed = () => {
    switch (step) {
      case 0:
        return !!selectedService;
      case 1:
        return !!selectedDate && !!selectedTime;
      case 2:
        return contact.name.trim() !== "" && contact.email.trim() !== "";
      default:
        return true;
    }
  };

  const handleNext = () => {
    if (step === 3) {
      setConfirmed(true);
      toast.success("Booking confirmed!");
      return;
    }
    setStep((s) => s + 1);
  };

  const handleBack = () => setStep((s) => s - 1);

  const handleReset = () => {
    setStep(0);
    setSelectedService(null);
    setSelectedDate(undefined);
    setSelectedTime(null);
    setContact({ name: "", email: "", phone: "", notes: "" });
    setConfirmed(false);
  };

  if (confirmed && selectedService && selectedDate && selectedTime) {
    return (
      <div className="min-h-screen bg-background flex flex-col">
        <header className="border-b border-border px-6 py-4">
          <h1 className="font-heading text-xl font-bold text-gradient">BookFlow</h1>
        </header>
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="w-full max-w-lg">
            <BookingConfirmation
              service={selectedService}
              date={selectedDate}
              time={selectedTime}
              contact={contact}
            />
            <div className="mt-8 text-center">
              <Button onClick={handleReset} variant="outline" className="border-border">
                Book Another Appointment
              </Button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b border-border px-6 py-4 flex items-center justify-between">
        <h1 className="font-heading text-xl font-bold text-gradient">BookFlow</h1>
        <span className="text-xs text-muted-foreground hidden sm:block">
          Smart Appointment Scheduling
        </span>
      </header>

      <main className="flex-1 flex flex-col max-w-2xl mx-auto w-full p-6">
        <div className="mb-8">
          <StepIndicator steps={STEPS} currentStep={step} />
        </div>

        <div className="flex-1">
          {/* Step 0: Service */}
          {step === 0 && (
            <div className="space-y-4">
              <div className="mb-6">
                <h2 className="font-heading text-2xl font-bold text-foreground">
                  Choose a Service
                </h2>
                <p className="text-muted-foreground mt-1">
                  Select the type of appointment you'd like to book.
                </p>
              </div>
              {services.map((s) => (
                <ServiceCard
                  key={s.id}
                  service={s}
                  selected={selectedService?.id === s.id}
                  onSelect={setSelectedService}
                />
              ))}
            </div>
          )}

          {/* Step 1: Date & Time */}
          {step === 1 && (
            <div className="space-y-6">
              <div className="mb-2">
                <h2 className="font-heading text-2xl font-bold text-foreground">
                  Pick a Date & Time
                </h2>
                <p className="text-muted-foreground mt-1">
                  Choose when you'd like your {selectedService?.name?.toLowerCase()}.
                </p>
              </div>

              <div>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal border-border bg-card",
                        !selectedDate && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {selectedDate
                        ? format(selectedDate, "EEEE, MMMM d, yyyy")
                        : "Select a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0 bg-card border-border" align="start">
                    <Calendar
                      mode="single"
                      selected={selectedDate}
                      onSelect={(d) => {
                        setSelectedDate(d);
                        setSelectedTime(null);
                      }}
                      disabled={(date) =>
                        date < new Date() || date.getDay() === 0
                      }
                      initialFocus
                      className="p-3 pointer-events-auto"
                    />
                  </PopoverContent>
                </Popover>
              </div>

              <TimeSlotPicker
                selectedDate={selectedDate}
                selectedTime={selectedTime}
                onSelectTime={setSelectedTime}
              />
            </div>
          )}

          {/* Step 2: Contact */}
          {step === 2 && (
            <div>
              <div className="mb-6">
                <h2 className="font-heading text-2xl font-bold text-foreground">
                  Your Details
                </h2>
                <p className="text-muted-foreground mt-1">
                  Tell us a bit about yourself so we can prepare for your visit.
                </p>
              </div>
              <BookingForm contact={contact} onChange={setContact} />
            </div>
          )}

          {/* Step 3: Review */}
          {step === 3 && selectedService && selectedDate && selectedTime && (
            <div>
              <div className="mb-6">
                <h2 className="font-heading text-2xl font-bold text-foreground">
                  Review & Confirm
                </h2>
                <p className="text-muted-foreground mt-1">
                  Double-check your booking details before confirming.
                </p>
              </div>
              <div className="bg-card border border-border rounded-xl p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{selectedService.icon}</span>
                  <div>
                    <p className="font-semibold text-foreground">{selectedService.name}</p>
                    <p className="text-sm text-primary">${selectedService.price} · {selectedService.duration} min</p>
                  </div>
                </div>
                <div className="h-px bg-border" />
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Date</p>
                    <p className="text-foreground font-medium">
                      {format(selectedDate, "MMM d, yyyy")}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Time</p>
                    <p className="text-foreground font-medium">{selectedTime}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Name</p>
                    <p className="text-foreground font-medium">{contact.name}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Email</p>
                    <p className="text-foreground font-medium">{contact.email}</p>
                  </div>
                </div>
                {contact.notes && (
                  <>
                    <div className="h-px bg-border" />
                    <div className="text-sm">
                      <p className="text-muted-foreground">Notes</p>
                      <p className="text-foreground mt-1">{contact.notes}</p>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center mt-8 pt-6 border-t border-border">
          <Button
            variant="ghost"
            onClick={handleBack}
            disabled={step === 0}
            className="text-muted-foreground"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <Button
            onClick={handleNext}
            disabled={!canProceed()}
            className="bg-primary text-primary-foreground hover:bg-primary/90 px-6"
          >
            {step === 3 ? "Confirm Booking" : "Continue"}
            {step < 3 && <ArrowRight className="w-4 h-4 ml-2" />}
          </Button>
        </div>
      </main>
    </div>
  );
};

export default Index;
