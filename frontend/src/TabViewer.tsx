// TabViewer — renders a Guitar Pro / MusicXML tab with synchronized playback.
//
// This is the P1 upgrade over the ASCII preview: alphaTab both engraves the tab
// and plays it back with a moving cursor (the Songsterr-style experience).
//
// TODO(P1):
//   * import { AlphaTabApi } from "@coderline/alphatab"
//   * mount on a container ref, load the .gp5/.musicxml returned by the backend
//   * wire play/pause, speed (playbackSpeed), and loop-selection controls
//
// Sketch:
//
//   const api = new AlphaTabApi(containerRef.current, {
//     file: tabUrl,
//     player: { enablePlayer: true, soundFont: "/soundfont.sf2" },
//   });
//   api.playbackSpeed = 0.75;   // slow-down for practice
//
export default function TabViewer({ tabUrl }: { tabUrl: string }) {
  return (
    <div data-tab-url={tabUrl}>
      {/* alphaTab mounts here (P1) */}
    </div>
  );
}
