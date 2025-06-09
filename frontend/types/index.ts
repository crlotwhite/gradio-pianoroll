/**
 * Main type definitions index
 * Re-exports all types for easy importing
 */

// Backend data types
export type {
  Note,
  PianoRollData,
  PianoRollBackendData,
  CurveData,
  CurvePoint,
  SegmentData,
  AudioProcessingOptions,
  TimingContext,
  CreateNoteResponse,
  TimingCalculationResult
} from './backend';

// Component types
export type {
  PianoRollProps,
  ToolbarProps,
  LayerControlPanelProps,
  DebugComponentProps,
  PianoRollChangeEvent,
  LyricInputEvent,
  NotesChangeEvent,
  PlaybackEvent,
  BackendDataManager as BackendDataManagerType,
  NoteCreationParams,
  NoteEditParams,
  TimingCalculatorOptions,
  AudioAnalysisResult
} from './component';

// Layer types (if needed)
export * from './layer';

// Audio types (if needed)
export * from './audio'; 