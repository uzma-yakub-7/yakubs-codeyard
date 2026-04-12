import { cn } from "@/lib/utils";
import { Clock, DollarSign } from "lucide-react";

export interface Service {
  id: string;
  name: string;
  description: string;
  duration: number;
  price: number;
  icon: string;
}

interface ServiceCardProps {
  service: Service;
  selected: boolean;
  onSelect: (service: Service) => void;
}

const ServiceCard = ({ service, selected, onSelect }: ServiceCardProps) => {
  return (
    <button
      onClick={() => onSelect(service)}
      className={cn(
        "w-full text-left p-5 rounded-xl border transition-all duration-300",
        "hover:glow-sm hover:border-primary/40",
        selected
          ? "border-primary bg-primary/10 glow-sm"
          : "border-border bg-card hover:bg-surface-elevated"
      )}
    >
      <div className="flex items-start gap-4">
        <span className="text-3xl">{service.icon}</span>
        <div className="flex-1 min-w-0">
          <h3 className="font-heading font-semibold text-foreground text-lg">
            {service.name}
          </h3>
          <p className="text-muted-foreground text-sm mt-1">
            {service.description}
          </p>
          <div className="flex items-center gap-4 mt-3 text-sm">
            <span className="flex items-center gap-1.5 text-muted-foreground">
              <Clock className="w-3.5 h-3.5" />
              {service.duration} min
            </span>
            <span className="flex items-center gap-1.5 text-primary font-medium">
              <DollarSign className="w-3.5 h-3.5" />
              {service.price}
            </span>
          </div>
        </div>
      </div>
    </button>
  );
};

export default ServiceCard;
