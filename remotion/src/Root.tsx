// ═══════════════════════════════════
// FILE: remotion/src/Root.tsx
// PURPOSE: Remotion root — registers compositions
// ═══════════════════════════════════

import React from "react";
import { Composition } from "remotion";
import { AdVideo } from "./AdVideo";
import { AdVideoProps } from "./types";

// Default props for the studio preview
const defaultProps: AdVideoProps = {
  scenes: [
    {
      sceneNumber: 1,
      sceneName: "Hook",
      startFrame: 0,
      durationInFrames: 150,
      imageUrl: "https://picsum.photos/seed/100/1080/1920",
      visualDirection: "Close-up of phone showing red portfolio",
      voiceoverText: "Are you tired of losing money trading alone?",
      subtitleText: "Are you tired of losing money trading alone?",
    },
    {
      sceneNumber: 2,
      sceneName: "Pain Point",
      startFrame: 150,
      durationInFrames: 300,
      imageUrl: "https://picsum.photos/seed/200/1080/1920",
      visualDirection: "Confused trader with multiple monitors",
      voiceoverText:
        "Every day, thousands of retail traders lose money following random advice.",
      subtitleText: "Thousands lose money following random advice.",
    },
    {
      sceneNumber: 3,
      sceneName: "Agitation",
      startFrame: 450,
      durationInFrames: 300,
      imageUrl: "https://picsum.photos/seed/300/1080/1920",
      visualDirection: "Market crash headlines montage",
      voiceoverText:
        "While you second-guess every trade, smart money is already positioned.",
      subtitleText: "Smart money is already positioned.",
    },
    {
      sceneNumber: 4,
      sceneName: "Solution",
      startFrame: 750,
      durationInFrames: 450,
      imageUrl: "https://picsum.photos/seed/400/1080/1920",
      visualDirection: "CrowdWisdomTrading platform with live chat",
      voiceoverText:
        "CrowdWisdomTrading gives you daily live sessions and 85% win rate alerts.",
      subtitleText: "Daily live sessions. 85% win rate alerts.",
    },
    {
      sceneNumber: 5,
      sceneName: "Social Proof",
      startFrame: 1200,
      durationInFrames: 300,
      imageUrl: "https://picsum.photos/seed/500/1080/1920",
      visualDirection: "Scrolling member testimonials",
      voiceoverText:
        "Over 3,000 traders have already made the switch.",
      subtitleText: "3,000+ traders made the switch.",
    },
    {
      sceneNumber: 6,
      sceneName: "CTA",
      startFrame: 1500,
      durationInFrames: 300,
      imageUrl: "https://picsum.photos/seed/600/1080/1920",
      visualDirection: "Logo with URL and Join Now button",
      voiceoverText:
        "Join 3,000 plus traders at CrowdWisdomTrading.com. Your first week is free.",
      subtitleText:
        "Join 3,000+ traders at CrowdWisdomTrading.com — First week FREE!",
    },
  ],
  subtitles: [],
  audioSrc: "",
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AdVideo"
        component={AdVideo}
        durationInFrames={1800}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={defaultProps}
      />
    </>
  );
};
