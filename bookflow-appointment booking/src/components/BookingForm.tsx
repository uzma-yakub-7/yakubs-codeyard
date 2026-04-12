import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

export interface ContactInfo {
  name: string;
  email: string;
  phone: string;
  notes: string;
}

interface BookingFormProps {
  contact: ContactInfo;
  onChange: (contact: ContactInfo) => void;
}

const BookingForm = ({ contact, onChange }: BookingFormProps) => {
  const update = (field: keyof ContactInfo, value: string) =>
    onChange({ ...contact, [field]: value });

  return (
    <div className="space-y-5">
      <div>
        <Label htmlFor="name" className="text-foreground">Full Name *</Label>
        <Input
          id="name"
          placeholder="John Doe"
          value={contact.name}
          onChange={(e) => update("name", e.target.value)}
          className="mt-1.5 bg-card border-border focus:border-primary"
        />
      </div>
      <div>
        <Label htmlFor="email" className="text-foreground">Email *</Label>
        <Input
          id="email"
          type="email"
          placeholder="john@example.com"
          value={contact.email}
          onChange={(e) => update("email", e.target.value)}
          className="mt-1.5 bg-card border-border focus:border-primary"
        />
      </div>
      <div>
        <Label htmlFor="phone" className="text-foreground">Phone</Label>
        <Input
          id="phone"
          type="tel"
          placeholder="+1 (555) 123-4567"
          value={contact.phone}
          onChange={(e) => update("phone", e.target.value)}
          className="mt-1.5 bg-card border-border focus:border-primary"
        />
      </div>
      <div>
        <Label htmlFor="notes" className="text-foreground">Notes</Label>
        <Textarea
          id="notes"
          placeholder="Any special requests or notes..."
          value={contact.notes}
          onChange={(e) => update("notes", e.target.value)}
          className="mt-1.5 bg-card border-border focus:border-primary resize-none"
          rows={3}
        />
      </div>
    </div>
  );
};

export default BookingForm;
