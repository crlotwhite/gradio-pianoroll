/**
 * LineLayer - Renders line data for pitch curves, loudness, voice/unvoice, etc.
 */

import { BaseLayer, LayerZIndex } from '../LayerSystem';
import type { LayerRenderContext } from '../../types/layer';
import type { LineDataPoint, LineLayerConfig } from '../../types/layer';

export class LineLayer extends BaseLayer {
  private data: LineDataPoint[] = [];
  private config: LineLayerConfig;
  private readonly DEFAULT_COLOR = '#FF6B6B';

  constructor(config: LineLayerConfig) {
    super(config.name, LayerZIndex.LINES);

    // Set default values for optional properties
    this.config = {
      height: undefined,  // Will be calculated based on canvas height
      position: 'center',
      renderMode: 'default',
      visible: true,
      opacity: 1.0,
      ...config,
      lineWidth: config.lineWidth || 2  // Set default lineWidth if not provided
    };

    // Set layer properties from config
    this.setVisible(this.config.visible || true);
    this.setOpacity(this.config.opacity || 1.0);
  }

  // Set line data
  setData(data: LineDataPoint[]): void {
    this.data = data || [];
  }

  // Get current data
  getData(): LineDataPoint[] {
    return this.data;
  }

  // Update configuration
  updateConfig(newConfig: Partial<LineLayerConfig>): void {
    this.config = { ...this.config, ...newConfig };

    // Update layer properties if they were changed
    if (newConfig.visible !== undefined) {
      this.setVisible(newConfig.visible);
    }
    if (newConfig.opacity !== undefined) {
      this.setOpacity(newConfig.opacity);
    }
  }

  // Get current configuration
  getConfig(): LineLayerConfig {
    return { ...this.config };
  }

  render(context: LayerRenderContext): void {
    if (!this.data || this.data.length === 0) {
      return;
    }

    const { ctx, width, height, horizontalScroll, verticalScroll } = context;

    // Check for special rendering modes
    if (this.config.renderMode === 'piano_grid') {
      this.renderPianoGridMode(context);
      return;
    }

    if (this.config.renderMode === 'independent_range') {
      this.renderIndependentRangeMode(context);
      return;
    }

    // Default rendering mode - use full canvas area, ignore vertical scroll
    this.renderDefaultMode(context);
  }

  private renderPianoGridMode(context: LayerRenderContext): void {
    /**
     * Piano Grid Mode: F0 곡선이 피아노롤 그리드와 정확히 정렬되어 렌더링
     * 수직 스크롤에 따라 이동하고, Y 좌표가 피아노롤 좌표계와 정확히 맞춤
     */
    const { ctx, width, height, horizontalScroll, verticalScroll } = context;

    // Save current context state
    ctx.save();

    // No clipping - use full canvas area
    // Set line style
    ctx.strokeStyle = this.config.color || this.DEFAULT_COLOR;
    ctx.lineWidth = this.config.lineWidth;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.globalAlpha = this.getOpacity();

    if (this.data.length < 2) {
      ctx.restore();
      return;
    }

    ctx.beginPath();
    let hasStarted = false;

    // Sort data by x coordinate for proper line drawing
    const sortedData = [...this.data].sort((a, b) => a.x - b.x);

    for (const point of sortedData) {
      const screenX = point.x - horizontalScroll;

      // Skip points that are off-screen (with some buffer)
      if (screenX < -50 || screenX > width + 50) continue;

      // Apply vertical scroll to Y coordinate (F0 follows piano grid)
      const screenY = point.y - verticalScroll;

      // Skip if Y coordinate is outside canvas bounds (with buffer)
      if (screenY < -50 || screenY > height + 50) continue;

      if (!hasStarted) {
        ctx.moveTo(screenX, screenY);
        hasStarted = true;
      } else {
        ctx.lineTo(screenX, screenY);
      }
    }

    if (hasStarted) {
      ctx.stroke();
    }

    // Draw small circles at data points for better visibility
    if (this.config.lineWidth >= 2) {
      ctx.fillStyle = this.config.color || this.DEFAULT_COLOR;
      const pointRadius = Math.max(1, this.config.lineWidth / 3);

      for (const point of sortedData) {
        const screenX = point.x - horizontalScroll;
        const screenY = point.y - verticalScroll;

        // Skip points that are off-screen
        if (screenX < -pointRadius || screenX > width + pointRadius) continue;
        if (screenY < -pointRadius || screenY > height + pointRadius) continue;

        ctx.beginPath();
        ctx.arc(screenX, screenY, pointRadius, 0, 2 * Math.PI);
        ctx.fill();
      }
    }

    // Draw legend/info (optional)
    if (this.config.originalRange) {
      this.drawPianoGridLegend(ctx, width, verticalScroll);
    }

    ctx.restore();
  }

  private renderIndependentRangeMode(context: LayerRenderContext): void {
    /**
     * Independent Range Mode: loudness, voice/unvoice 등의 데이터를 전체 캔버스 높이에 고정 표시
     * 수직 스크롤의 영향을 받지 않고, 전체 grid canvas 높이를 사용
     */
    const { ctx, width, height, horizontalScroll } = context;

    // Use full canvas area (entire grid height)
    const renderHeight = height;
    const renderTop = 0;

    // Save current context state
    ctx.save();

    // Set clipping region to full canvas
    ctx.beginPath();
    ctx.rect(0, renderTop, width, renderHeight);
    ctx.clip();

    // Draw subtle background with higher opacity for better visibility
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, renderTop, width, renderHeight);

    // Draw grid lines for reference
    this.drawGrid(ctx, width, renderHeight, renderTop);

    // Draw the line (ignore vertical scroll)
    this.drawLineIndependentRangeMode(ctx, width, renderHeight, renderTop, horizontalScroll);

    // Draw enhanced labels for independent range mode
    this.drawIndependentRangeLabels(ctx, renderTop, renderHeight);

    // Restore context state
    ctx.restore();
  }

  private renderDefaultMode(context: LayerRenderContext): void {
    /**
     * Default Mode: 비-F0 데이터들을 전체 캔버스 영역에 고정 표시
     * 수직 스크롤의 영향을 받지 않음
     */
    const { ctx, width, height, horizontalScroll } = context;

    // Use full canvas area for overlay mode, otherwise use configured or default height
    const renderHeight = this.config.position === 'overlay' ? height : (this.config.height || height);
    const renderTop = this.calculateRenderTop(height, renderHeight);

    // Save current context state
    ctx.save();

    // Set clipping region to full canvas or specified area
    ctx.beginPath();
    ctx.rect(0, renderTop, width, renderHeight);
    ctx.clip();

    // Draw subtle background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.02)';
    ctx.fillRect(0, renderTop, width, renderHeight);

    // Draw grid lines (optional)
    this.drawGrid(ctx, width, renderHeight, renderTop);

    // Draw the line (ignore vertical scroll)
    this.drawLineDefaultMode(ctx, width, renderHeight, renderTop, horizontalScroll);

    // Draw value labels
    this.drawLabels(ctx, renderTop, renderHeight);

    // Restore context state
    ctx.restore();
  }

  private drawPianoGridLegend(ctx: CanvasRenderingContext2D, width: number, verticalScroll: number): void {
    const { originalRange } = this.config;
    if (!originalRange) return;

    // Draw legend in top-right corner, accounting for vertical scroll
    const legendTop = Math.max(10, 10 - verticalScroll);
    const legendHeight = 60;

    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(width - 150, legendTop, 140, legendHeight);

    ctx.fillStyle = this.config.color || this.DEFAULT_COLOR;
    ctx.font = '10px Arial';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';

    const legendX = width - 145;
    let legendY = legendTop + 5;

    ctx.fillText(`${this.config.name}`, legendX, legendY);
    legendY += 12;

    // Safely handle Hz range display
    if (originalRange.minHz !== undefined && originalRange.maxHz !== undefined) {
      const minHz = typeof originalRange.minHz === 'number' ? originalRange.minHz.toFixed(1) : originalRange.minHz;
      const maxHz = typeof originalRange.maxHz === 'number' ? originalRange.maxHz.toFixed(1) : originalRange.maxHz;
      ctx.fillText(`${minHz}Hz - ${maxHz}Hz`, legendX, legendY);
      legendY += 12;
    }

    // Safely handle MIDI range display
    if (originalRange.minMidi !== undefined && originalRange.maxMidi !== undefined) {
      const minMidi = typeof originalRange.minMidi === 'number' ? originalRange.minMidi.toFixed(1) : originalRange.minMidi;
      const maxMidi = typeof originalRange.maxMidi === 'number' ? originalRange.maxMidi.toFixed(1) : originalRange.maxMidi;
      ctx.fillText(`MIDI: ${minMidi} - ${maxMidi}`, legendX, legendY);
      legendY += 12;
    }

    ctx.fillText(`${this.data.length} points`, legendX, legendY);
  }

  private calculateRenderTop(canvasHeight: number, renderHeight: number): number {
    switch (this.config.position) {
      case 'top':
        return 50; // Leave some space for timeline
      case 'bottom':
        return canvasHeight - renderHeight - 20;
      case 'center':
      default:
        return Math.floor((canvasHeight - renderHeight) / 2);
      case 'overlay':
        return 0; // Full overlay
    }
  }

  private drawGrid(ctx: CanvasRenderingContext2D, width: number, height: number, top: number): void {
    const centerY = top + height / 2;
    const quarterY1 = top + height / 4;
    const quarterY2 = top + (height * 3) / 4;

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 0.5;

    // Horizontal grid lines
    [top, quarterY1, centerY, quarterY2, top + height].forEach(y => {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    });
  }

  private drawLineDefaultMode(ctx: CanvasRenderingContext2D, width: number, height: number, top: number, horizontalScroll: number): void {
    if (this.data.length < 2) return;

    // Set line style
    ctx.strokeStyle = this.config.color || this.DEFAULT_COLOR;
    ctx.lineWidth = this.config.lineWidth;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.globalAlpha = this.getOpacity();

    // Calculate Y range
    const yRange = this.config.yMax - this.config.yMin;

    ctx.beginPath();
    let hasStarted = false;

    // Sort data by x coordinate for proper line drawing
    const sortedData = [...this.data].sort((a, b) => a.x - b.x);

    for (const point of sortedData) {
      const screenX = point.x - horizontalScroll;

      // Skip points that are off-screen (with some buffer)
      if (screenX < -50 || screenX > width + 50) continue;

      // Map Y value to canvas coordinates (inverted: higher values at top)
      const normalizedY = (point.y - this.config.yMin) / yRange;
      const screenY = top + height - (normalizedY * height); // 반전: 높은 값이 위로

      if (!hasStarted) {
        ctx.moveTo(screenX, screenY);
        hasStarted = true;
      } else {
        ctx.lineTo(screenX, screenY);
      }
    }

    if (hasStarted) {
      ctx.stroke();
    }

    // Draw data points (optional, for debugging or emphasis)
    if (this.config.lineWidth >= 3) {
      this.drawDataPointsDefaultMode(ctx, width, height, top, horizontalScroll);
    }
  }

  private drawDataPointsDefaultMode(ctx: CanvasRenderingContext2D, width: number, height: number, top: number, horizontalScroll: number): void {
    const yRange = this.config.yMax - this.config.yMin;
    const pointRadius = Math.max(1, this.config.lineWidth / 2);

    ctx.fillStyle = this.config.color || this.DEFAULT_COLOR;
    ctx.globalAlpha = this.getOpacity();

    for (const point of this.data) {
      const screenX = point.x - horizontalScroll;

      // Skip points that are off-screen
      if (screenX < -pointRadius || screenX > width + pointRadius) continue;

      // Map Y value to canvas coordinates (inverted: higher values at top)
      const normalizedY = (point.y - this.config.yMin) / yRange;
      const screenY = top + height - (normalizedY * height); // 반전: 높은 값이 위로

      ctx.beginPath();
      ctx.arc(screenX, screenY, pointRadius, 0, 2 * Math.PI);
      ctx.fill();
    }
  }

  private drawLineIndependentRangeMode(ctx: CanvasRenderingContext2D, width: number, height: number, top: number, horizontalScroll: number): void {
    if (this.data.length < 2) return;

    // Set line style with higher visibility
    ctx.strokeStyle = this.config.color || this.DEFAULT_COLOR;
    ctx.lineWidth = this.config.lineWidth;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.globalAlpha = this.getOpacity();

    // Calculate Y range
    const yRange = this.config.yMax - this.config.yMin;

    ctx.beginPath();
    let hasStarted = false;

    // Sort data by x coordinate for proper line drawing
    const sortedData = [...this.data].sort((a, b) => a.x - b.x);

    for (const point of sortedData) {
      const screenX = point.x - horizontalScroll;

      // Skip points that are off-screen (with some buffer)
      if (screenX < -50 || screenX > width + 50) continue;

      // Map Y value to canvas coordinates (inverted: higher values at top)
      // Use full height for better visibility
      const normalizedY = (point.y - this.config.yMin) / yRange;
      const screenY = top + height - (normalizedY * height); // 반전: 높은 값이 위로

      if (!hasStarted) {
        ctx.moveTo(screenX, screenY);
        hasStarted = true;
      } else {
        ctx.lineTo(screenX, screenY);
      }
    }

    if (hasStarted) {
      ctx.stroke();
    }

    // Draw data points for better visibility in independent range mode
    this.drawDataPointsIndependentRange(ctx, width, height, top, horizontalScroll);
  }

  private drawDataPointsIndependentRange(ctx: CanvasRenderingContext2D, width: number, height: number, top: number, horizontalScroll: number): void {
    const yRange = this.config.yMax - this.config.yMin;
    const pointRadius = Math.max(1.5, this.config.lineWidth / 2);

    ctx.fillStyle = this.config.color || this.DEFAULT_COLOR;
    ctx.globalAlpha = this.getOpacity() * 0.8;

    for (const point of this.data) {
      const screenX = point.x - horizontalScroll;

      // Skip points that are off-screen
      if (screenX < -pointRadius || screenX > width + pointRadius) continue;

      // Map Y value to canvas coordinates (inverted: higher values at top)
      const normalizedY = (point.y - this.config.yMin) / yRange;
      const screenY = top + height - (normalizedY * height); // 반전: 높은 값이 위로

      ctx.beginPath();
      ctx.arc(screenX, screenY, pointRadius, 0, 2 * Math.PI);
      ctx.fill();
    }
  }

  private drawIndependentRangeLabels(ctx: CanvasRenderingContext2D, top: number, height: number): void {
    // Draw enhanced labels for independent range mode
    ctx.fillStyle = this.config.color || this.DEFAULT_COLOR;
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';

    // Layer name with data type
    const layerTitle = this.config.dataType ?
      `${this.config.name} (${this.config.dataType})` :
      this.config.name;
    ctx.fillText(layerTitle, 10, top + 10);

    // Value range with unit
    ctx.font = '10px Arial';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    const unit = this.config.unit || '';

    // Show original range if available
    if (this.config.originalRange) {
      const { originalRange } = this.config;

      if (originalRange.min !== undefined && originalRange.max !== undefined) {
        ctx.fillText(`${originalRange.max.toFixed(2)}${unit}`, 10, top + 30);
        ctx.fillText(`${originalRange.min.toFixed(2)}${unit}`, 10, top + height - 20);
      } else {
        ctx.fillText(`${this.config.yMax.toFixed(1)}`, 10, top + 30);
        ctx.fillText(`${this.config.yMin.toFixed(1)}`, 10, top + height - 20);
      }

      // Show additional info for voice/unvoice data
      if (originalRange.voiced_ratio !== undefined) {
        ctx.fillText(`Voiced: ${(originalRange.voiced_ratio * 100).toFixed(1)}%`, 10, top + height - 40);
      }
    } else {
      ctx.fillText(`${this.config.yMax.toFixed(1)}${unit}`, 10, top + 30);
      ctx.fillText(`${this.config.yMin.toFixed(1)}${unit}`, 10, top + height - 20);
    }

    // Data points count
    ctx.fillText(`${this.data.length} points`, 10, top + height - 5);
  }

  private drawLabels(ctx: CanvasRenderingContext2D, top: number, height: number): void {
    // Draw layer name and value range
    ctx.fillStyle = this.config.color || this.DEFAULT_COLOR;
    ctx.font = '10px Arial';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';

    // Layer name
    ctx.fillText(this.config.name, 5, top + 2);

    // Value range
    ctx.font = '8px Arial';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.fillText(`${this.config.yMax.toFixed(1)}`, 5, top + 15);
    ctx.fillText(`${this.config.yMin.toFixed(1)}`, 5, top + height - 10);
  }

  // Utility methods
  hasData(): boolean {
    return this.data && this.data.length > 0;
  }

  getValueAtX(x: number): number | null {
    if (!this.data || this.data.length === 0) return null;

    // Find closest data point
    let closest = this.data[0];
    let minDistance = Math.abs(closest.x - x);

    for (const point of this.data) {
      const distance = Math.abs(point.x - x);
      if (distance < minDistance) {
        minDistance = distance;
        closest = point;
      }
    }

    return closest.y;
  }

  getDataInRange(xStart: number, xEnd: number): LineDataPoint[] {
    return this.data.filter(point => point.x >= xStart && point.x <= xEnd);
  }
}