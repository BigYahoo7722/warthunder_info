// ---------------------------------------------------------------------------
// Canonical vehicle schema.
//
// This is the single source of truth for what a "vehicle record" looks like.
// scripts/scraper.py writes JSON that must match this shape — if you add a
// field here, add it to the Python VEHICLE_FIELDS reference too (see that
// file's module docstring).
// ---------------------------------------------------------------------------

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
  enginePowerHp: number;
  weightTons: number;
  powerToWeight: number; // hp/ton, derived but stored for fast sort/filter
  topSpeedKmh: number;
  reverseSpeedKmh?: number;
  turnTimeSec?: number; // ground vehicles
  climbRateMs?: number; // aircraft / helicopters
  transmission?: string;
}

export interface PenetrationPoint {
  rangeM: number;
  angle0: number; // mm RHAe at 0°
  angle30: number;
  angle60: number;
}

export interface AmmoRound {
  name: string;
  type: string; // APFSDS, HEAT-FS, APCBC, AP, HE-VT, etc.
  muzzleVelocityMs: number;
  penetration: PenetrationPoint[]; // 1 point (summary) to many (full chart)
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
  moduleNotes?: string; // internal module / ammo-rack placement summary
}

export interface AvionicsStats {
  radarRangeKm?: number;
  thermalGen?: 1 | 2 | 3;
  rwr: boolean;
  lwr: boolean;
  ballisticComputer: boolean;
}

export interface Vehicle {
  id: string; // slug, e.g. "usa_f16c_block_50"
  name: string;
  nation: Nation;
  category: Category;
  rank: number; // I–VIII
  br: BattleRating;
  repairCost: RepairCost;
  crew: number;
  slMultiplier: number;
  rpMultiplier: number;
  mobility?: MobilityStats;
  firepower?: FirepowerStats;
  armor?: ArmorStats;
  avionics?: AvionicsStats;
  proTips: string[];
  isPremium?: boolean;
  isEvent?: boolean;
  isRare?: boolean;
  isSquadron?: boolean;
  sourceDetail: "flagship" | "generated"; // see README — flagship = fully
  // hand-verified structure for the schema demo; generated = lightweight
  // placeholder from scripts/generate_mock_data.py, meant to be replaced by
  // the real scraper/datamine pipeline output.
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
