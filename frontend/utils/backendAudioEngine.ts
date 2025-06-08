// Backend audio engine utility for PianoRoll
export class BackendAudioEngine {
  backendAudioContext: AudioContext | null = null;
  backendAudioBuffer: AudioBuffer | null = null;
  backendAudioSource: AudioBufferSourceNode | null = null;
  backendPlayStartTime = 0;
  backendPlayheadInterval: number | null = null;

  constructor() {}

  async initBackendAudio() {
    if (!this.backendAudioContext) {
      this.backendAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      if (this.backendAudioContext.state === 'suspended') {
        await this.backendAudioContext.resume();
      }
    } else if (this.backendAudioContext.state === 'suspended') {
      await this.backendAudioContext.resume();
    }
  }

  async decodeBackendAudio(audio_data: string): Promise<AudioBuffer | null> {
    if (!audio_data || !this.backendAudioContext) return null;
    try {
      let arrayBuffer: ArrayBuffer;
      if (audio_data.startsWith('data:')) {
        const base64Data = audio_data.split(',')[1];
        arrayBuffer = Uint8Array.from(atob(base64Data), c => c.charCodeAt(0)).buffer;
      } else {
        const response = await fetch(audio_data);
        arrayBuffer = await response.arrayBuffer();
      }
      if (arrayBuffer.byteLength === 0) return null;
      this.backendAudioBuffer = await this.backendAudioContext.decodeAudioData(arrayBuffer);
      return this.backendAudioBuffer;
    } catch (error) {
      this.backendAudioBuffer = null;
      return null;
    }
  }

  startBackendAudioPlayback(currentFlicks: number, onEnded: () => void) {
    if (!this.backendAudioContext || !this.backendAudioBuffer) return;
    if (this.backendAudioContext.state === 'suspended') {
      this.backendAudioContext.resume().then(() => this.actuallyStartPlayback(currentFlicks, onEnded));
    } else {
      this.actuallyStartPlayback(currentFlicks, onEnded);
    }
  }

  private actuallyStartPlayback(currentFlicks: number, onEnded: () => void) {
    if (!this.backendAudioContext || !this.backendAudioBuffer) return;
    if (this.backendAudioSource) {
      this.backendAudioSource.stop();
      this.backendAudioSource = null;
    }
    this.backendAudioSource = this.backendAudioContext.createBufferSource();
    this.backendAudioSource.buffer = this.backendAudioBuffer;
    this.backendAudioSource.connect(this.backendAudioContext.destination);
    const startPositionInSeconds = currentFlicks / 705600000;
    const currentTime = this.backendAudioContext.currentTime;
    this.backendAudioSource.start(currentTime, startPositionInSeconds);
    this.backendPlayStartTime = currentTime - startPositionInSeconds;
    this.backendAudioSource.onended = onEnded;
  }

  pauseBackendAudio(currentFlicksRef: { value: number }) {
    if (this.backendAudioSource && this.backendAudioContext) {
      const elapsedTime = this.backendAudioContext.currentTime - this.backendPlayStartTime;
      currentFlicksRef.value = Math.round(elapsedTime * 705600000);
      this.backendAudioSource.stop();
      this.backendAudioSource = null;
    }
    if (this.backendPlayheadInterval) {
      clearInterval(this.backendPlayheadInterval);
      this.backendPlayheadInterval = null;
    }
  }

  stopBackendAudio(currentFlicksRef: { value: number }) {
    if (this.backendAudioSource) {
      this.backendAudioSource.stop();
      this.backendAudioSource = null;
    }
    if (this.backendPlayheadInterval) {
      clearInterval(this.backendPlayheadInterval);
      this.backendPlayheadInterval = null;
    }
    currentFlicksRef.value = 0;
  }

  updateBackendPlayhead(isPlayingRef: { value: boolean }, currentFlicksRef: { value: number }, onStop: () => void) {
    if (!isPlayingRef.value || !this.backendAudioContext) return;
    this.backendPlayheadInterval = setInterval(() => {
      if (isPlayingRef.value && this.backendAudioContext && this.backendAudioBuffer) {
        const elapsedTime = this.backendAudioContext.currentTime - this.backendPlayStartTime;
        currentFlicksRef.value = Math.round(elapsedTime * 705600000);
        if (elapsedTime >= this.backendAudioBuffer.duration) {
          this.stopBackendAudio(currentFlicksRef);
          onStop();
        }
      }
    }, 16);
  }

  async downloadBackendAudio(audio_data: string) {
    if (!audio_data) return;
    let blob: Blob;
    let filename = 'piano_roll_audio.wav';
    if (audio_data.startsWith('data:')) {
      const response = await fetch(audio_data);
      blob = await response.blob();
      const mimeMatch = audio_data.match(/data:audio\/([^;]+)/);
      if (mimeMatch) {
        const format = mimeMatch[1];
        filename = `piano_roll_audio.${format}`;
      }
    } else {
      const response = await fetch(audio_data);
      if (!response.ok) return;
      blob = await response.blob();
      const urlMatch = audio_data.match(/\.([^.?]+)(\?|$)/);
      if (urlMatch) {
        const extension = urlMatch[1];
        filename = `piano_roll_audio.${extension}`;
      }
    }
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  dispose() {
    if (this.backendPlayheadInterval) {
      clearInterval(this.backendPlayheadInterval);
      this.backendPlayheadInterval = null;
    }
    if (this.backendAudioSource) {
      this.backendAudioSource.stop();
      this.backendAudioSource = null;
    }
    if (this.backendAudioContext) {
      this.backendAudioContext.close();
      this.backendAudioContext = null;
    }
    this.backendAudioBuffer = null;
  }
}

export {};
