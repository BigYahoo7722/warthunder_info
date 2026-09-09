"use client";

import { useEffect, useMemo } from "react";
import * as THREE from "three";
import { useGLTF } from "@react-three/drei";
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

// public/models/<folder>/scene.gltf — CC-BY-4.0 Sketchfab downloads, see
// CREDITS.md for the required attribution text for each.
const MODEL_PATH: Record<Category, string> = {
  army: "/models/tank/scene.gltf",
  aviation: "/models/jet/scene.gltf",
  helicopters: "/models/helicopter/scene.gltf",
  fleet: "/models/ship/scene.gltf",
};

export function VehicleModel({
  category,
  nation: _nation, // kept in the prop contract for CinematicHero/VehicleRevealScene callers; real models carry their own livery now instead of a per-nation procedural tint
  refs,
}: {
  category: Category;
  nation: string;
  refs: ModelRefs;
}) {
  switch (category) {
    case "aviation":
      return <JetModel refs={refs} />;
    case "helicopters":
      return <HeliModel refs={refs} />;
    case "fleet":
      return <ShipModel refs={refs} />;
    case "army":
    default:
      return <TankModel refs={refs} />;
  }
}

/**
 * Reparents a light or empty into a node that's part of an already-loaded
 * GLTF scene graph (e.g. a rig bone), so it inherits that node's animated
 * world transform automatically — used for the muzzle flash light, which
 * needs to move with the barrel/turret/rotor mount as it recoils.
 */
function reparent(child: THREE.Object3D | null, parent: THREE.Object3D | null | undefined) {
  if (child && parent && child.parent !== parent) parent.add(child);
}

// ---------------------------------------------------------------------
// Tank — Low Poly T-72, Game Ready (Mr. The Rich, CC-BY-4.0)
// Real rig: Main_01 -> ... -> All_06 -> { Turret_07 -> Barrel_08 ->
// BulletSpawn_09, Wheel.L.1-6, Wheel.R.1-6, ... }. BulletSpawn_09 is a
// literal bullet-spawn bone the original rigger placed at the barrel tip.
// ---------------------------------------------------------------------
function TankModel({ refs }: { refs: ModelRefs }) {
  const { scene } = useGLTF("/models/tank/scene.gltf") as unknown as { scene: THREE.Group };
  const cloned = useMemo(() => scene.clone(true), [scene]);
  const n = useMemo(() => {
    const map: Record<string, THREE.Object3D> = {};
    cloned.traverse((o) => { if (o.name) map[o.name] = o; });
    return map;
  }, [cloned]);

  useEffect(() => {
    refs.hull.current = (n["Main_01"] as THREE.Group) ?? cloned;
    refs.articulated.current = (n["Turret_07"] as THREE.Group) ?? cloned;
    refs.emitter.current = n["BulletSpawn_09"] ?? cloned;
    reparent(refs.muzzleLight.current, refs.emitter.current);

    const wheelNames = [
      "Wheel.L.1_012", "Wheel.L.2_011", "Wheel.L.3_013", "Wheel.L.4_00", "Wheel.L.5_014", "Wheel.L.6_015",
      "Wheel.R.1_017", "Wheel.R.2_016", "Wheel.R.3_018", "Wheel.R.4_019", "Wheel.R.5_020", "Wheel.R.6_021",
    ];
    wheelNames.forEach((name, i) => refs.setAux(n[name] ?? null, i));
  }, [n, cloned, refs]);

  return (
    <>
      <primitive object={cloned} scale={0.9} />
      <pointLight ref={refs.muzzleLight} intensity={0} distance={6} color="#ffb35c" />
    </>
  );
}

// ---------------------------------------------------------------------
// Jet — Modern Jet Fighter Low Poly Game Ready Free (Hdjusj, CC-BY-4.0)
// Single fused mesh, no separate rig — treated as one rigid body. The
// missile emitter is a plain empty we add ourselves at the wingtip,
// since the source model has no dedicated hardpoint node.
// ---------------------------------------------------------------------
function JetModel({ refs }: { refs: ModelRefs }) {
  const { scene } = useGLTF("/models/jet/scene.gltf") as unknown as { scene: THREE.Group };
  const cloned = useMemo(() => scene.clone(true), [scene]);

  useEffect(() => {
    refs.hull.current = cloned;
    refs.articulated.current = cloned; // no separate articulated part on a fused mesh — recoil moves the whole airframe, which reads fine for a missile launch kick
  }, [cloned, refs]);

  return (
    <group>
      <primitive object={cloned} scale={0.8} rotation={[0, Math.PI / 2, 0]} />
      <group
        ref={(el) => {
          if (el) refs.emitter.current = el;
        }}
        position={[0.9, -0.3, 1.6]}
      >
        <pointLight ref={refs.muzzleLight} intensity={0} distance={5} color="#ff8a3d" />
      </group>
    </group>
  );
}

// ---------------------------------------------------------------------
// Helicopter — Rigged Helicopter (nikhilmohan, CC-BY-4.0)
// Real rig: Empty_heli -> { Empty -> baling-baling_2 (main rotor, 2
// mesh parts), Empty_baling_1 -> "baling baling_1" (tail rotor, 2 mesh
// parts), body_helicopter }. Note the tail rotor node's name has a
// literal space in it ("baling baling_1"), copied verbatim from the
// source file — not a typo introduced here.
// ---------------------------------------------------------------------
function HeliModel({ refs }: { refs: ModelRefs }) {
  const { scene } = useGLTF("/models/helicopter/scene.gltf") as unknown as { scene: THREE.Group };
  const cloned = useMemo(() => scene.clone(true), [scene]);
  const n = useMemo(() => {
    const map: Record<string, THREE.Object3D> = {};
    cloned.traverse((o) => { if (o.name) map[o.name] = o; });
    return map;
  }, [cloned]);

  useEffect(() => {
    refs.hull.current = (n["Empty_heli"] as THREE.Group) ?? cloned;
    refs.articulated.current = (n["Empty"] as THREE.Group) ?? cloned; // main rotor mount
    refs.setAux(n["baling-baling_2"] ?? null, 0); // main rotor
    refs.setAux(n["baling baling_1"] ?? null, 1); // tail rotor
  }, [n, cloned, refs]);

  return (
    <group>
      <primitive object={cloned} scale={0.7} />
      <group
        ref={(el) => {
          if (el) refs.emitter.current = el;
          reparent(refs.muzzleLight.current, el);
        }}
        position={[0.7, 0.5, 0.6]}
      >
        <pointLight ref={refs.muzzleLight} intensity={0} distance={5} color="#ffb35c" />
      </group>
    </group>
  );
}

// ---------------------------------------------------------------------
// Ship — Low poly battleship (minehffd, CC-BY-4.0)
// Source file has no semantically-named turret node (just generic
// Cube.NNN / Cylinder.NNN from the FBX->glTF export) so, like the jet,
// this is treated as one rigid hull with a manually-placed bow emitter
// rather than guessing which anonymous cylinder is the main gun.
// ---------------------------------------------------------------------
function ShipModel({ refs }: { refs: ModelRefs }) {
  const { scene } = useGLTF("/models/ship/scene.gltf") as unknown as { scene: THREE.Group };
  const cloned = useMemo(() => scene.clone(true), [scene]);

  useEffect(() => {
    refs.hull.current = cloned;
    refs.articulated.current = cloned;
  }, [cloned, refs]);

  return (
    <group>
      <primitive object={cloned} scale={0.35} />
      <group
        ref={(el) => {
          if (el) refs.emitter.current = el;
        }}
        position={[2.4, 0.8, 0]}
      >
        <pointLight ref={refs.muzzleLight} intensity={0} distance={7} color="#ffb35c" />
      </group>
    </group>
  );
}

useGLTF.preload("/models/tank/scene.gltf");
useGLTF.preload("/models/jet/scene.gltf");
useGLTF.preload("/models/helicopter/scene.gltf");
useGLTF.preload("/models/ship/scene.gltf");
