// ═══════════════════════════════════
// FILE: remotion/src/components/Scene.tsx
// PURPOSE: Single scene component — background image + dark overlay + scene badge
// ═══════════════════════════════════

import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  useCurrentFrame,
} from "remotion";

interface SceneComponentProps {
  imageUrl: string;
  durationInFrames: number;
  sceneNumber: number;
}

export const Scene: React.FC<SceneComponentProps> = ({
  imageUrl,
  durationInFrames,
  sceneNumber,
}) => {
  const frame = useCurrentFrame();

  // Fade-in over the first 15 frames
  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Subtle zoom effect
  const scale = interpolate(frame, [0, durationInFrames], [1.0, 1.05], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ opacity }}>
      {/* Background image */}
      <AbsoluteFill
        style={{
          transform: `scale(${scale})`,
          overflow: "hidden",
        }}
      >
        <Img
          src={imageUrl}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      </AbsoluteFill>

      {/* Dark gradient overlay for text readability */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.1) 40%, rgba(0,0,0,0.6) 100%)",
        }}
      />

      {/* Scene number badge (top-left) */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: 40,
          backgroundColor: "rgba(255, 255, 255, 0.15)",
          backdropFilter: "blur(10px)",
          borderRadius: 12,
          padding: "8px 18px",
          color: "#ffffff",
          fontSize: 24,
          fontWeight: 600,
          fontFamily: "'Inter', sans-serif",
          letterSpacing: 1,
        }}
      >
        SCENE {sceneNumber}
      </div>
    </AbsoluteFill>
  );
};
