// ═══════════════════════════════════
// FILE: remotion/src/types.ts
// PURPOSE: TypeScript interfaces for Remotion props
// ═══════════════════════════════════

export interface SceneProps {
  sceneNumber: number;
  sceneName: string;
  startFrame: number;
  durationInFrames: number;
  imageUrl: string;
  visualDirection: string;
  voiceoverText: string;
  subtitleText: string;
}

export interface SubtitleEntry {
  startFrame: number;
  endFrame: number;
  start_ms: number;
  end_ms: number;
  text: string;
  sceneNumber: number;
}

export interface AdVideoProps {
  scenes: SceneProps[];
  subtitles: SubtitleEntry[];
  audioSrc: string;
}
