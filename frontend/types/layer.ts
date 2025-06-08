// Piano roll layer system types

export interface LayerRenderContext {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  width: number;
  height: number;
  horizontalScroll: number;
  verticalScroll: number;
  pixelsPerBeat: number;
  tempo: number;
  currentFlicks: number;
  isPlaying: boolean;
  timeSignature: { numerator: number; denominator: number };
  snapSetting: string;
  [key: string]: any;
}

export interface LayerProps {
  opacity: number;
  visible: boolean;
  zIndex: number;
  name: string;
}

export interface Note {
  id: string;
  start: number;
  duration: number;
  startFlicks?: number;
  durationFlicks?: number;
  startSeconds?: number;
  durationSeconds?: number;
  endSeconds?: number;
  startBeats?: number;
  durationBeats?: number;
  startTicks?: number;
  durationTicks?: number;
  startSample?: number;
  durationSamples?: number;
  pitch: number;
  velocity: number;
  lyric?: string;
  phoneme?: string;
}

export interface LineDataPoint {
  x: number;
  y: number;
}

export interface LineLayerConfig {
  name: string;
  color: string;
  lineWidth: number;
  yMin: number;
  yMax: number;
  height?: number;
  position?: 'top' | 'center' | 'bottom' | 'overlay';
  renderMode?: 'default' | 'piano_grid' | 'independent_range';
  visible?: boolean;
  opacity?: number;
  dataType?: string;
  unit?: string;
  originalRange?: {
    minHz?: number;
    maxHz?: number;
    minMidi?: number;
    maxMidi?: number;
    min?: number;
    max?: number;
    voiced_ratio?: number;
    y_min?: number;
    y_max?: number;
  };
}
