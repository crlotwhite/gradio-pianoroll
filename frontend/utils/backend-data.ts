/**
 * Frontend utility class for managing backend data
 * Mirrors the functionality of PianoRollBackendData Python class
 */

import type { PianoRollBackendData, CurveData, SegmentData } from '../types/backend';

export class BackendDataManager {
  private _data: PianoRollBackendData;

  constructor(initialData?: Partial<PianoRollBackendData>) {
    this._data = {
      audio_data: null,
      curve_data: {},
      segment_data: [],
      use_backend_audio: false,
      ...initialData
    };
  }

  // Getter for the data
  get data(): PianoRollBackendData {
    return { ...this._data };
  }

  // Set audio data
  setAudio(audioData: string): void {
    this._data.audio_data = audioData;
    console.log("🎵 [BackendDataManager] Audio data set:", !!audioData);
  }

  // Add or update curve data
  addCurve(name: string, curveData: CurveData): void {
    if (!this._data.curve_data) {
      this._data.curve_data = {};
    }
    this._data.curve_data[name] = curveData;
    console.log(`📊 [BackendDataManager] Curve '${name}' added:`, curveData.dataType);
  }

  // Remove curve data
  removeCurve(name: string): void {
    if (this._data.curve_data && name in this._data.curve_data) {
      delete this._data.curve_data[name];
      console.log(`📊 [BackendDataManager] Curve '${name}' removed`);
    }
  }

  // Add segment data
  addSegment(segment: SegmentData): void {
    if (!this._data.segment_data) {
      this._data.segment_data = [];
    }
    this._data.segment_data.push(segment);
    console.log("📍 [BackendDataManager] Segment added:", segment.type, segment.value);
  }

  // Clear all segment data
  clearSegments(): void {
    this._data.segment_data = [];
    console.log("📍 [BackendDataManager] All segments cleared");
  }

  // Enable/disable backend audio
  enableBackendAudio(enable: boolean = true): void {
    this._data.use_backend_audio = enable;
    console.log("🔊 [BackendDataManager] Backend audio:", enable ? "enabled" : "disabled");
  }

  // Check if any backend data is present
  hasData(): boolean {
    return (
      !!this._data.audio_data ||
      (!!this._data.curve_data && Object.keys(this._data.curve_data).length > 0) ||
      (!!this._data.segment_data && this._data.segment_data.length > 0)
    );
  }

  // Get curve data by name
  getCurve(name: string): CurveData | undefined {
    return this._data.curve_data?.[name];
  }

  // Get all curve names
  getCurveNames(): string[] {
    return Object.keys(this._data.curve_data || {});
  }

  // Get segments by type
  getSegmentsByType(type: string): SegmentData[] {
    return (this._data.segment_data || []).filter(segment => segment.type === type);
  }

  // Update from backend response
  updateFromBackend(backendData: Partial<PianoRollBackendData>): void {
    if (backendData.audio_data !== undefined) {
      this._data.audio_data = backendData.audio_data;
    }
    if (backendData.curve_data !== undefined) {
      this._data.curve_data = { ...backendData.curve_data };
    }
    if (backendData.segment_data !== undefined) {
      this._data.segment_data = [...backendData.segment_data];
    }
    if (backendData.use_backend_audio !== undefined) {
      this._data.use_backend_audio = backendData.use_backend_audio;
    }

    console.log("🔄 [BackendDataManager] Updated from backend:", {
      hasAudio: !!this._data.audio_data,
      curveCount: Object.keys(this._data.curve_data || {}).length,
      segmentCount: (this._data.segment_data || []).length,
      useBackendAudio: this._data.use_backend_audio
    });
  }

  // Export data for sending to backend
  toDict(): PianoRollBackendData {
    return { ...this._data };
  }

  // Reset all data
  reset(): void {
    this._data = {
      audio_data: null,
      curve_data: {},
      segment_data: [],
      use_backend_audio: false
    };
    console.log("🔄 [BackendDataManager] Reset to initial state");
  }

  // Clone the manager
  clone(): BackendDataManager {
    return new BackendDataManager(this._data);
  }
}

// Utility functions for working with backend data

/**
 * Extract backend data from a piano roll value object
 */
export function extractBackendData(value: any): PianoRollBackendData {
  const backendData: PianoRollBackendData = {
    audio_data: null,
    curve_data: {},
    segment_data: [],
    use_backend_audio: false
  };

  if (value && typeof value === 'object') {
    if ('audio_data' in value) {
      backendData.audio_data = value.audio_data;
    }
    if ('curve_data' in value && value.curve_data) {
      backendData.curve_data = value.curve_data;
    }
    if ('segment_data' in value && Array.isArray(value.segment_data)) {
      backendData.segment_data = value.segment_data;
    }
    if ('use_backend_audio' in value) {
      backendData.use_backend_audio = !!value.use_backend_audio;
    }
  }

  return backendData;
}

/**
 * Merge backend data into a piano roll value object
 */
export function mergeBackendData(value: any, backendData: PianoRollBackendData): any {
  if (!value || typeof value !== 'object') {
    return value;
  }

  return {
    ...value,
    ...backendData
  };
}

/**
 * Validate curve data structure
 */
export function validateCurveData(curveData: any): curveData is CurveData {
  return (
    curveData &&
    typeof curveData === 'object' &&
    typeof curveData.color === 'string' &&
    typeof curveData.lineWidth === 'number' &&
    Array.isArray(curveData.data) &&
    typeof curveData.dataType === 'string'
  );
}

/**
 * Validate segment data structure
 */
export function validateSegmentData(segmentData: any): segmentData is SegmentData {
  return (
    segmentData &&
    typeof segmentData === 'object' &&
    typeof segmentData.start === 'number' &&
    typeof segmentData.end === 'number' &&
    typeof segmentData.type === 'string' &&
    typeof segmentData.value === 'string'
  );
} 