"use client";

import { Suspense, ReactNode } from "react";
import { Canvas } from "@react-three/fiber";
import { Environment, ContactShadows, AdaptiveDpr, AdaptiveEvents } from "@react-three/drei";
import { EffectComposer, Bloom, DepthOfField, Vignette, ChromaticAberration } from "@react-three/postprocessing";
import * as THREE from "three";

/**
 * Global cinematic Canvas provider.
 * Wrap any page/section that needs the WebGL cinematic layer with <Scene3D>.
 * Keeps a single WebGL context per mounted sequence to avoid context-loss
 * from stacking multiple <Canvas> instances on one page.
 */
export default function Scene3D({
  children,
  cameraPosition = [0, 3.2, 9],
  fov = 40,
  postFx = true,
}: {
  children: ReactNode;
  cameraPosition?: [number, number, number];
  fov?: number;
  postFx?: boolean;
}) {
  return (
    <Canvas
      shadows
      dpr={[1, 1.75]} // cap DPR — heavy bloom/DOF at native retina DPR tanks mobile FPS
      gl={{
        antialias: false, // MSAA disabled on purpose; post-processing chain does its own AA-ish softening
        powerPreference: "high-performance",
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.1,
      }}
      camera={{ position: cameraPosition, fov, near: 0.1, far: 200 }}
      className="!absolute inset-0"
    >
      <AdaptiveDpr pixelated={false} />
      <AdaptiveEvents />

      <color attach="background" args={["#05070a"]} />
      <fog attach="fog" args={["#05070a", 12, 45]} />

      {/* Key/rim lighting — battlefield dusk mood */}
      <ambientLight intensity={0.15} />
      <directionalLight
        position={[8, 12, 6]}
        intensity={2.2}
        color="#ffd8a8"
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-far={40}
        shadow-camera-left={-15}
        shadow-camera-right={15}
        shadow-camera-top={15}
        shadow-camera-bottom={-15}
      />
      <directionalLight position={[-10, 5, -8]} intensity={0.6} color="#3a6dff" />

      <Suspense fallback={null}>
        <Environment preset="sunset" background={false} blur={0.8} />
        {children}
        <ContactShadows
          position={[0, -0.01, 0]}
          opacity={0.55}
          scale={30}
          blur={2.2}
          far={8}
          resolution={512}
          color="#000000"
        />
      </Suspense>

      {postFx && (
        <EffectComposer multisampling={0} enableNormalPass={false}>
          <DepthOfField focusDistance={0.012} focalLength={0.035} bokehScale={3.5} height={480} />
          <Bloom intensity={0.9} luminanceThreshold={0.22} luminanceSmoothing={0.3} mipmapBlur radius={0.7} />
          <ChromaticAberration offset={new THREE.Vector2(0.0006, 0.0006)} />
          <Vignette eskil={false} offset={0.15} darkness={0.7} />
        </EffectComposer>
      )}
    </Canvas>
  );
}
