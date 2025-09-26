import { Component, ElementRef, Input, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Chart, ChartData, ChartOptions, Point } from 'chart.js';
import 'chartjs-adapter-date-fns';
import zoomPlugin from 'chartjs-plugin-zoom';
import annotationPlugin from 'chartjs-plugin-annotation';
import { BaseChartDirective } from 'ng2-charts';
import 'chartjs-adapter-date-fns';

// Register the annotation plugin
Chart.register(annotationPlugin);

export enum DrawingMode {
  None = 0,
  Horizontal = 1,
  Vertical = 2,
  Both = 3
}

@Component({
  selector: 'graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss'],
  imports: [CommonModule, BaseChartDirective],
  standalone: true
})
export class GraphComponent {
  @ViewChild(BaseChartDirective) chart?: BaseChartDirective;

  @Input() blockFitAll: boolean = false

  @Input() set resize(trigger: boolean) {
    this.fitAllGraph()
  }
  @Input() zoomEnabled: boolean = true
  @Input() set selectedDataLineIndex(value: number) {
    this._selectedDataLineIndex = value;
    this.updateLines();
  }
  get selectedDataLineIndex(): number {
    return this._selectedDataLineIndex;
  }

  @Input() set clearLines(value: boolean) {
    this.clearAllLines();
  }

  @Input() set drawingMode(value: number) {
    this._drawingMode = value as DrawingMode;

    // Limpar posição temporária quando o modo de desenho muda
    this._tempMousePosition = { x: null, y: null };
    this._isMouseOverChart = false;

    this.updateLines();
    this.updateMouseEvents();
  }
  get drawingMode(): number {
    return this._drawingMode;
  }
  private _drawingMode: DrawingMode = DrawingMode.None;

  private _horizontalLines: number[] = [];
  private _verticalLines: number[] = [];
  private isDrawingMode: boolean = false;
  private _minMaxPoints: { min: { x: number, y: number } | null, max: { x: number, y: number } | null } = { min: null, max: null };
  private _selectedDataLineIndex: number = -1;
  
  // Propriedades para linha temporária que segue o mouse
  private _tempMousePosition: { x: number | null, y: number | null } = { x: null, y: null };
  private _isMouseOverChart: boolean = false;
  private marginY: number = 0
  private marginX: number = 0
  private maxY: number = 0
  private minY: number = 0
  private maxX: number = 0
  private minX: number = 0

  @Input() set inputInfo(newValue: any) {
    console.log('Novo info de gráfico recebido:');

    // Configure datasets with proper point settings
    const datasetsWithPoints = newValue.map((dataset: any) => ({
      ...dataset,
      pointRadius: 2,
      pointHoverRadius: 4,
      pointBorderWidth: 1,
      pointBorderColor: 'transparent',
      tension: 0 // Force straight lines between points
    }));

    this.lineChartData =
    {
      datasets: datasetsWithPoints
    }

    this.calculateMargin(datasetsWithPoints)

    this.updateZoomLimits()
    this.fitAllGraph()
    this.updateLines()
  }

  lineChartOptions: ChartOptions<'line'> = {
    responsive: true,
    animation: false,
    maintainAspectRatio: false,
    elements: {
      line: {
        tension: 0 // Disable curve interpolation - straight lines between points
      }
    },
    scales: {
      x: {
        type: 'time',
        time: {
          displayFormats: {
            millisecond: 'HH:mm:ss.SSS',
            second: 'HH:mm:ss',
            minute: 'HH:mm',
            hour: 'HH:mm',
            day: 'dd/MM',
            week: 'dd/MM',
            month: 'MMM yyyy',
            quarter: '[Q]Q - yyyy',
            year: 'yyyy',
          },
          tooltipFormat: 'MMM dd, HH:mm'
        },
        ticks: {
          source: 'auto',
        },
        title: {
          display: true,
          text: 'Tempo',

        },
        min: undefined,
        max: undefined,
        // Adicionar configurações para melhor renderização durante zoom
        grid: {
          display: true,
          drawOnChartArea: true,
          drawTicks: true
        }
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Valor',
        },
        min: undefined,
        max: undefined
      },
    },
    plugins: {
      decimation: {
        enabled: true,
        algorithm: 'lttb', // 'lttb' (Largest Triangle Three Buckets) is preferred for line charts
        samples: 1000,     // You can tweak this (e.g., 1000–5000)
        threshold: 1000   // Enable decimation only if points > threshold
      },
      legend: {
        position: 'bottom',
        display: true,
        labels: {
          boxWidth: 12
        }
      },
      tooltip: {
        enabled: true,
        mode: 'nearest',
        intersect: true,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: 'rgba(0, 0, 0, 0.8)',
        bodyColor: 'rgba(0, 0, 0, 0.8)',
        borderWidth: 2,
        cornerRadius: 6,
        displayColors: false,
        callbacks: {
          title: (context) => {
            const date = new Date(context[0].parsed.x);
            return date.toLocaleString('pt-BR', {
              day: '2-digit',
              month: '2-digit',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit'
            });
          },
          label: (context) => {
            const value = context.parsed.y;
            return `${context.dataset.label}: ${value}`;
          }
        }
      },
      annotation: {
        annotations: {}
      },
      zoom: {
        zoom: {
          wheel: { enabled: true, speed: 0.1 },
          pinch: { enabled: true },
          mode: 'xy',
          onZoomStart: ({ chart, event }) => {
            const mouseEvent = event as MouseEvent;

            if (mouseEvent.ctrlKey) {
              chart.options.plugins!.zoom!.zoom!.mode = 'x';
            } else if (mouseEvent.shiftKey) {
              chart.options.plugins!.zoom!.zoom!.mode = 'y';
            } else {
              chart.options.plugins!.zoom!.zoom!.mode = 'xy';
            }
            if (this.zoomEnabled) {
              chart.options.plugins!.zoom!.zoom!.drag!.enabled = true;
              chart.options.plugins!.zoom!.pan!.enabled = false;
            }
            else {
              chart.options.plugins!.zoom!.zoom!.drag!.enabled = false;
              chart.options.plugins!.zoom!.pan!.enabled = true;
            }

            return true
          },
          drag: {
            enabled: true,
            backgroundColor: 'rgba(0,123,255,0.25)',
            borderColor: 'rgba(0,123,255,0.8)',
            borderWidth: 1
          },
        },
        pan: {
          enabled: false,
          mode: 'xy',
          onPanStart: ({ chart, event }) => {
            if (this.zoomEnabled) {
              chart.options.plugins!.zoom!.zoom!.drag!.enabled = true;
              chart.options.plugins!.zoom!.pan!.enabled = false;
            }
            else {
              chart.options.plugins!.zoom!.zoom!.drag!.enabled = false;
              chart.options.plugins!.zoom!.pan!.enabled = true;
            }
            return true
          }
        },
        limits: {
          x: {
            min: 0,
            max: 0,
          },
          y: {
            min: 0,
            max: 0,
          },
        },
      },
    },
  };

  public lineChartData: ChartData<'line'> = {
    datasets: [

    ]
  };
  filteredData: Array<{ name: string, series: Array<any> }> = [];

  constructor() { }

  ngAfterViewInit() {
    this.setupMouseEvents();
    this.setupZoomEvents();
  }

  setupZoomEvents() {
    // Aguardar o gráfico estar pronto
    setTimeout(() => {
      if (this.chart?.chart) {
        const chart = this.chart.chart;

        // Adicionar listener para eventos de zoom com throttling
        let zoomTimeout: any;
        chart.canvas.addEventListener('wheel', () => {
          clearTimeout(zoomTimeout);
          zoomTimeout = setTimeout(() => {
            this.forceChartUpdate();
          }, 200);
        });
      }
    }, 200);
  }

  private forceChartUpdate() {
    if (this.chart?.chart) {
      // Forçar atualização completa do gráfico
      this.chart.chart.update('none');

      // Re-aplicar as anotações se existirem
      if (this._horizontalLines.length > 0 || this._verticalLines.length > 0) {
        this.updateLines();
      }
    }
  }

  setupMouseEvents() {
    // Wait for chart to be ready
    setTimeout(() => {
      if (this.chart?.chart) {
        const canvas = this.chart.chart.canvas;

        // Remove existing listeners to avoid duplicates
        canvas.removeEventListener('click', this.handleCanvasClick.bind(this));
        canvas.removeEventListener('mousemove', this.handleMouseMove.bind(this));
        canvas.removeEventListener('mouseenter', this.handleMouseEnter.bind(this));
        canvas.removeEventListener('mouseleave', this.handleMouseLeave.bind(this));

        // Add new listeners
        canvas.addEventListener('click', (event) => {
          if (this._drawingMode !== DrawingMode.None) {
            this.handleCanvasClick(event);
          }
        });

        canvas.addEventListener('mousemove', (event) => {
          if (this._drawingMode !== DrawingMode.None) {
            this.handleMouseMove(event);
          }
        });

        canvas.addEventListener('mouseenter', (event) => {
          if (this._drawingMode !== DrawingMode.None) {
            this.handleMouseEnter(event);
          }
        });

        canvas.addEventListener('mouseleave', (event) => {
          if (this._drawingMode !== DrawingMode.None) {
            this.handleMouseLeave(event);
          }
        });
      }
    }, 100);
  }

  handleCanvasClick(event: MouseEvent) {
    if (!this.chart?.chart) return;

    // Se temos posição temporária do mouse, usar ela para fixar a linha
    if (this._tempMousePosition.x !== null || this._tempMousePosition.y !== null) {
      if (this._drawingMode === DrawingMode.Horizontal && this._tempMousePosition.y !== null) {
        this.addHorizontalLine(this._tempMousePosition.y);
      } else if (this._drawingMode === DrawingMode.Vertical && this._tempMousePosition.x !== null) {
        this.addVerticalLine(this._tempMousePosition.x);
      } else if (this._drawingMode === DrawingMode.Both) {
        if (this._tempMousePosition.y !== null) {
          this.addHorizontalLine(this._tempMousePosition.y);
        }
        if (this._tempMousePosition.x !== null) {
          this.addVerticalLine(this._tempMousePosition.x);
        }
      }
      
      // Limpar posição temporária após fixar
      this._tempMousePosition = { x: null, y: null };
      return;
    }

    // Fallback para o comportamento original se não houver posição temporária
    const rect = this.chart.chart.canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Convert pixel coordinates to chart coordinates
    const yScale = this.chart.chart.scales['y'];
    const xScale = this.chart.chart.scales['x'];

    const yValue = yScale.getValueForPixel(y);
    const xValue = xScale.getValueForPixel(x);

    if (this._drawingMode === DrawingMode.Horizontal) {
      if (yValue !== null && yValue !== undefined && !isNaN(yValue)) {
        this.addHorizontalLine(Number(yValue));
      }
    } else if (this._drawingMode === DrawingMode.Vertical) {
      if (xValue !== null && xValue !== undefined && !isNaN(xValue)) {
        this.addVerticalLine(Number(xValue));
      }
    } else if (this._drawingMode === DrawingMode.Both) {
      // First add horizontal line
      if (yValue !== null && yValue !== undefined && !isNaN(yValue)) {
        this.addHorizontalLine(Number(yValue));
      }
      // Then add vertical line
      if (xValue !== null && xValue !== undefined && !isNaN(xValue)) {
        this.addVerticalLine(Number(xValue));
      }
    }
  }

  handleMouseMove(event: MouseEvent) {
    if (!this.chart?.chart) return;

    // Optional: Add visual feedback when hovering in drawing mode
    if (this._drawingMode !== DrawingMode.None && this.chart?.chart?.canvas) {
      this.chart.chart.canvas.style.cursor = 'crosshair';
    } else if (this.chart?.chart?.canvas) {
      this.chart.chart.canvas.style.cursor = 'default';
    }

    // Atualizar posição da linha temporária se estiver no modo de desenho
    if (this._drawingMode !== DrawingMode.None && this._isMouseOverChart) {
      const rect = this.chart.chart.canvas.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      // Convert pixel coordinates to chart coordinates
      const yScale = this.chart.chart.scales['y'];
      const xScale = this.chart.chart.scales['x'];

      const yValue = yScale.getValueForPixel(y);
      const xValue = xScale.getValueForPixel(x);

      // Atualizar posição temporária baseada no modo de desenho
      if (this._drawingMode === DrawingMode.Horizontal || this._drawingMode === DrawingMode.Both) {
        this._tempMousePosition.y = (yValue !== null && yValue !== undefined && !isNaN(yValue)) ? Number(yValue) : null;
      }
      
      if (this._drawingMode === DrawingMode.Vertical || this._drawingMode === DrawingMode.Both) {
        this._tempMousePosition.x = (xValue !== null && xValue !== undefined && !isNaN(xValue)) ? Number(xValue) : null;
      }

      // Atualizar as linhas para mostrar a linha temporária
      this.updateLines();
    }
  }

  handleMouseEnter(event: MouseEvent) {
    this._isMouseOverChart = true;
  }

  handleMouseLeave(event: MouseEvent) {
    this._isMouseOverChart = false;
    // Limpar posição temporária quando o mouse sai do gráfico
    this._tempMousePosition = { x: null, y: null };
    this.updateLines();
  }

  addHorizontalLine(yValue: number) {
    // Round to 2 decimal places for cleaner display
    const roundedValue = Math.round(yValue * 100) / 100;

    // Add the new line if it doesn't already exist
    if (!this._horizontalLines.includes(roundedValue)) {
      this._horizontalLines.push(roundedValue);
      this.updateLines();
      console.log(`Added horizontal line at Y = ${roundedValue}`);
    } else {
      console.log(`Horizontal line at Y = ${roundedValue} already exists`);
    }
  }

  addVerticalLine(xValue: number) {
    // Round to 2 decimal places for cleaner display
    const roundedValue = Math.round(xValue * 100) / 100;

    // Add the new line if it doesn't already exist
    if (!this._verticalLines.includes(roundedValue)) {
      this._verticalLines.push(roundedValue);
      this.updateLines();
      console.log(`Added vertical line at X = ${roundedValue}`);
    } else {
      console.log(`Vertical line at X = ${roundedValue} already exists`);
    }
  }

  removeHorizontalLine(yValue: number) {
    const index = this._horizontalLines.indexOf(yValue);
    if (index > -1) {
      this._horizontalLines.splice(index, 1);
      this.updateLines();
      console.log(`Removed horizontal line at Y = ${yValue}`);
    }
  }

  clearAllHorizontalLines() {
    this._horizontalLines = [];
    this.updateLines();
    console.log('Cleared all horizontal lines');
  }

  clearAllVerticalLines() {
    this._verticalLines = [];
    this.updateLines();
    console.log('Cleared all vertical lines');
  }

  clearAllLines() {
    this._horizontalLines = [];
    this._verticalLines = [];
    this.updateLines();
    console.log('Cleared all lines');
  }

  updateMouseEvents() {
    if (this.chart?.chart?.canvas) {
      const canvas = this.chart.chart.canvas;

      if (this._drawingMode !== DrawingMode.None) {
        canvas.style.cursor = 'crosshair';
        // Disable zoom when drawing mode is on
        if (this.lineChartOptions.plugins?.zoom) {
          this.lineChartOptions.plugins.zoom.zoom!.wheel!.enabled = false;
          this.lineChartOptions.plugins.zoom.zoom!.pinch!.enabled = false;
          this.lineChartOptions.plugins.zoom.zoom!.drag!.enabled = false;
          this.lineChartOptions.plugins.zoom.pan!.enabled = false;
        }
      } else {
        canvas.style.cursor = 'default';
        // Re-enable zoom when drawing mode is off
        if (this.lineChartOptions.plugins?.zoom) {
          this.lineChartOptions.plugins.zoom.zoom!.wheel!.enabled = true;
          this.lineChartOptions.plugins.zoom.zoom!.pinch!.enabled = true;
          this.lineChartOptions.plugins.zoom.zoom!.drag!.enabled = this.zoomEnabled;
          this.lineChartOptions.plugins.zoom.pan!.enabled = !this.zoomEnabled;
        }
      }

      // Update chart without resetting zoom by only updating the zoom plugin
      if (this.chart?.chart) {
        // Update the chart's zoom plugin options directly without recreating the entire options object
        const chart = this.chart.chart;
        if (chart.options.plugins?.zoom) {
          chart.options.plugins.zoom.zoom!.wheel!.enabled = this._drawingMode === DrawingMode.None;
          chart.options.plugins.zoom.zoom!.pinch!.enabled = this._drawingMode === DrawingMode.None;
          chart.options.plugins.zoom.zoom!.drag!.enabled = this._drawingMode === DrawingMode.None ? this.zoomEnabled : false;
          chart.options.plugins.zoom.pan!.enabled = this._drawingMode === DrawingMode.None ? !this.zoomEnabled : false;
        }

        // Update without animation to preserve zoom
        chart.update('none');
      }
    }
  }

  calculateMargin(linesInfos: any) {
    let minYaxis = Number.MAX_SAFE_INTEGER
    let maxYaxis = Number.MIN_SAFE_INTEGER

    let minXaxis = new Date(8640000000000000).getTime();
    let maxXaxis = new Date(-8640000000000000).getTime()
    for (var infos of linesInfos) {
      for (let info of infos.data) {
        let point: Point = <any>(info)
        let dt = point.x;
        let value = point.y

        if (minXaxis > dt) {
          minXaxis = dt
        }
        if (maxXaxis < dt) {
          maxXaxis = dt
        }

        if (minYaxis > value) {
          minYaxis = value
        }
        if (maxYaxis < value) {
          maxYaxis = value
        }


      }
    }

    this.marginY = (maxYaxis - minYaxis) * 0.2
    this.maxY = maxYaxis + this.marginY
    this.minY = minYaxis - this.marginY
    this.maxX = maxXaxis
    this.minX = minXaxis
  }

  fitAllGraph() {
    if (this.lineChartData && !this.blockFitAll) {
      if (this.lineChartOptions.scales &&
        this.lineChartOptions.scales['y'] &&
        this.lineChartOptions.scales['x']) {
        this.lineChartOptions.scales['y'].max = this.maxY
        this.lineChartOptions.scales['y'].min = this.minY

        if (this.marginY === 0) {
          this.lineChartOptions.scales['y'].max += 1
          this.lineChartOptions.scales['y'].min -= 1
        }

        this.lineChartOptions.scales['x'].max = new Date(this.maxX).getTime()
        this.lineChartOptions.scales['x'].min = new Date(this.minX).getTime()
      }

    }

    this.updateZoomLimits();
    this.chart?.chart?.resetZoom();

    // Force chart update to apply the new scales
    if (this.chart?.chart) {
      // Trigger change detection by creating a new options object
      this.lineChartOptions = { ...this.lineChartOptions };

      // Use setTimeout to ensure the change detection cycle completes
      setTimeout(() => {
        if (this.chart?.chart) {
          this.chart.chart.update('none'); // 'none' prevents animation during update
        }
      }, 0);
    }

  }

  updateLines() {
    console.log('Updating lines:', { horizontal: this._horizontalLines, vertical: this._verticalLines });

    // Calculate min/max points if enabled
    this.calculateMinMaxPoints();

    // Create annotations object
    const annotations: any = {};

    // Add min/max annotations
    const minMaxAnnotations = this.getMinMaxAnnotations();
    Object.assign(annotations, minMaxAnnotations);

    // Add temporary horizontal line if mouse is over chart and in drawing mode
    if (this._tempMousePosition.y !== null && this._isMouseOverChart && 
        (this._drawingMode === DrawingMode.Horizontal || this._drawingMode === DrawingMode.Both)) {
      annotations['tempHorizontalLine'] = {
        type: 'line',
        yMin: this._tempMousePosition.y,
        yMax: this._tempMousePosition.y,
        borderColor: 'rgba(200, 198, 194, 0.8)', 
        borderWidth: 2,
        borderDash: [3, 3],
        enter: {
          mode: 'immediate',
          animation: {
            duration: 0
          }
        }
      };

      // Add text annotation for temporary horizontal line value
      if (this.chart?.chart) {
        const chart = this.chart.chart;
        const xScale = chart.scales['x'];
        if (xScale) {
          const xValue = xScale.min + (xScale.max - xScale.min) * 0.015; // Grudado no eixo Y
          annotations['tempHorizontalLineText'] = {
            type: 'label',
            xValue: xValue,
            yValue: this._tempMousePosition.y,
            content: `${this._tempMousePosition.y.toFixed(2)}`,
            backgroundColor: 'rgba(200, 198, 194, 0.9)',
            color: 'rgba(0, 0, 0, 0.8)',
            font: {
              size: 11,
              weight: 'bold'
            },
            padding: 3,
            borderRadius: 3,
            borderColor: 'rgba(200, 198, 194, 0.8)',
            borderWidth: 1
          };
        }
      }
    }

    // Add horizontal lines as annotations
    this._horizontalLines.forEach((yValue, index) => {
      annotations[`horizontalLine${index}`] = {
        type: 'line',
        yMin: yValue,
        yMax: yValue,
        borderColor: 'rgba(43, 42, 42, 0.8)',
        borderWidth: 2,
        borderDash: [5, 5],
        enter: {
          mode: 'immediate',
          animation: {
            duration: 0
          }
        }
      };

      // Add text annotation for horizontal line value
      if (this.chart?.chart) {
        const chart = this.chart.chart;
        const xScale = chart.scales['x'];
        if (xScale) {
          const xValue = xScale.min + (xScale.max - xScale.min) * 0.015; // Grudado no eixo Y
          annotations[`horizontalLineText${index}`] = {
            type: 'label',
            xValue: xValue,
            yValue: yValue,
            content: `${yValue}`,
            backgroundColor: 'rgba(186, 183, 178, 0.9)',
            color: 'rgba(0, 0, 0, 0.8)',
            font: {
              size: 11,
              weight: 'bold'
            },
            padding: 3,
            borderRadius: 3,
            borderColor: 'rgba(72, 71, 70, 0.8)',
            borderWidth: 1
          };
        }
      }
    });

    // Add temporary vertical line if mouse is over chart and in drawing mode
    if (this._tempMousePosition.x !== null && this._isMouseOverChart && 
        (this._drawingMode === DrawingMode.Vertical || this._drawingMode === DrawingMode.Both)) {
      annotations['tempVerticalLine'] = {
        type: 'line',
        xMin: this._tempMousePosition.x,
        xMax: this._tempMousePosition.x,
        borderColor: 'rgba(200, 198, 194, 0.8)', // Orange color for temporary line
        borderWidth: 2,
        borderDash: [3, 3]
      };

      // Add text annotation for temporary vertical line value
      if (this.chart?.chart) {
        const chart = this.chart.chart;
        const yScale = chart.scales['y'];
        if (yScale) {
          const yValue = yScale.min + (yScale.max - yScale.min) * 0.015; // Grudado no eixo X
          annotations['tempVerticalLineText'] = {
            type: 'label',
            xValue: this._tempMousePosition.x,
            yValue: yValue,
            content: new Date(this._tempMousePosition.x).toLocaleString('pt-BR', {
              day: '2-digit',
              month: '2-digit',
              hour: '2-digit',
              minute: '2-digit'
            }),
            backgroundColor: 'rgba(200, 198, 194, 0.9)',
            color: 'rgba(0, 0, 0, 0.8)',
            font: {
              size: 11,
              weight: 'bold'
            },
            padding: 3,
            borderRadius: 3,
            borderColor: 'rgba(72, 71, 70, 0.8)',
            borderWidth: 1
          };
        }
      }
    }

    // Add vertical lines as annotations
    this._verticalLines.forEach((xValue, index) => {
      annotations[`verticalLine${index}`] = {
        type: 'line',
        xMin: xValue,
        xMax: xValue,
        borderColor: 'rgba(43, 42, 42, 0.8)',
        borderWidth: 2,
        borderDash: [5, 5]
      };

      // Add text annotation for vertical line value
      if (this.chart?.chart) {
        const chart = this.chart.chart;
        const yScale = chart.scales['y'];
        if (yScale) {
          const yValue = yScale.min + (yScale.max - yScale.min) * 0.015; // Grudado no eixo X
          annotations[`verticalLineText${index}`] = {
            type: 'label',
            xValue: xValue,
            yValue: yValue,
            content: new Date(xValue).toLocaleString('pt-BR', {
              day: '2-digit',
              month: '2-digit',
              hour: '2-digit',
              minute: '2-digit'
            }),
            backgroundColor: 'rgba(186, 183, 178, 0.9)',
            color: 'rgba(0, 0, 0, 0.8)',
            font: {
              size: 11,
              weight: 'bold'
            },
            padding: 3,
            borderRadius: 3,
            borderColor: 'rgba(72, 71, 70, 0.8)',
            borderWidth: 1
          };
        }
      }
    });

    // Update only the annotation plugin without recreating the entire options object
    if (this.chart?.chart) {
      const chart = this.chart.chart;

      // Update only the annotation plugin in the existing options
      if (this.lineChartOptions.plugins) {
        this.lineChartOptions.plugins.annotation = {
          annotations: annotations
        };
      }

      // Update the chart's annotation plugin directly
      if (chart.options.plugins) {
        chart.options.plugins.annotation = {
          annotations: annotations
        };
      }

      // Update without animation to preserve zoom
      chart.update('none');
    }
  }

  private calculateMinMaxPoints(): void {
    if (this.selectedDataLineIndex < 0 || !this.lineChartData?.datasets) {
      this._minMaxPoints = { min: null, max: null };
      return;
    }

    const selectedDataset = this.lineChartData.datasets[this.selectedDataLineIndex];
    if (!selectedDataset || !selectedDataset.data || selectedDataset.data.length === 0) {
      this._minMaxPoints = { min: null, max: null };
      return;
    }

    let minPoint: { x: number, y: number } | null = null;
    let maxPoint: { x: number, y: number } | null = null;

    // Find min and max points
    selectedDataset.data.forEach((point: any) => {
      if (point && typeof point.x === 'number' && typeof point.y === 'number') {
        if (!minPoint || point.y < minPoint.y) {
          minPoint = { x: point.x, y: point.y };
        }
        if (!maxPoint || point.y > maxPoint.y) {
          maxPoint = { x: point.x, y: point.y };
        }
      }
    });

    this._minMaxPoints = { min: minPoint, max: maxPoint };
  }

  private updateZoomLimits(): void {
    if (this.lineChartOptions.plugins?.zoom?.limits) {
      this.lineChartOptions.plugins.zoom.limits['x']!.min = this.minX;
      this.lineChartOptions.plugins.zoom.limits['x']!.max = this.maxX;
      this.lineChartOptions.plugins.zoom.limits['y']!.min = this.minY;
      this.lineChartOptions.plugins.zoom.limits['y']!.max = this.maxY;
    }
  }

  private getMinMaxAnnotations(): any {
    const annotations: any = {};

    if (this._minMaxPoints.min) {
      // Min point annotation
      annotations['minPoint'] = {
        type: 'point',
        xValue: this._minMaxPoints.min.x,
        yValue: this._minMaxPoints.min.y,
        backgroundColor: 'rgba(0, 255, 0, 0.8)',
        borderColor: 'rgba(0, 255, 0, 1)',
        borderWidth: 3,
        radius: 6,
        label: {
          content: `MIN: ${this._minMaxPoints.min.y.toFixed(2)}`,
          enabled: true,
          position: 'bottom',
          backgroundColor: 'rgba(0, 255, 0, 0.9)',
          color: 'rgba(0, 0, 0, 0.8)',
          font: {
            size: 11,
            weight: 'bold'
          },
          padding: 4,
          borderRadius: 4
        }
      };

      // Min point vertical line
      annotations['minVerticalLine'] = {
        type: 'line',
        xMin: this._minMaxPoints.min.x,
        xMax: this._minMaxPoints.min.x,
        borderColor: 'rgba(0, 255, 0, 0.6)',
        borderWidth: 2,
        borderDash: [3, 3]
      };
    }

    if (this._minMaxPoints.max) {
      // Max point annotation
      annotations['maxPoint'] = {
        type: 'point',
        xValue: this._minMaxPoints.max.x,
        yValue: this._minMaxPoints.max.y,
        backgroundColor: 'rgba(255, 0, 0, 0.8)',
        borderColor: 'rgba(255, 0, 0, 1)',
        borderWidth: 3,
        radius: 6,
        label: {
          content: `MAX: ${this._minMaxPoints.max.y.toFixed(2)}`,
          enabled: true,
          position: 'top',
          backgroundColor: 'rgba(255, 0, 0, 0.9)',
          color: 'rgba(0, 0, 0, 0.8)',
          font: {
            size: 11,
            weight: 'bold'
          },
          padding: 4,
          borderRadius: 4
        }
      };

      // Max point vertical line
      annotations['maxVerticalLine'] = {
        type: 'line',
        xMin: this._minMaxPoints.max.x,
        xMax: this._minMaxPoints.max.x,
        borderColor: 'rgba(255, 0, 0, 0.6)',
        borderWidth: 2,
        borderDash: [3, 3]
      };
    }

    return annotations;
  }
}
