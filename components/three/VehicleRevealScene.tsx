"use client";

import { useRef, useState, useMemo, useCallback, useEffect } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import { Html, Trail } from "@react-three/drei";
import gsap from "gsap";
import * as THREE from "three";
import type { Vehicle } from "@/lib/types";
import { VehicleModel, type ModelRefs } from "./VehicleModel";

type Phase = "idle" | "entry" | "settle" | "fire" | "flight" | "impact" | "reveal";
type FireKind = "shell" | "missile" | "rocket" | "broadside";

interface CategoryProfile {
  entryFrom: THREE.Vector3;
  entryTo: THREE.Vector3;
  entryDuration: number;
  entryEase: string;
  settle: (hull: THREE.Group, articulated: THREE.Group) => gsap.core.Timeline;
  fireKind: FireKind;
  trailColor: string;
  auxSpin: (aux: THREE.Object3D[], playing: boolean) => void;
}

function buildProfile(category: Vehicle["category"]): CategoryProfile {
  switch (category) {
    case "aviation":
      return {
        entryFrom: new THREE.Vector3(-14, 6, -10),
        entryTo: new THREE.Vector3(-1, 2.4, 0),
        entryDuration: 1.6,
        entryEase: "power2.out",
        fireKind: "missile",
        trailColor: "#ff5c3d",
        settle: (hull) => gsap.timeline().to(hull.rotation, { z: 0.12, duration: 0.4, ease: "power1.out" })
          .to(hull.rotation, { z: -0.05, duration: 0.6, ease: "elastic.out(1,0.5)" }),
        auxSpin: () => {},
      };
    case "helicopters":
      return {
        entryFrom: new THREE.Vector3(0, 9, 0),
        entryTo: new THREE.Vector3(0, 2.1, 0),
        entryDuration: 1.8,
        entryEase: "power2.inOut",
        fireKind: "rocket",
        trailColor: "#ffb35c",
        settle: (hull) => gsap.timeline().to(hull.position, { y: "+=0.12", duration: 0.9, ease: "sine.inOut", yoyo: true, repeat: 1 }),
        auxSpin: (aux, playing) => {
          aux.forEach((a) => {
            gsap.killTweensOf(a.rotation);
            if (playing) gsap.to(a.rotation, { y: "+=6.28", duration: 0.18, repeat: -1, ease: "none" });
          });
        },
      };
    case "fleet":
      return {
        entryFrom: new THREE.Vector3(-20, 0, -4),
        entryTo: new THREE.Vector3(0, 0, 0),
        entryDuration: 2.3,
        entryEase: "power3.out",
        fireKind: "broadside",
        trailColor: "#ffe2b0",
        settle: (hull) => gsap.timeline().to(hull.rotation, { z: 0.02, duration: 1.1, ease: "sine.inOut", yoyo: true, repeat: 1 }),
        auxSpin: () => {},
      };
    case "army":
    default:
      return {
        entryFrom: new THREE.Vector3(-22, 0, 0),
        entryTo: new THREE.Vector3(0, 0, 0),
        entryDuration: 2.1,
        entryEase: "power3.out",
        fireKind: "shell",
        trailColor: "#5cc8ff",
        settle: (hull) => gsap.timeline()
          .to(hull.rotation, { z: 0.05, duration: 0.12, ease: "power2.out" })
          .to(hull.position, { y: "-=0.06", duration: 0.12, ease: "power2.out" }, "<")
          .to(hull.rotation, { z: -0.015, duration: 0.35, ease: "elastic.out(1,0.4)" })
          .to(hull.position, { y: "+=0.06", duration: 0.35, ease: "elastic.out(1,0.4)" }, "<"),
        auxSpin: (aux, playing) => {
          if (!playing) return;
          aux.forEach((a) => gsap.to(a.rotation, { x: "-=40", duration: 2.1, ease: "power3.out" }));
        },
      };
  }
}

export default function VehicleRevealScene({
  vehicle,
  autoplay = false,
  onRevealChange,
}: {
  vehicle: Vehicle;
  autoplay?: boolean;
  onRevealChange?: (revealed: boolean) => void;
}) {
  const { camera } = useThree();
  const profile = useMemo(() => buildProfile(vehicle.category), [vehicle.category]);

  const hull = useRef<THREE.Group>(null!);
  const articulated = useRef<THREE.Group>(null!);
  const emitter = useRef<THREE.Object3D>(null!);
  const muzzleLight = useRef<THREE.PointLight>(null!);
  const shellRef = useRef<THREE.Mesh>(null!);
  const auxRefs = useRef<THREE.Object3D[]>([]);

  const setAux = useCallback((el: THREE.Object3D | null, i: number) => {
    if (el) auxRefs.current[i] = el;
  }, []);

  const refs: ModelRefs = { hull, articulated, emitter, muzzleLight, setAux };

  const [phase, setPhase] = useState<Phase>("idle");
  const [revealed, setRevealed] = useState(false);
  const flightT = useRef(0);

  const targetPos = useMemo(() => new THREE.Vector3(6.2, profile.entryTo.y + 1.2, -2), [profile]);
  const emitterWorld = useMemo(() => new THREE.Vector3(), []);
  const camLook = useMemo(() => new THREE.Vector3(), []);
  const camPos = useMemo(() => new THREE.Vector3(), []);

  const play = useCallback(() => {
    if (phase !== "idle") return;
    const tl = gsap.timeline();

    tl.call(() => setPhase("entry"));
    tl.fromTo(hull.current.position, { ...profile.entryFrom }, {
      ...profile.entryTo,
      duration: profile.entryDuration,
      ease: profile.entryEase,
    });
    tl.call(() => profile.auxSpin(auxRefs.current, true), undefined, "<");

    tl.call(() => setPhase("settle"));
    tl.add(profile.settle(hull.current, articulated.current));

    tl.call(() => {
      setPhase("fire");
      profile.auxSpin(auxRefs.current, false);
    });
    // universal recoil: articulated part kicks back along local +x, emitter flashes
    tl.to(articulated.current.position, { x: "+=0.12", duration: 0.06, ease: "power4.out" });
    tl.call(() => { if (muzzleLight.current) muzzleLight.current.intensity = 45; });
    tl.to(articulated.current.position, { x: "-=0.12", duration: 0.45, ease: "power2.out" });
    tl.call(() => gsap.to(muzzleLight.current, { intensity: 0, duration: 0.3, ease: "power2.out" }));

    tl.call(() => setPhase("flight"));
    tl.to(flightT, {
      current: 1,
      duration: 0.8,
      ease: "power1.in",
      onStart: () => {
        emitter.current?.getWorldPosition(emitterWorld);
      },
      onUpdate: () => {
        if (shellRef.current) {
          shellRef.current.visible = true;
          shellRef.current.position.lerpVectors(emitterWorld, targetPos, flightT.current);
        }
      },
    }, "-=0.1");

    tl.call(() => {
      setPhase("impact");
      if (shellRef.current) shellRef.current.visible = false;
    });
    tl.call(() => {
      setPhase("reveal");
      setRevealed(true);
      onRevealChange?.(true);
    }, undefined, "+=0.15");

    return tl;
  }, [phase, profile, targetPos, emitterWorld, onRevealChange]);

  useEffect(() => {
    if (autoplay) {
      const id = requestAnimationFrame(() => play());
      return () => cancelAnimationFrame(id);
    }
  }, [autoplay, play]);

  useFrame((_, delta) => {
    if (phase === "flight" && shellRef.current) {
      camPos.set(shellRef.current.position.x - 3, shellRef.current.position.y + 2.2, shellRef.current.position.z + 5);
      camera.position.lerp(camPos, Math.min(1, delta * 4));
      camLook.lerp(shellRef.current.position, Math.min(1, delta * 6));
      camera.lookAt(camLook);
    } else if (phase === "impact" || phase === "reveal") {
      camPos.set(profile.entryTo.x + 3.2, profile.entryTo.y + 2.4, profile.entryTo.z + 8.5);
      camera.position.lerp(camPos, Math.min(1, delta * 2));
      camLook.lerp(targetPos, Math.min(1, delta * 2));
      camera.lookAt(camLook);
    }
  });

  return (
    <group onClick={play}>
      <VehicleModel category={vehicle.category} nation={vehicle.nation} refs={refs} />

      <Trail width={2.2} length={7} color={profile.trailColor} attenuation={(t) => t * t}>
        <mesh ref={shellRef} visible={false}>
          <sphereGeometry args={[0.12, 12, 12]} />
          <meshBasicMaterial color="#ffe2b0" toneMapped={false} />
        </mesh>
      </Trail>

      <ImpactTarget position={targetPos} triggered={phase === "impact" || phase === "reveal"} />

      {revealed && (
        <Html position={[targetPos.x, targetPos.y + 1.8, targetPos.z]} center distanceFactor={8}>
          <VehicleStatChip vehicle={vehicle} />
        </Html>
      )}

      {phase === "idle" && !autoplay && (
        <Html position={[profile.entryTo.x - 2, profile.entryTo.y + 2.5, profile.entryTo.z]} center>
          <button
            onClick={play}
            className="px-4 py-2 rounded-full bg-panel/60 backdrop-blur-md border border-brass/40 text-parchment text-sm tracking-wide hover:bg-panel2/70 hover:border-brass transition"
          >
            ▶ Play
          </button>
        </Html>
      )}
    </group>
  );
}

function ImpactTarget({ position, triggered }: { position: THREE.Vector3; triggered: boolean }) {
  const fragments = useMemo(
    () => Array.from({ length: 10 }).map(() => ({
      dir: new THREE.Vector3((Math.random() - 0.5) * 2, Math.random() * 1.5, (Math.random() - 0.5) * 2),
      seed: Math.random(),
    })),
    []
  );
  const group = useRef<THREE.Group>(null!);

  useFrame((_, delta) => {
    if (!triggered || !group.current) return;
    group.current.children.forEach((child, i) => {
      const f = fragments[i];
      child.position.addScaledVector(f.dir, delta * 3);
      child.rotation.x += delta * (2 + f.seed * 3);
      child.rotation.y += delta * (2 + f.seed * 3);
      (child as THREE.Mesh).scale.multiplyScalar(1 - delta * 0.6);
    });
  });

  return (
    <group ref={group} position={position}>
      {triggered &&
        fragments.map((_, i) => (
          <mesh key={i}>
            <boxGeometry args={[0.18, 0.18, 0.18]} />
            <meshStandardMaterial color="#8f8f8f" emissive="#ff6a2b" emissiveIntensity={0.6} />
          </mesh>
        ))}
    </group>
  );
}

function VehicleStatChip({ vehicle }: { vehicle: Vehicle }) {
  return (
    <div className="w-64 rounded-xl bg-panel/70 backdrop-blur-xl border border-brass/30 shadow-dossier p-3 text-parchment select-none font-mono">
      <div className="text-[10px] uppercase tracking-widest2 text-brass/80">{vehicle.nation} · {vehicle.category}</div>
      <div className="text-base font-display tracking-wide">{vehicle.name}</div>
      <div className="mt-2 grid grid-cols-3 gap-1.5 text-center">
        <Stat label="BR" value={vehicle.br?.rb?.toFixed(1) ?? "—"} />
        <Stat label="Crew" value={vehicle.crew ? String(vehicle.crew) : "—"} />
        <Stat label="Rank" value={vehicle.rank ? String(vehicle.rank) : "—"} />
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-panel2/60 py-1">
      <div className="text-[9px] text-parchment/50">{label}</div>
      <div className="text-xs font-medium text-brass">{value}</div>
    </div>
  );
}
