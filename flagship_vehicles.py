"""
flagship_vehicles.py
=====================
Hand-structured sample vehicles, each matching the Vehicle shape in
lib/types.ts at full depth (multi-point penetration charts, full avionics,
several pro-tips). Imported by generate_mock_data.py.

IMPORTANT — read before treating any number here as authoritative:
These are ILLUSTRATIVE values sized to be plausible for each vehicle's
real-world class and era, built to demonstrate the schema's depth as
requested ("generate a highly detailed MOCK JSON schema"). A few figures
(engine thrust class, reverse speed, hull/turret magnitude) are loosely
grounded against public data — e.g. the Leopard-2-family armor values here
are the right order of magnitude versus the actual datamine record for
germ_leopard_2a5.blkx, which lists composite turret-front zones in the
several-hundred-mm-effective range. But none of this should be read as
current in-game War Thunder balance data. Replace with scraper.py's output
for real numbers.
"""

FLAGSHIP_VEHICLES: list[dict] = [
    # ---------------------------------------------------------------- USA --
    {
        "id": "usa_army_m1a2_sep_abrams",
        "name": "M1A2 SEP Abrams",
        "nation": "usa",
        "category": "army",
        "rank": 7,
        "br": {"ab": 10.3, "rb": 10.7, "sb": 10.7},
        "repairCost": {"ab": 2800, "rb": 5200, "sb": 6100},
        "crew": 4,
        "slMultiplier": 1.90,
        "rpMultiplier": 1.85,
        "mobility": {
            "enginePowerHp": 1500,
            "weightTons": 62.5,
            "powerToWeight": 24.0,
            "topSpeedKmh": 67,
            "reverseSpeedKmh": 8,
            "turnTimeSec": 9.8,
            "transmission": "Hydrokinetic (Allison X-1100-3B), 4 fwd / 2 rev",
        },
        "firepower": {
            "reloadBaseSec": 7.2,
            "reloadAcedSec": 6.2,
            "verticalTargetingSpeedDegS": 10.0,
            "horizontalTargetingSpeedDegS": 40.0,
            "ammoTypes": [
                {
                    "name": "M829A2",
                    "type": "APFSDS",
                    "muzzleVelocityMs": 1680,
                    "penetration": [
                        {"rangeM": 10, "angle0": 650, "angle30": 520, "angle60": 280},
                        {"rangeM": 500, "angle0": 620, "angle30": 495, "angle60": 265},
                        {"rangeM": 1000, "angle0": 590, "angle30": 470, "angle60": 250},
                        {"rangeM": 1500, "angle0": 565, "angle30": 450, "angle60": 238},
                        {"rangeM": 2000, "angle0": 540, "angle30": 430, "angle60": 225},
                    ],
                },
                {
                    "name": "M830A1",
                    "type": "HEAT-FS",
                    "muzzleVelocityMs": 1140,
                    "penetration": [
                        {"rangeM": 10, "angle0": 600, "angle30": 480, "angle60": 255},
                        {"rangeM": 2000, "angle0": 600, "angle30": 480, "angle60": 255},
                    ],
                },
            ],
        },
        "armor": {
            "hullFrontMm": 260,
            "hullSideMm": 60,
            "hullRearMm": 30,
            "turretFrontMm": 620,
            "turretSideMm": 140,
            "turretRearMm": 40,
            "era": False,
            "composite": True,
            "moduleNotes": "Bustle-stored main ammo behind blow-out panels; a held frontal turret hit is usually survivable if the blast doors stay shut.",
        },
        "proTips": [
            "The bustle blow-out panels mean frontal ammo hits are often survivable — don't panic-abandon on the first ammo rack ping.",
            "Reverse speed is only 8 km/h; plan your disengagement route before you commit, not after.",
            "Horizontal traverse at 40°/s outpaces most rank VII turrets — use it to out-track opponents in a circling fight.",
            "M830A1 HEAT-FS doesn't lose penetration with range — useful past 1500m where the APFSDS round has started to fall off.",
        ],
        "sourceDetail": "flagship",
    },
    {
        "id": "usa_aviation_f16c_block50",
        "name": "F-16C Fighting Falcon (Block 50)",
        "nation": "usa",
        "category": "aviation",
        "rank": 8,
        "br": {"ab": 12.0, "rb": 12.3, "sb": 12.3},
        "repairCost": {"ab": 3400, "rb": 7200, "sb": 8600},
        "crew": 1,
        "slMultiplier": 2.10,
        "rpMultiplier": 2.00,
        "mobility": {
            "enginePowerHp": 29000,
            "weightTons": 12.3,
            "powerToWeight": 2.36,
            "topSpeedKmh": 2120,
            "climbRateMs": 250,
        },
        "firepower": {
            "reloadBaseSec": 0.06,
            "reloadAcedSec": 0.06,
            "ammoTypes": [
                {
                    "name": "M61A1 Vulcan",
                    "type": "Cannon (20mm)",
                    "muzzleVelocityMs": 1030,
                    "penetration": [
                        {"rangeM": 400, "angle0": 45, "angle30": 35, "angle60": 20},
                    ],
                },
                {
                    "name": "AIM-9M Sidewinder",
                    "type": "IR missile",
                    "muzzleVelocityMs": 850,
                    "penetration": [
                        {"rangeM": 0, "angle0": 0, "angle30": 0, "angle60": 0},
                    ],
                },
            ],
        },
        "avionics": {
            "radarRangeKm": 130,
            "rwr": True,
            "lwr": False,
            "ballisticComputer": True,
        },
        "proTips": [
            "AIM-9M has a wider off-boresight seeker cone than the base -9L — you can take higher-aspect shots than the block number suggests.",
            "Radar range is class-leading here, but don't out-climb your energy state chasing a lock at altitude against a nimbler rank VIII.",
            "The M61A1 has a generous ammo count — use it to finish wounded targets instead of always reaching for a missile.",
            "Corner speed favors sustained turns over a single hard break; bleeding all your energy in one turn hands the fight away.",
        ],
        "sourceDetail": "flagship",
    },
    # -------------------------------------------------------------- Sweden --
    {
        "id": "sweden_army_strv122b_plus",
        "name": "Strv 122B+",
        "nation": "sweden",
        "category": "army",
        "rank": 7,
        "br": {"ab": 10.0, "rb": 10.3, "sb": 10.3},
        "repairCost": {"ab": 2700, "rb": 5000, "sb": 5900},
        "crew": 4,
        "slMultiplier": 1.88,
        "rpMultiplier": 1.82,
        "mobility": {
            "enginePowerHp": 1500,
            "weightTons": 62.0,
            "powerToWeight": 24.2,
            "topSpeedKmh": 70,
            "reverseSpeedKmh": 12,
            "turnTimeSec": 8.5,
            "transmission": "Hydrokinetic (Renk HSWL 354), 4 fwd / 4 rev",
        },
        "firepower": {
            "reloadBaseSec": 6.9,
            "reloadAcedSec": 5.9,
            "verticalTargetingSpeedDegS": 10.0,
            "horizontalTargetingSpeedDegS": 42.0,
            "ammoTypes": [
                {
                    "name": "Slpprj 22",
                    "type": "APFSDS",
                    "muzzleVelocityMs": 1750,
                    "penetration": [
                        {"rangeM": 10, "angle0": 680, "angle30": 545, "angle60": 295},
                        {"rangeM": 500, "angle0": 650, "angle30": 520, "angle60": 280},
                        {"rangeM": 1000, "angle0": 620, "angle30": 495, "angle60": 265},
                        {"rangeM": 2000, "angle0": 570, "angle30": 455, "angle60": 240},
                    ],
                },
                {
                    "name": "Slprjbrsp 90",
                    "type": "HEAT-FS",
                    "muzzleVelocityMs": 1150,
                    "penetration": [
                        {"rangeM": 10, "angle0": 610, "angle30": 490, "angle60": 260},
                        {"rangeM": 2000, "angle0": 610, "angle30": 490, "angle60": 260},
                    ],
                },
            ],
        },
        "armor": {
            "hullFrontMm": 280,
            "hullSideMm": 65,
            "hullRearMm": 30,
            "turretFrontMm": 650,
            "turretSideMm": 150,
            "turretRearMm": 40,
            "era": False,
            "composite": True,
            "moduleNotes": "Leopard 2 Improved hull/turret with additional Swedish applique armor on the turret cheeks and hull nose.",
        },
        "proTips": [
            "The 12 km/h reverse speed is unusually fast for the class — a Leopard-family trait worth using to reposition without exposing your side.",
            "Turret front is genuinely tough here; bait head-on trades against APFSDS-only opponents at your BR when you can.",
            "Same 120mm L/44 platform as the Leopard 2A5/A6 line — ammo and reload figures carry over if you already know that family.",
            "Applique cheek armor is a real but narrow angle of protection — don't assume it covers a wide arc.",
        ],
        "sourceDetail": "flagship",
    },
    {
        "id": "sweden_aviation_jas39c_gripen",
        "name": "JAS 39C Gripen",
        "nation": "sweden",
        "category": "aviation",
        "rank": 8,
        "br": {"ab": 11.7, "rb": 12.0, "sb": 12.0},
        "repairCost": {"ab": 3200, "rb": 6800, "sb": 8100},
        "crew": 1,
        "slMultiplier": 2.05,
        "rpMultiplier": 1.95,
        "mobility": {
            "enginePowerHp": 18100,
            "weightTons": 6.8,
            "powerToWeight": 2.66,
            "topSpeedKmh": 2005,
            "climbRateMs": 255,
        },
        "firepower": {
            "reloadBaseSec": 0.08,
            "reloadAcedSec": 0.08,
            "ammoTypes": [
                {
                    "name": "Mauser BK27",
                    "type": "Cannon (27mm revolver)",
                    "muzzleVelocityMs": 1025,
                    "penetration": [
                        {"rangeM": 400, "angle0": 55, "angle30": 42, "angle60": 24},
                    ],
                },
                {
                    "name": "IRIS-T",
                    "type": "IR missile (high off-boresight)",
                    "muzzleVelocityMs": 950,
                    "penetration": [
                        {"rangeM": 0, "angle0": 0, "angle30": 0, "angle60": 0},
                    ],
                },
            ],
        },
        "avionics": {
            "radarRangeKm": 120,
            "rwr": True,
            "lwr": True,
            "ballisticComputer": True,
        },
        "proTips": [
            "IRIS-T's off-boresight angle is well past what the seeker growl suggests — you can shoot targets outside your nose without a full lead turn.",
            "The airframe is light for its thrust class; use vertical maneuvers rather than trying to out-turn heavier rank VIII opponents flat.",
            "Laser warning receiver gives you a tell most opponents at this BR don't get — trust the warning and break before the missile is visual.",
            "BK27's revolver cannon has a high rate of fire but a modest belt — short bursts stretch it further than one long squeeze.",
        ],
        "sourceDetail": "flagship",
    },
    # -------------------------------------------------- bonus / grid variety --
    {
        "id": "germany_army_leopard_2a7v",
        "name": "Leopard 2A7V",
        "nation": "germany",
        "category": "army",
        "rank": 7,
        "br": {"ab": 10.7, "rb": 11.0, "sb": 11.0},
        "repairCost": {"ab": 2900, "rb": 5400, "sb": 6300},
        "crew": 4,
        "slMultiplier": 1.92,
        "rpMultiplier": 1.88,
        "mobility": {
            "enginePowerHp": 1500,
            "weightTons": 64.5,
            "powerToWeight": 23.3,
            "topSpeedKmh": 68,
            "reverseSpeedKmh": 12,
            "turnTimeSec": 8.7,
            "transmission": "Hydrokinetic (Renk HSWL 354), 4 fwd / 4 rev",
        },
        "firepower": {
            "reloadBaseSec": 6.8,
            "reloadAcedSec": 5.8,
            "verticalTargetingSpeedDegS": 10.0,
            "horizontalTargetingSpeedDegS": 42.0,
            "ammoTypes": [
                {
                    "name": "DM63",
                    "type": "APFSDS",
                    "muzzleVelocityMs": 1750,
                    "penetration": [
                        {"rangeM": 10, "angle0": 680, "angle30": 545, "angle60": 295},
                        {"rangeM": 1000, "angle0": 620, "angle30": 495, "angle60": 265},
                        {"rangeM": 2000, "angle0": 570, "angle30": 455, "angle60": 240},
                    ],
                }
            ],
        },
        "armor": {
            "hullFrontMm": 280,
            "hullSideMm": 65,
            "hullRearMm": 30,
            "turretFrontMm": 660,
            "turretSideMm": 150,
            "turretRearMm": 40,
            "era": False,
            "composite": True,
            "moduleNotes": "Order-of-magnitude consistent with the real datamine record for the 2A5 hull/turret family (see module docstring).",
        },
        "proTips": [
            "Add-on turret roof armor helps against top-attack munitions but not against a plunging large-caliber HE hit.",
            "The AKE additional side armor set is heavy — expect the slightly worse power-to-weight vs. a bare 2A6.",
        ],
        "sourceDetail": "flagship",
    },
    {
        "id": "ussr_aviation_su27sm",
        "name": "Su-27SM",
        "nation": "ussr",
        "category": "aviation",
        "rank": 8,
        "br": {"ab": 11.3, "rb": 11.7, "sb": 11.7},
        "repairCost": {"ab": 3300, "rb": 7000, "sb": 8300},
        "crew": 1,
        "slMultiplier": 2.0,
        "rpMultiplier": 1.9,
        "mobility": {
            "enginePowerHp": 27600,
            "weightTons": 17.5,
            "powerToWeight": 1.58,
            "topSpeedKmh": 2500,
            "climbRateMs": 260,
        },
        "firepower": {
            "reloadBaseSec": 0.07,
            "reloadAcedSec": 0.07,
            "ammoTypes": [
                {
                    "name": "GSh-30-1",
                    "type": "Cannon (30mm)",
                    "muzzleVelocityMs": 860,
                    "penetration": [{"rangeM": 400, "angle0": 50, "angle30": 38, "angle60": 22}],
                },
                {
                    "name": "R-73",
                    "type": "IR missile (high off-boresight)",
                    "muzzleVelocityMs": 900,
                    "penetration": [{"rangeM": 0, "angle0": 0, "angle30": 0, "angle60": 0}],
                },
            ],
        },
        "avionics": {"radarRangeKm": 100, "rwr": True, "lwr": False, "ballisticComputer": True},
        "proTips": [
            "Airframe is heavier than the base Su-27 but the extra avionics and payload flexibility are usually worth the trade.",
            "R-73 has a very wide seeker cone — use helmet-style off-axis shots rather than lining up a classic tail chase.",
        ],
        "sourceDetail": "flagship",
    },
    {
        "id": "britain_army_challenger_2",
        "name": "Challenger 2",
        "nation": "britain",
        "category": "army",
        "rank": 6,
        "br": {"ab": 9.3, "rb": 9.7, "sb": 9.7},
        "repairCost": {"ab": 2400, "rb": 4500, "sb": 5300},
        "crew": 4,
        "slMultiplier": 1.75,
        "rpMultiplier": 1.7,
        "mobility": {
            "enginePowerHp": 1200,
            "weightTons": 62.5,
            "powerToWeight": 19.2,
            "topSpeedKmh": 59,
            "reverseSpeedKmh": 6,
            "turnTimeSec": 11.5,
            "transmission": "Automatic (David Brown TN54), 6 fwd / 2 rev",
        },
        "firepower": {
            "reloadBaseSec": 8.5,
            "reloadAcedSec": 7.3,
            "verticalTargetingSpeedDegS": 8.0,
            "horizontalTargetingSpeedDegS": 32.0,
            "ammoTypes": [
                {
                    "name": "L23A1",
                    "type": "APFSDS",
                    "muzzleVelocityMs": 1535,
                    "penetration": [
                        {"rangeM": 10, "angle0": 480, "angle30": 385, "angle60": 205},
                        {"rangeM": 2000, "angle0": 420, "angle30": 335, "angle60": 175},
                    ],
                }
            ],
        },
        "armor": {
            "hullFrontMm": 300,
            "hullSideMm": 60,
            "hullRearMm": 25,
            "turretFrontMm": 590,
            "turretSideMm": 130,
            "turretRearMm": 35,
            "era": False,
            "composite": True,
            "moduleNotes": "Chobham-derivative composite turret; famously survivable frontally, at the cost of a slow reverse and long reload.",
        },
        "proTips": [
            "8.5s base reload is slow for the BR — don't take a fight you can't win in one shot against multiple opponents.",
            "Frontal turret armor punches above its BR; hull-down with just the turret exposed is unusually strong here.",
        ],
        "sourceDetail": "flagship",
    },
]
