"use client";

import { useEffect, useState } from "react";
import Scene3D from "./Scene";
import VehicleRevealScene from "./VehicleRevealScene";
import { useFlagshipFor3D } from "@/hooks/useVehicleFor3D";
import type { Category } from "@/lib/types";

const ROTATION: Category[] = ["army", "aviation", "helicopters", "fleet"];
const SLIDE_DURATION_MS = 11_000;

/**
 * Full replacement for the old Hero.tsx gradient-slide banner.
 * Cycles the four vehicle categories, autoplaying each one's cinematic
 * reveal sequence with a real flagship vehicle's stats at the end.
 */
export default function CinematicHero({ visible }: { visible: boolean }) {
  const [index, setIndex] = useState(0);
  const category = ROTATION[index];
  const { data: vehicle } = useFlagshipFor3D(category);

  useEffect(() => {
    if (!visible) return;
    const timer = setInterval(() => setIndex((i) => (i + 1) % ROTATION.length), SLIDE_DURATION_MS);
    return () => clearInterval(timer);
  }, [visible]);

  if (!visible) return null;

  return (
    <div className="relative h-[62vh] min-h-[420px] w-full overflow-hidden border-b border-hairline">
      <Scene3D cameraPosition={[-4, 3, 10]}>
        {vehicle && <VehicleRevealScene key={vehicle.id} vehicle={vehicle} autoplay />}
      </Scene3D>

      <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10 flex flex-col gap-3 p-6 sm:p-10">
        <div className="flex gap-1.5" role="tablist" aria-label="Hero category">
          {ROTATION.map((c, i) => (
            <button
              key={c}
              role="tab"
              aria-selected={i === index}
              onClick={() => setIndex(i)}
              className={`pointer-events-auto h-1 rounded-full transition-all ${
                i === index ? "w-8 bg-brass" : "w-4 bg-parchment/20 hover:bg-parchment/40"
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
