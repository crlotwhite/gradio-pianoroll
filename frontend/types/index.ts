/**
 * Centralized type exports for Piano Roll
 *
 * This module serves as the main barrel file for all type definitions.
 * Import types from here to avoid importing from multiple files.
 */

// ============================================================================
// Note Types (from ./notes)
// ============================================================================

export type {
  Note,
  NoteTimingData,
  TimeSignature,
  NoteRenderConfig,
  RenderableNote,
  QuantizationSettings,
} from './notes';

// ============================================================================
// Playback Types (from ./playback)
// ============================================================================

export type {
  PlaybackState,
  AudioSourceType,
  PlaybackEventType,
  PlaybackEventPayload,
  AudioRenderConfig,
  AudioRenderResult,
  AudioEngine,
  BackendAudioConfig,
  WaveformConfig,
} from './playback';

// ============================================================================
// Event Types (from ./events)
// ============================================================================

export type {
  PianoRollEvent,
  NoteChangeEvent,
  LyricInputEvent,
  DataChangeEvent,
  PlaybackEvent,
  ScrollEvent,
  PositionInfoEvent,
  UtilsReadyEvent,
  LayerChangedEvent,
  GridScrollEvent,
  EditModeChangePayload,
  TempoChangePayload,
  TimeSignatureChangePayload,
  SnapChangePayload,
  ZoomChangePayload,
  PositionChangePayload,
  ToolbarEventMap,
  GridEventMap,
} from './events';

// ============================================================================
// Audio Types (from ./audio)
// ============================================================================

export type {
  PlayheadUpdateCallback,
  AudioBufferWithMetadata,
  WaveformAnalysis,
  AudioExportOptions,
  AudioDeviceInfo,
  AudioContextState,
} from './audio';

// ============================================================================
// Component Props Types (from ./component)
// ============================================================================

export type {
  PianoRollProps,
  ToolbarProps,
  LayerControlPanelProps,
  DebugComponentProps,
  KeyboardProps,
  TimelineProps,
  PlayheadProps,
  GridProps,
  LyricEditorProps,
  WaveformProps,
} from './component';

// ============================================================================
// Layer Types (from ./layer)
// ============================================================================

export type {
  LayerRenderContext,
  LayerProps,
  LineDataPoint,
  LineLayerConfig,
  LayerType,
  Layer,
} from './layer';

// ============================================================================
// Piano Roll Data Types (from ./piano_roll_data)
// ============================================================================

export type {
  LineLayerConfigWithData,
  PianoRollData,
  PianoRollSettings,
  PianoRollValidationResult,
} from './piano_roll_data';

// ============================================================================
// Re-export from utils (coordinate and mouse handler types)
// These are kept here for convenience, but are defined in the utils directory.
// ============================================================================

export type {
  MeasureInfo,
  PitchInfo,
  CoordinateConfig,
  MousePositionInfo,
} from '../utils/coordinateUtils';

export type {
  EditMode,
  InteractionMode,
  MouseHandlerConfig,
  MouseState,
  MouseDownResult,
  MouseMoveResult,
  MouseUpResult,
  FindNoteCallback,
  SnapToGridCallback,
} from '../utils/mouseHandler';

export type {
  RenderableNote as NoteRendererRenderableNote,
  NoteRenderConfig as NoteRendererNoteRenderConfig,
  NoteRenderContext,
} from '../utils/noteRenderer';
