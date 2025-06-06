/**
 * GridLayer - Renders the background grid lines (measures, beats, subdivisions)
 */

import { BaseLayer, LayerZIndex } from '../LayerSystem';
import type { LayerRenderContext } from '../LayerSystem';

export class GridLayer extends BaseLayer {
  // Grid colors
  private readonly GRID_COLOR = '#444444';
  private readonly BEAT_COLOR = '#555555';
  private readonly MEASURE_COLOR = '#666666';
  private readonly BACKGROUND_COLOR = '#2c2c2c';

  constructor() {
    super('grid', LayerZIndex.GRID);
  }

  render(context: LayerRenderContext): void {
    const { ctx, width, height, horizontalScroll, verticalScroll, pixelsPerBeat, timeSignature, snapSetting } = context;

    // Draw background
    ctx.fillStyle = this.BACKGROUND_COLOR;
    ctx.fillRect(0, 0, width, height);

    // Calculate grid dimensions
    const NOTE_HEIGHT = 20;
    const TOTAL_NOTES = 128;
    const beatsPerMeasure = timeSignature.numerator;
    const pixelsPerMeasure = beatsPerMeasure * pixelsPerBeat;

    // Calculate visible area
    const startX = horizontalScroll;
    const endX = horizontalScroll + width;
    const startY = verticalScroll;
    const endY = verticalScroll + height;

    // Draw vertical grid lines (beat and measure lines)
    const startMeasure = Math.floor(startX / pixelsPerMeasure);
    const endMeasure = Math.ceil(endX / pixelsPerMeasure);

    for (let measure = startMeasure; measure <= endMeasure; measure++) {
      const measureX = measure * pixelsPerMeasure - horizontalScroll;

      // Draw measure line
      ctx.strokeStyle = this.MEASURE_COLOR;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(measureX, 0);
      ctx.lineTo(measureX, height);
      ctx.stroke();

      // Draw beat lines within measure
      if (snapSetting === '1/1') {
        // No beat lines for whole notes
      } else if (snapSetting === '1/2') {
        // Show only the middle beat line for half notes (divides measure in half)
        const middleBeat = Math.floor(beatsPerMeasure / 2);
        if (middleBeat > 0 && middleBeat < beatsPerMeasure) {
          const beatX = measureX + middleBeat * pixelsPerBeat;
          ctx.strokeStyle = this.BEAT_COLOR;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(beatX, 0);
          ctx.lineTo(beatX, height);
          ctx.stroke();
        }
      } else {
        // Show all beat lines for other snap settings
        for (let beat = 1; beat < beatsPerMeasure; beat++) {
          const beatX = measureX + beat * pixelsPerBeat;

          ctx.strokeStyle = this.BEAT_COLOR;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(beatX, 0);
          ctx.lineTo(beatX, height);
          ctx.stroke();
        }
      }

      // Skip subdivision lines for 1/1 snap setting
      if (snapSetting === '1/1') {
        continue;
      }

      // Calculate subdivisions based on snap setting
      const subdivisions = this.getSubdivisionsFromSnapSetting(snapSetting, beatsPerMeasure, pixelsPerMeasure, pixelsPerBeat);

      // Draw subdivision lines
      for (let division = 1; division < subdivisions.divisionsPerMeasure; division++) {
        // Skip if this is already a beat line
        if (division % (subdivisions.divisionsPerMeasure / beatsPerMeasure) === 0) {
          continue;
        }

        const divisionX = measureX + division * subdivisions.pixelsPerDivision;

        ctx.strokeStyle = this.GRID_COLOR;
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(divisionX, 0);
        ctx.lineTo(divisionX, height);
        ctx.stroke();
      }
    }

    // Draw horizontal grid lines
    const GRID_LINE_INTERVAL = NOTE_HEIGHT;
    const startRow = Math.floor(startY / GRID_LINE_INTERVAL);
    const endRow = Math.ceil(endY / GRID_LINE_INTERVAL);

    for (let row = startRow; row <= endRow; row++) {
      const rowY = row * GRID_LINE_INTERVAL - verticalScroll;

      // Draw row background for black keys (C#, D#, F#, G#, A#)
      const midiNote = TOTAL_NOTES - 1 - row;
      const noteIndex = midiNote % 12;

      if ([1, 3, 6, 8, 10].includes(noteIndex)) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
        ctx.fillRect(0, rowY, width, GRID_LINE_INTERVAL);
      }

      // Draw grid line
      ctx.strokeStyle = this.GRID_COLOR;
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(0, rowY);
      ctx.lineTo(width, rowY);
      ctx.stroke();
    }
  }

  private getSubdivisionsFromSnapSetting(
    snapSetting: string, 
    beatsPerMeasure: number, 
    pixelsPerMeasure: number,
    pixelsPerBeat: number
  ): { divisionsPerMeasure: number, pixelsPerDivision: number } {
    // 음악적 의미에 맞는 subdivision 계산
    // 1/1 = 온음표 = 4박자
    // 1/2 = 2분음표 = 2박자  
    // 1/4 = 4분음표 = 1박자
    // 1/8 = 8분음표 = 0.5박자
    // 1/16 = 16분음표 = 0.25박자
    // 1/32 = 32분음표 = 0.125박자

    let divisionsPerMeasure = 0;
    let pixelsPerDivision = 0;

    switch (snapSetting) {
      case '1/1':
        // 온음표: 한 마디당 beatsPerMeasure / 4 개의 온음표 (4/4에서는 1개)
        divisionsPerMeasure = beatsPerMeasure / 4;
        if (divisionsPerMeasure < 1) divisionsPerMeasure = 1; // 최소 1개
        pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
        break;
      case '1/2':
        // 2분음표: 한 마디당 beatsPerMeasure / 2 개의 2분음표 (4/4에서는 2개)
        divisionsPerMeasure = beatsPerMeasure / 2;
        pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
        break;
      case '1/4':
        // 4분음표: 한 마디당 beatsPerMeasure 개의 4분음표 (4/4에서는 4개)
        divisionsPerMeasure = beatsPerMeasure;
        pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
        break;
      case '1/8':
        // 8분음표: 한 마디당 beatsPerMeasure * 2 개의 8분음표 (4/4에서는 8개)
        divisionsPerMeasure = beatsPerMeasure * 2;
        pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
        break;
      case '1/16':
        // 16분음표: 한 마디당 beatsPerMeasure * 4 개의 16분음표 (4/4에서는 16개)
        divisionsPerMeasure = beatsPerMeasure * 4;
        pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
        break;
      case '1/32':
        // 32분음표: 한 마디당 beatsPerMeasure * 8 개의 32분음표 (4/4에서는 32개)
        divisionsPerMeasure = beatsPerMeasure * 8;
        pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
        break;
      default:
        // 기본값: 4분음표
        divisionsPerMeasure = beatsPerMeasure;
        pixelsPerDivision = pixelsPerMeasure / divisionsPerMeasure;
    }

    return { divisionsPerMeasure, pixelsPerDivision };
  }
} 