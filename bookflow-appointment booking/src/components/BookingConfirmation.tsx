import { format } from "date-fns";
import { CheckCircle2, Calendar, Clock, User, Mail } from "lucide-react";
import type { Service } from "./ServiceCard";
import type { ContactInfo } from "./BookingForm";

interface BookingConfirmationProps {
  service: Service;
  date: Date;
  time: string;
  contact: ContactInfo;
}

const BookingConfirmation = ({ service, date, time, contact }: BookingConfirmationProps) => {
  return (
    <div className="text-center space-y-8">
      <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 glow-md">
        <CheckCircle2 className="w-10 h-10 text-primary" />
      </div>

      <div>
        <h2 className="font-heading text-2xl font-bold text-foreground">
          Booking Confirmed!
        </h2>
        <p className="text-muted-foreground mt-2">
          Your appointment has been scheduled successfully.
        </p>
      </div>

      <div className="bg-card border border-border rounded-xl p-6 text-left space-y-4 max-w-sm mx-auto">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{service.icon}</span>
          <div>
            <p className="font-semibold text-foreground">{service.name}</p>
            <p className="text-sm text-primary font-medium">${service.price}</p>
          </div>
        </div>
        <div className="h-px bg-border" />
        <div className="space-y-3 text-sm">
          <div className="flex items-center gap-3 text-muted-foreground">
            <Calendar className="w-4 h-4 text-primary" />
            {format(date, "EEEE, MMMM d, yyyy")}
          </div>
          <div className="flex items-center gap-3 text-muted-foreground">
            <Clock className="w-4 h-4 text-primary" />
            {time} · {service.duration} minutes
          </div>
          <div className="flex items-center gap-3 text-muted-foreground">
            <User className="w-4 h-4 text-primary" />
            {contact.name}
          </div>
          <div className="flex items-center gap-3 text-muted-foreground">
            <Mail className="w-4 h-4 text-primary" />
            {contact.email}
          </div>
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        A confirmation email has been sent to {contact.email}
      </p>
    </div>
  );
};

export default BookingConfirmation;
