import type { Service } from "@/components/ServiceCard";

export const services: Service[] = [
  {
    id: "consultation",
    name: "Initial Consultation",
    description: "First-time consultation to understand your needs and goals.",
    duration: 30,
    price: 50,
    icon: "💬",
  },
  {
    id: "standard",
    name: "Standard Session",
    description: "Regular session with personalized attention and follow-up.",
    duration: 60,
    price: 100,
    icon: "⚡",
  },
  {
    id: "premium",
    name: "Premium Package",
    description: "Extended session with comprehensive analysis and action plan.",
    duration: 90,
    price: 175,
    icon: "👑",
  },
  {
    id: "followup",
    name: "Quick Follow-Up",
    description: "Brief check-in to review progress and adjust plan.",
    duration: 15,
    price: 30,
    icon: "🔄",
  },
];
