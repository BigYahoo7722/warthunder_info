export type Nation =
  | "usa"
  | "germany"
  | "ussr"
  | "britain"
  | "japan"
  | "china"
  | "italy"
  | "france"
  | "sweden"
  | "israel";

export type Category = "aviation" | "army" | "fleet" | "helicopters";

export interface BattleRating {
  ab: number;
  rb: number;
  sb: number;
}

export interface RepairCost {
  ab: number;
  rb: number;
  sb: number;
}

export interface MobilityStats {
  enginePowerHp?: number;
  weightTons: number;
  powerToWeight?: number;
  topSpeedKmh?: number;
  reverseSpeedKmh?: number;
  turnTimeSec?: number;
  climbRateMs?: number;
  transmission?: string;
}

export interface PenetrationPoint {
  rangeM: number;
  angle0: number;
  angle30: number;
  angle60: number;
}

export interface AmmoRound {
  name: string;
  type: string;
  muzzleVelocityMs: number;
  penetration: PenetrationPoint[];
}

export interface FirepowerStats {
  reloadBaseSec: number;
  reloadAcedSec: number;
  verticalTargetingSpeedDegS?: number;
  horizontalTargetingSpeedDegS?: number;
  ammoTypes: AmmoRound[];
}

export interface ArmorStats {
  hullFrontMm: number;
  hullSideMm: number;
  hullRearMm: number;
  turretFrontMm?: number;
  turretSideMm?: number;
  turretRearMm?: number;
  era: boolean;
  composite: boolean;
  moduleNotes?: string;
}

export interface AvionicsStats {
  radarRangeKm?: number;
  thermalGen?: 1 | 2 | 3;
  rwr: boolean;
  lwr: boolean;
  ballisticComputer: boolean;
}

export interface Vehicle {
  id: string;
  name: string;
  nation: Nation;
  category: Category;
  rank: number;
  br: BattleRating;
  repairCost?: RepairCost;
  crew: number;
  slMultiplier?: number;
  rpMultiplier?: number;
  mobility?: MobilityStats;
  firepower?: FirepowerStats;
  armor?: ArmorStats;
  avionics?: AvionicsStats;
  proTips: string[];
  isPremium?: boolean;
  isEvent?: boolean;
  isRare?: boolean;
  isSquadron?: boolean;
  sourceDetail: "flagship" | "generated" | "scraped";

  // پشتیبانی از هرگونه فیلد dynamic و ناشناس بدون ارور تایپ‌اسکریپت
  [key: string]: any;
}

export interface VehiclePage {
  items: Vehicle[];
  nextCursor: number | null;
  total: number;
}

export const NATION_LABELS: Record<Nation, string> = {
  usa: "USA",
  germany: "Germany",
  ussr: "USSR",
  britain: "Britain",
  japan: "Japan",
  china: "China",
  italy: "Italy",
  france: "France",
  sweden: "Sweden",
  israel: "Israel",
};

export const CATEGORY_LABELS: Record<Category, string> = {
  aviation: "Aviation",
  army: "Army",
  fleet: "Fleet",
  helicopters: "Helicopters",
};
