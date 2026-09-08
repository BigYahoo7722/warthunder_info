"use client";

import * as THREE from "three";
import type { MutableRefObject } from "react";
import type { Category } from "@/lib/types";

/**
 * Every category exposes the SAME ref contract so VehicleRevealScene.tsx
 * can drive any of the four with one animation engine instead of four
 * bespoke ones:
 *   hull        — the whole vehicle body (entry motion, brake dip / bob)
 *   articulated — the part that "aims" (turret / rotor mast / superstructure)
 *   emitter     — the exact point fire comes from (barrel tip / rail / pod)
 *   muzzleLight — flash light parented under emitter
 *   aux[]       — repeating parts (wheels / rotor blades) for spin animation
 */
export interface ModelRefs {
  hull: MutableRefObject<THREE.Group>;
  articulated: MutableRefObject<THREE.Group>;
  emitter: MutableRefObject<THREE.Object3D>;
  muzzleLight: MutableRefObject<THREE.PointLight>;
  setAux: (el: THREE.Object3D | null, i: number) => void;
}

// Livery accents per nation so the placeholder geometry doesn't look
// identical for every vehicle — pulled from the same nation the card/modal
// already show, not invented per-vehicle.
const NATION_TINT: Record<string, string> = {
  usa: "#4a5a45",
  germany: "#4a5940",
  ussr: "#4a4238",
  britain: "#3f4a3a",
  japan: "#48493a",
  china: "#4a4230",
  italy: "#454a3d",
  france: "#3d4a42",
  sweden: "#3a4048",
  israel: "#4a4438",
};

export function VehicleModel({
  category,
  nation,
  refs,
}: {
  category: Category;
  nation: string;
  refs: ModelRefs;
}) {
  const tint = NATION_TINT[nation] ?? "#454a3d";

  switch (category) {
    case "aviation":
      return <JetModel tint={tint} refs={refs} />;
    case "helicopters":
      return <HeliModel tint={tint} refs={refs} />;
    case "fleet":
      return <ShipModel tint={tint} refs={refs} />;
    case "army":
    default:
      return <TankModel tint={tint} refs={refs} />;
  }
}

function TankModel({ tint, refs }: { tint: string; refs: ModelRefs }) {
  return (
    <group ref={refs.hull}>
      <mesh castShadow receiveShadow position={[0, 0.55, 0]}>
        <boxGeometry args={[3.4, 0.7, 1.9]} />
        <meshStandardMaterial color={tint} roughness={0.75} metalness={0.35} />
      </mesh>
      {[-1.3, -0.6, 0.1, 0.8, 1.4].map((x, i) => (
        <group key={i} ref={(el) => refs.setAux(el, i)} position={[x, 0.35, 1.05]}>
          <mesh castShadow>
            <cylinderGeometry args={[0.35, 0.35, 0.25, 16]} />
            <meshStandardMaterial color="#111" roughness={0.9} />
          </mesh>
        </group>
      ))}
      <group ref={refs.articulated} position={[0.1, 1.05, 0]}>
        <mesh castShadow>
          <boxGeometry args={[1.5, 0.55, 1.4]} />
          <meshStandardMaterial color={tint} roughness={0.7} metalness={0.4} />
        </mesh>
        <mesh ref={refs.emitter as any} castShadow position={[1.7, 0.05, 0]}>
          <cylinderGeometry args={[0.09, 0.09, 2.6, 12]} />
          <meshStandardMaterial color="#22261f" roughness={0.5} metalness={0.6} />
          <pointLight ref={refs.muzzleLight} position={[1.3, 0, 0]} intensity={0} distance={6} color="#ffb35c" />
        </mesh>
      </group>
    </group>
  );
}

function JetModel({ tint, refs }: { tint: string; refs: ModelRefs }) {
  return (
    <group ref={refs.hull}>
      <group ref={refs.articulated}>
        {/* fuselage */}
        <mesh castShadow receiveShadow rotation={[0, 0, 0]}>
          <capsuleGeometry args={[0.32, 3.2, 6, 12]} />
          <meshStandardMaterial color={tint} roughness={0.35} metalness={0.75} />
        </mesh>
        {/* wings */}
        <mesh castShadow position={[0, 0, 0]}>
          <boxGeometry args={[0.12, 0.05, 3.4]} />
          <meshStandardMaterial color={tint} roughness={0.4} metalness={0.7} />
        </mesh>
        {/* tailfin */}
        <mesh castShadow position={[-1.5, 0.35, 0]}>
          <boxGeometry args={[0.5, 0.7, 0.08]} />
          <meshStandardMaterial color={tint} roughness={0.4} metalness={0.7} />
        </mesh>
        {/* engine glow (afterburner) */}
        <mesh position={[-1.75, 0, 0]}>
          <circleGeometry args={[0.22, 16]} rotation={[0, Math.PI / 2, 0]} />
          <meshBasicMaterial color="#7fd0ff" toneMapped={false} />
        </mesh>
        {/* wingtip rail — missile emitter */}
        <group ref={refs.emitter as any} position={[0.3, -0.15, 1.6]}>
          <mesh castShadow>
            <boxGeometry args={[0.7, 0.1, 0.1]} />
            <meshStandardMaterial color="#333" metalness={0.8} />
          </mesh>
          <pointLight ref={refs.muzzleLight} intensity={0} distance={5} color="#ff8a3d" />
        </group>
      </group>
    </group>
  );
}

function HeliModel({ tint, refs }: { tint: string; refs: ModelRefs }) {
  return (
    <group ref={refs.hull}>
      {/* cabin + tail boom */}
      <mesh castShadow receiveShadow position={[0, 0.7, 0]}>
        <sphereGeometry args={[0.6, 16, 12]} />
        <meshStandardMaterial color={tint} roughness={0.4} metalness={0.6} />
      </mesh>
      <mesh castShadow position={[-1.6, 0.85, 0]}>
        <cylinderGeometry args={[0.08, 0.16, 2.2, 10]} rotation={[0, 0, Math.PI / 2]} />
        <meshStandardMaterial color={tint} roughness={0.4} metalness={0.6} />
      </mesh>
      {/* main rotor mast (articulated) + blades (aux[0]) */}
      <group ref={refs.articulated} position={[0, 1.35, 0]}>
        <mesh castShadow>
          <cylinderGeometry args={[0.06, 0.06, 0.3, 8]} />
          <meshStandardMaterial color="#222" />
        </mesh>
        <group ref={(el) => refs.setAux(el, 0)}>
          <mesh castShadow position={[0, 0.15, 0]}>
            <boxGeometry args={[4.2, 0.05, 0.18]} />
            <meshStandardMaterial color="#1a1a1a" />
          </mesh>
          <mesh castShadow position={[0, 0.15, 0]} rotation={[0, Math.PI / 2, 0]}>
            <boxGeometry args={[4.2, 0.05, 0.18]} />
            <meshStandardMaterial color="#1a1a1a" />
          </mesh>
        </group>
      </group>
      {/* tail rotor (aux[1]) */}
      <group ref={(el) => refs.setAux(el, 1)} position={[-2.6, 0.9, 0]}>
        <mesh castShadow>
          <boxGeometry args={[0.05, 0.9, 0.1]} />
          <meshStandardMaterial color="#1a1a1a" />
        </mesh>
      </group>
      {/* door gun / rocket pod emitter */}
      <group ref={refs.emitter as any} position={[0.7, 0.5, 0.6]}>
        <mesh castShadow>
          <cylinderGeometry args={[0.08, 0.08, 0.5, 8]} rotation={[Math.PI / 2, 0, 0]} />
          <meshStandardMaterial color="#333" metalness={0.7} />
        </mesh>
        <pointLight ref={refs.muzzleLight} intensity={0} distance={5} color="#ffb35c" />
      </group>
    </group>
  );
}

function ShipModel({ tint, refs }: { tint: string; refs: ModelRefs }) {
  return (
    <group ref={refs.hull}>
      {/* hull */}
      <mesh castShadow receiveShadow position={[0, 0.4, 0]}>
        <boxGeometry args={[5.5, 0.8, 1.3]} />
        <meshStandardMaterial color={tint} roughness={0.6} metalness={0.5} />
      </mesh>
      {/* superstructure */}
      <mesh castShadow position={[-0.6, 1.1, 0]}>
        <boxGeometry args={[1.3, 1.0, 1.0]} />
        <meshStandardMaterial color={tint} roughness={0.6} metalness={0.5} />
      </mesh>
      {/* main turret (articulated) with twin barrels (emitter) */}
      <group ref={refs.articulated} position={[1.6, 0.85, 0]}>
        <mesh castShadow>
          <boxGeometry args={[0.9, 0.45, 0.9]} />
          <meshStandardMaterial color={tint} roughness={0.55} metalness={0.55} />
        </mesh>
        <group ref={refs.emitter as any} position={[1.1, 0, 0.18]}>
          <mesh castShadow>
            <cylinderGeometry args={[0.06, 0.06, 1.8, 10]} rotation={[0, 0, Math.PI / 2]} />
            <meshStandardMaterial color="#22261f" metalness={0.6} />
          </mesh>
          <pointLight ref={refs.muzzleLight} intensity={0} distance={7} color="#ffb35c" />
        </group>
      </group>
    </group>
  );
}
