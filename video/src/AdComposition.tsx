import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export interface ScriptSegment {
  text: string;
  start: number;
  duration: number;
}

export interface AdScript {
  title: string;
  narration: string;
  segments: ScriptSegment[];
  voice_path: string;
  image_paths: string[];
}

const BRAND_COLOR = '#00C896';

export const AdComposition: React.FC<{script: AdScript}> = ({script}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const currentSecond = frame / fps;

  // Current subtitle segment
  const currentSegment = script.segments.find(
    (seg) =>
      currentSecond >= seg.start && currentSecond < seg.start + seg.duration,
  );

  // Cycle through images — each image shows for ~10 seconds
  const imageCount = script.image_paths.length || 1;
  const secondsPerImage = Math.ceil(60 / imageCount);
  const imageIndex = Math.min(
    Math.floor(currentSecond / secondsPerImage),
    imageCount - 1,
  );
  const currentImage = script.image_paths[imageIndex];

  // Subtitle fade in/out
  const subtitleOpacity = currentSegment
    ? interpolate(
        frame % (fps * currentSegment.duration),
        [0, fps * 0.3, fps * (currentSegment.duration - 0.3), fps * currentSegment.duration],
        [0, 1, 1, 0],
        {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
      )
    : 0;

  // Subtitle scale spring
  const subtitleScale = currentSegment
    ? spring({
        frame: frame - currentSegment.start * fps,
        fps,
        config: {damping: 12, stiffness: 200},
        durationInFrames: fps * 0.4,
      })
    : 1;

  // Logo fade in
  const logoOpacity = interpolate(frame, [0, fps * 1], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Progress bar
  const progressWidth = (frame / durationInFrames) * 100;

  return (
    <AbsoluteFill style={{backgroundColor: '#000000'}}>

      {/* Background image */}
      {currentImage && (
        <AbsoluteFill>
          <Img
            src={staticFile(currentImage)}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
          />
          {/* Dark vignette overlay */}
          <AbsoluteFill
            style={{
              background:
                'linear-gradient(to bottom, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.1) 40%, rgba(0,0,0,0.7) 80%, rgba(0,0,0,0.9) 100%)',
            }}
          />
        </AbsoluteFill>
      )}

      {/* Voice audio */}
      {script.voice_path && (
        <Audio src={staticFile(script.voice_path)} />
      )}

      {/* Top bar — CWT branding */}
      <AbsoluteFill
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          paddingTop: 80,
          opacity: logoOpacity,
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 16,
            background: 'rgba(0,0,0,0.6)',
            borderRadius: 50,
            padding: '12px 32px',
            border: `2px solid ${BRAND_COLOR}`,
          }}
        >
          <div
            style={{
              width: 16,
              height: 16,
              borderRadius: '50%',
              backgroundColor: BRAND_COLOR,
            }}
          />
          <span
            style={{
              color: '#FFFFFF',
              fontSize: 28,
              fontWeight: 700,
              letterSpacing: 1,
              fontFamily: 'Arial, sans-serif',
            }}
          >
            CrowdWisdomTrading
          </span>
        </div>
      </AbsoluteFill>

      {/* Subtitle area */}
      <AbsoluteFill
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'flex-end',
          alignItems: 'center',
          paddingBottom: 120,
          paddingLeft: 40,
          paddingRight: 40,
        }}
      >
        {currentSegment && (
          <div
            style={{
              opacity: subtitleOpacity,
              transform: `scale(${subtitleScale})`,
              textAlign: 'center',
            }}
          >
            <div
              style={{
                color: '#FFFFFF',
                fontSize: 52,
                fontWeight: 800,
                lineHeight: 1.25,
                textShadow: '0 4px 20px rgba(0,0,0,0.8)',
                background: 'rgba(0,0,0,0.45)',
                borderRadius: 16,
                padding: '20px 32px',
                border: `3px solid ${BRAND_COLOR}`,
                fontFamily: 'Arial, sans-serif',
                maxWidth: 900,
              }}
            >
              {currentSegment.text}
            </div>
          </div>
        )}
      </AbsoluteFill>

      {/* Progress bar */}
      <AbsoluteFill
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          paddingBottom: 40,
          paddingLeft: 40,
          paddingRight: 40,
        }}
      >
        <div
          style={{
            width: '100%',
            height: 6,
            backgroundColor: 'rgba(255,255,255,0.3)',
            borderRadius: 3,
          }}
        >
          <div
            style={{
              width: `${progressWidth}%`,
              height: '100%',
              backgroundColor: BRAND_COLOR,
              borderRadius: 3,
            }}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
