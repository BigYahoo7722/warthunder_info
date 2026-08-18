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
  enginePowerHp?: number; // not yet extracted by the real scraper — see daily_scraper.py's "NOT CONFIRMED" notes
  weightTons: number;
  powerToWeight?: number; // hp/ton, derived — only meaningful when enginePowerHp is present
  topSpeedKmh?: number; // not yet extracted by the real scraper, same reason as enginePowerHp
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
  repairCost?: RepairCost; // not yet extracted by the real scraper — see daily_scraper.py's "NOT CONFIRMED" notes
  crew: number;
  slMultiplier?: number; // same
  rpMultiplier?: number; // same
  mobility?: MobilityStats;
  firepower?: FirepowerStats;
  armor?: ArmorStats;
  avionics?: AvionicsStats;
  proTips: string[];
  isPremium?: boolean;
  isEvent?: boolean;
  isRare?: boolean;
  isSquadron?: boolean;
  sourceDetail: "flagship" | "generated" | "scraped"; // see README — flagship = fully
  // hand-verified structure for the schema demo; generated = lightweight
  // placeholder from scripts/generate_mock_data.py; scraped = real data
  // from daily_scraper.py, currently a genuine subset of this schema (see
  // that script's "NOT CONFIRMED" section for exactly what's missing).

  // 👇 این خط جادویی اضافه شد 👇
  // اجازه ورود هر کلید (Key) ناشناس با هر مقداری (Value) از سمت دیتابیس/ربات
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
