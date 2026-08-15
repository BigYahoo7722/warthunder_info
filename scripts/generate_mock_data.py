#!/usr/bin/env python3
"""
generate_mock_data.py
======================
Builds data/vehicles.json, the demo "database" the Next.js API route reads.

This is NOT the scraper (see scraper.py for that). It exists so the frontend
can be built, reviewed, and stress-tested without waiting on a live scrape.
Two tiers of record, both matching the Vehicle shape in lib/types.ts:

  1. FLAGSHIP vehicles: hand-authored, all sections populated at full depth
     (multi-point penetration charts, full avionics, etc.) so the modal's
     every collapsible section has something real to render. These are the
     ones also written out to data/schema-example.json.

  2. GENERATED vehicles: procedurally created, lightweight (1-2 penetration
     points instead of a full chart, 1-2 pro-tips) so generation is fast and
     the JSON stays a reasonable size at ~2,600 records. Their names are
     deliberately systematic (e.g. "USA-ARM-4102") rather than invented real
     vehicle names — this is placeholder bulk data to prove the virtualized
     grid holds up at roster scale, not a claim about real War Thunder
     vehicles. Replace this tier with scraper.py's output when you have it.

Run: python3 scripts/generate_mock_data.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

random.seed(2600)  # reproducible output between runs

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "vehicles.json"

NATIONS = ["usa", "germany", "ussr", "britain", "japan", "china", "italy", "france", "sweden", "israel"]
CATEGORIES = ["aviation", "army", "fleet", "helicopters"]

NATION_CODE = {
    "usa": "USA", "germany": "GER", "ussr": "USSR", "britain": "GBR", "japan": "JPN",
    "china": "CHN", "italy": "ITA", "france": "FRA", "sweden": "SWE", "israel": "ISR",
}
CATEGORY_CODE = {"aviation": "AVN", "army": "ARM", "fleet": "FLT", "helicopters": "HEL"}

# Roughly how many generated (non-flagship) vehicles to place in each
# nation/category cell. Real trees are lopsided — e.g. Sweden's fleet tree is
# thin, Germany's army tree is deep — so weight the ranges instead of using a
# flat count everywhere; it reads more like a real roster in the demo.
THIN_TREES = {("sweden", "fleet"), ("israel", "fleet"), ("israel", "helicopters"), ("italy", "helicopters")}


def vehicle_count_for(nation: str, category: str) -> int:
    if (nation, category) in THIN_TREES:
        return random.randint(6, 14)
    return random.randint(55, 85)


PRO_TIP_POOL = [
    "Uptiered? Use terrain and uptime, not head-on trades, to close the BR gap.",
    "Check the reload-aced figure before crewing this — it's the real number you'll see in a match.",
    "The penetration chart is at 0/30/60°; angling your own armor works both ways against this round.",
    "Watch the repair cost at this BR — a string of deaths here erodes SL faster than it looks.",
    "This vehicle's turn time rewards close-range brawling more than long sightlines.",
    "Pair the base reload with a loader crew skill investment before judging DPM.",
    "Historically this saw service in a support role — the in-game loadout reflects that.",
    "Ammo rack placement matters more than raw armor thickness here; know where it's stowed.",
]


def pick_tips(n: int) -> list[str]:
    return random.sample(PRO_TIP_POOL, k=n)


def gen_mobility(category: str) -> dict:
    if category in ("army", "fleet"):
        weight = round(random.uniform(4, 65), 1)
        hp = random.randint(180, 1500)
        return {
            "enginePowerHp": hp,
            "weightTons": weight,
            "powerToWeight": round(hp / weight, 1),
            "topSpeedKmh": random.randint(28, 70) if category == "army" else random.randint(18, 55),
            "reverseSpeedKmh": random.randint(4, 15),
            "turnTimeSec": round(random.uniform(6, 16), 1),
            "transmission": random.choice(["Manual, 5 fwd / 1 rev", "Hydromechanical, 6 fwd / 2 rev", "Manual, 4 fwd / 1 rev"]),
        }
    # aviation / helicopters
    weight = round(random.uniform(2.5, 25), 1)
    hp = random.randint(900, 32000)
    return {
        "enginePowerHp": hp,
        "weightTons": weight,
        "powerToWeight": round(hp / weight, 1),
        "topSpeedKmh": random.randint(260, 2100) if category == "aviation" else random.randint(180, 320),
        "climbRateMs": round(random.uniform(8, 280), 1),
    }


def gen_firepower(category: str) -> dict:
    if category in ("army", "fleet"):
        base = round(random.uniform(4.5, 14), 1)
        return {
            "reloadBaseSec": base,
            "reloadAcedSec": round(base * 0.86, 1),
            "verticalTargetingSpeedDegS": round(random.uniform(4, 20), 1),
            "horizontalTargetingSpeedDegS": round(random.uniform(8, 42), 1),
            "ammoTypes": [
                {
                    "name": random.choice(["APCBC", "APFSDS", "HEAT-FS", "AP", "SAPHE"]),
                    "type": random.choice(["APCBC", "APFSDS", "HEAT-FS", "AP", "SAPHE"]),
                    "muzzleVelocityMs": random.randint(750, 1800),
                    "penetration": [
                        {
                            "rangeM": 500,
                            "angle0": random.randint(90, 500),
                            "angle30": random.randint(70, 420),
                            "angle60": random.randint(30, 220),
                        }
                    ],
                }
            ],
        }
    base = round(random.uniform(0.06, 4.0), 2)
    return {
        "reloadBaseSec": base,
        "reloadAcedSec": round(base * 0.9, 2),
        "ammoTypes": [
            {
                "name": random.choice(["AP-I", "HEF-I", "M61 20mm", "AIM-9 class IR"]),
                "type": random.choice(["Cannon", "MG", "IR missile"]),
                "muzzleVelocityMs": random.randint(700, 1050),
                "penetration": [{"rangeM": 400, "angle0": random.randint(15, 60), "angle30": random.randint(10, 45), "angle60": random.randint(5, 25)}],
            }
        ],
    }


def gen_armor() -> dict:
    return {
        "hullFrontMm": random.randint(10, 220),
        "hullSideMm": random.randint(8, 80),
        "hullRearMm": random.randint(6, 45),
        "turretFrontMm": random.randint(20, 300),
        "turretSideMm": random.randint(15, 90),
        "turretRearMm": random.randint(10, 60),
        "era": random.random() < 0.35,
        "composite": random.random() < 0.5,
    }


def gen_avionics() -> dict:
    has_radar = random.random() < 0.6
    return {
        "radarRangeKm": random.randint(15, 140) if has_radar else None,
        "thermalGen": random.choice([1, 2, 3]) if random.random() < 0.7 else None,
        "rwr": random.random() < 0.55,
        "lwr": random.random() < 0.25,
        "ballisticComputer": random.random() < 0.7,
    }


def gen_vehicle(nation: str, category: str, seq: int) -> dict:
    rank = random.randint(1, 8)
    br = round(random.uniform(1.0, 11.7), 1)
    vid = f"{nation}_{category}_gen_{seq:04d}"
    name = f"{NATION_CODE[nation]}-{CATEGORY_CODE[category]}-{rank}{seq:03d}"

    v = {
        "id": vid,
        "name": name,
        "nation": nation,
        "category": category,
        "rank": rank,
        "br": {"ab": round(br * 0.9, 1), "rb": br, "sb": round(br * 1.02, 1)},
        "repairCost": {
            "ab": random.randint(400, 4000),
            "rb": random.randint(800, 9000),
            "sb": random.randint(1200, 12000),
        },
        "crew": random.randint(1, 6),
        "slMultiplier": round(random.uniform(0.9, 2.4), 2),
        "rpMultiplier": round(random.uniform(0.9, 2.4), 2),
        "mobility": gen_mobility(category),
        "firepower": gen_firepower(category),
        "proTips": pick_tips(random.choice([1, 2])),
        "isPremium": random.random() < 0.12,
        "isEvent": random.random() < 0.05,
        "isRare": random.random() < 0.04,
        "sourceDetail": "generated",
    }
    if category in ("army", "fleet"):
        v["armor"] = gen_armor()
    if category in ("aviation", "helicopters"):
        v["avionics"] = gen_avionics()
    return v


def build_generated() -> list[dict]:
    out = []
    for nation in NATIONS:
        for category in CATEGORIES:
            count = vehicle_count_for(nation, category)
            for seq in range(1, count + 1):
                out.append(gen_vehicle(nation, category, seq))
    return out


def main() -> None:
    from flagship_vehicles import FLAGSHIP_VEHICLES  # local import, see that file

    generated = build_generated()
    all_vehicles = FLAGSHIP_VEHICLES + generated
    random.shuffle(all_vehicles)  # don't cluster flagships at the front of every list

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w") as f:
        json.dump(all_vehicles, f, separators=(",", ":"))

    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"Wrote {len(all_vehicles)} vehicles ({len(FLAGSHIP_VEHICLES)} flagship, "
          f"{len(generated)} generated) — {size_kb:.0f} KB → {OUT_PATH}")


if __name__ == "__main__":
    main()
