import { cn } from "@/lib/utils";

interface TimeSlotPickerProps {
  selectedTime: string | null;
  onSelectTime: (time: string) => void;
  selectedDate: Date | undefined;
}

const generateTimeSlots = () => {
  const slots: string[] = [];
  for (let h = 9; h <= 17; h++) {
    slots.push(`${h.toString().padStart(2, "0")}:00`);
    if (h < 17) slots.push(`${h.toString().padStart(2, "0")}:30`);
  }
  return slots;
};

const TimeSlotPicker = ({ selectedTime, onSelectTime, selectedDate }: TimeSlotPickerProps) => {
  const slots = generateTimeSlots();

  if (!selectedDate) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        Please select a date first
      </div>
    );
  }

  return (
    <div>
      <h3 className="font-heading font-medium text-foreground mb-3">
        Available Times
      </h3>
      <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
        {slots.map((slot) => {
          // Simulate some slots being unavailable
          const isUnavailable = ["10:30", "14:00", "16:30"].includes(slot);
          return (
            <button
              key={slot}
              disabled={isUnavailable}
              onClick={() => onSelectTime(slot)}
              className={cn(
                "py-2.5 px-3 rounded-lg text-sm font-medium transition-all duration-200",
                "border",
                isUnavailable
                  ? "border-border text-muted-foreground/40 cursor-not-allowed line-through"
                  : selectedTime === slot
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border bg-card hover:border-primary/50 hover:bg-surface-elevated text-foreground"
              )}
            >
              {slot}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default TimeSlotPicker;
