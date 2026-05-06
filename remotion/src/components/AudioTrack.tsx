// ═══════════════════════════════════
// FILE: remotion/src/components/AudioTrack.tsx
// PURPOSE: ElevenLabs audio sync component
// ═══════════════════════════════════

import React from "react";
import { Audio, staticFile } from "remotion";

interface AudioTrackProps {
  src: string;
}

export const AudioTrack: React.FC<AudioTrackProps> = ({ src }) => {
  if (!src) {
    return null;
  }

  // If the source is a relative path, try to resolve it via staticFile
  // Otherwise, use it as-is (could be an absolute path or URL)
  const audioSrc = src.startsWith("http") || src.startsWith("/")
    ? src
    : staticFile(src);

  return (
    <Audio
      src={audioSrc}
      volume={1}
      startFrom={0}
    />
  );
};
