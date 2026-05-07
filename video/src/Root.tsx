import React from 'react';
import {Composition} from 'remotion';
import {AdComposition, AdScript} from './AdComposition';
import defaultScript from './script_data.json';

export const RemotionRoot: React.FC = () => {
  const fps = 30;
  const durationSeconds = 60;

  return (
    <Composition
      id="AdVideo"
      component={AdComposition}
      durationInFrames={durationSeconds * fps}
      fps={fps}
      width={1080}
      height={1920}
      defaultProps={{script: defaultScript as AdScript}}
    />
  );
};
