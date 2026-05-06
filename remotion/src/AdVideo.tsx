// ═══════════════════════════════════
// FILE: remotion/src/AdVideo.tsx
// PURPOSE: Main composition — assembles all scenes with audio and subtitles
// ═══════════════════════════════════

import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { AdVideoProps } from "./types";
import { Scene } from "./components/Scene";
import { Subtitle } from "./components/Subtitle";
import { AudioTrack } from "./components/AudioTrack";

export const AdVideo: React.FC<AdVideoProps> = ({
  scenes,
  subtitles,
  audioSrc,
}) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0a",
      }}
    >
      {/* Render each scene as a Sequence */}
      {scenes.map((scene) => (
        <Sequence
          key={scene.sceneNumber}
          from={scene.startFrame}
          durationInFrames={scene.durationInFrames}
          name={`Scene ${scene.sceneNumber}: ${scene.sceneName}`}
        >
          <Scene
            imageUrl={scene.imageUrl}
            durationInFrames={scene.durationInFrames}
            sceneNumber={scene.sceneNumber}
          />
        </Sequence>
      ))}

      {/* Subtitle overlay — rendered on top of all scenes */}
      <AbsoluteFill>
        <Subtitle subtitles={subtitles} />
      </AbsoluteFill>

      {/* Audio track */}
      {audioSrc && <AudioTrack src={audioSrc} />}
    </AbsoluteFill>
  );
};
