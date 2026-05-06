// ═══════════════════════════════════
// FILE: remotion/src/components/Subtitle.tsx
// PURPOSE: Animated subtitle component — highlights current text
// ═══════════════════════════════════

import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { SubtitleEntry } from "../types";

interface SubtitleProps {
  subtitles: SubtitleEntry[];
}

export const Subtitle: React.FC<SubtitleProps> = ({ subtitles }) => {
  const frame = useCurrentFrame();

  // Find the currently active subtitle
  const activeSubtitle = subtitles.find(
    (sub) => frame >= sub.startFrame && frame < sub.endFrame
  );

  if (!activeSubtitle) {
    return null;
  }

  // Fade in/out animation
  const fadeIn = interpolate(
    frame,
    [activeSubtitle.startFrame, activeSubtitle.startFrame + 5],
    [0, 1],
    { extrapolateRight: "clamp", extrapolateLeft: "clamp" }
  );

  const fadeOut = interpolate(
    frame,
    [activeSubtitle.endFrame - 5, activeSubtitle.endFrame],
    [1, 0],
    { extrapolateRight: "clamp", extrapolateLeft: "clamp" }
  );

  const opacity = Math.min(fadeIn, fadeOut);

  // Slight upward slide
  const translateY = interpolate(
    frame,
    [activeSubtitle.startFrame, activeSubtitle.startFrame + 10],
    [20, 0],
    { extrapolateRight: "clamp", extrapolateLeft: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: 180,
      }}
    >
      <div
        style={{
          opacity,
          transform: `translateY(${translateY}px)`,
          maxWidth: "90%",
          textAlign: "center",
          padding: "16px 28px",
          borderRadius: 16,
          backgroundColor: "rgba(0, 0, 0, 0.55)",
          backdropFilter: "blur(8px)",
        }}
      >
        <span
          style={{
            color: "#ffffff",
            fontSize: 48,
            fontWeight: 800,
            fontFamily: "'Inter', 'Helvetica Neue', sans-serif",
            lineHeight: 1.3,
            textShadow: "0 2px 8px rgba(0,0,0,0.8)",
            letterSpacing: -0.5,
          }}
        >
          {activeSubtitle.text}
        </span>
      </div>
    </AbsoluteFill>
  );
};
