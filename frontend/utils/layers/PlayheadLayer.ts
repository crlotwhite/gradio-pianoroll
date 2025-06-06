/**
 * PlayheadLayer - Renders the playback position indicator
 */

import { BaseLayer, LayerZIndex } from '../LayerSystem';
import type { LayerRenderContext } from '../LayerSystem';
import { flicksToPixels } from '../flicks';

export class PlayheadLayer extends BaseLayer {
  // Playhead colors
  private readonly PLAYHEAD_COLOR = '#ff5252';
  private readonly PLAYHEAD_COLOR_SHADOW = 'rgba(255, 82, 82, 0.3)';

  constructor() {
    super('playhead', LayerZIndex.PLAYHEAD);
  }

  render(context: LayerRenderContext): void {
    const { ctx, width, height, horizontalScroll, pixelsPerBeat, tempo, currentFlicks, isPlaying } = context;

    // Don't render if not playing and no specific position is set
    if (!isPlaying && currentFlicks === 0) {
      return;
    }

    // Calculate playhead position
    const positionInPixels = flicksToPixels(currentFlicks, pixelsPerBeat, tempo);
    const visiblePosition = positionInPixels - horizontalScroll;

    // Only render if playhead is visible
    if (visiblePosition >= 0 && visiblePosition <= width) {
      // Draw playhead line
      ctx.strokeStyle = this.PLAYHEAD_COLOR;
      ctx.lineWidth = 2;
      ctx.shadowColor = this.PLAYHEAD_COLOR_SHADOW;
      ctx.shadowBlur = 6;

      ctx.beginPath();
      ctx.moveTo(visiblePosition, 0);
      ctx.lineTo(visiblePosition, height);
      ctx.stroke();

      // Reset shadow for other elements
      ctx.shadowColor = 'transparent';
      ctx.shadowBlur = 0;

      // Draw playhead top indicator (triangle)
      const triangleSize = 8;
      ctx.fillStyle = this.PLAYHEAD_COLOR;
      ctx.beginPath();
      ctx.moveTo(visiblePosition, 0);
      ctx.lineTo(visiblePosition - triangleSize / 2, triangleSize);
      ctx.lineTo(visiblePosition + triangleSize / 2, triangleSize);
      ctx.closePath();
      ctx.fill();
    }
  }

  // Helper method to check if playhead is visible in current viewport
  isPlayheadVisible(currentFlicks: number, horizontalScroll: number, width: number, pixelsPerBeat: number, tempo: number): boolean {
    const positionInPixels = flicksToPixels(currentFlicks, pixelsPerBeat, tempo);
    const visiblePosition = positionInPixels - horizontalScroll;
    return visiblePosition >= 0 && visiblePosition <= width;
  }
} 