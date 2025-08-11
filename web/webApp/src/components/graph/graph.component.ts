import { Component, ElementRef, Input, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Chart, ChartData, ChartOptions, Point } from 'chart.js';
import 'chartjs-adapter-date-fns';
import zoomPlugin from 'chartjs-plugin-zoom';
import { BaseChartDirective } from 'ng2-charts';
import 'chartjs-adapter-date-fns';

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
  @Input() set drawingMode(value: number) {
    this._drawingMode = value as DrawingMode;
    
    // Clear all lines when switching back to None mode
    if (this._drawingMode === DrawingMode.None) {
      this._horizontalLines = [];
      this._verticalLines = [];
      this.updateLines();
    }
    
    this.updateMouseEvents();
  }
  get drawingMode(): number {
    return this._drawingMode;
  }
  private _drawingMode: DrawingMode = DrawingMode.None;

  private _horizontalLines: number[] = [];
  private _verticalLines: number[] = [];
  private isDrawingMode: boolean = false;
  private marginY: number = 0
  private marginX: number = 0
  private maxY: number = 0
  private minY: number = 0
  private maxX: number = 0
  private minX: number = 0

  @Input() set inputInfo(newValue: any) {
    console.log('Novo info de gráfico recebido:');
    
    // Remove dots from all data datasets by setting pointRadius to 0 and ensure straight lines
    const datasetsWithoutDots = newValue.map((dataset: any) => ({
      ...dataset,
      pointRadius: 2,
      tension: 0 // Force straight lines between points
    }));
    
    this.lineChartData = 
    {
      datasets: datasetsWithoutDots
    }

    this.calculateMargin(datasetsWithoutDots)

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
            second:     'HH:mm:ss',
            minute:     'HH:mm',
            hour:       'HH:mm',
            day:        'dd/MM',
            week:       'dd/MM',
            month:      'MMM yyyy',
            quarter:    '[Q]Q - yyyy',
            year:       'yyyy',
          },
          tooltipFormat: 'MMM dd, HH:mm', 
        },
        ticks: {
          source: 'auto',
        },
        title: {
          display: true,
          text: 'Tempo',
          
        },
        min: undefined,
        max: undefined
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
    parsing: false,
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
            if(this.zoomEnabled)
            {
              chart.options.plugins!.zoom!.zoom!.drag!.enabled = true;
              chart.options.plugins!.zoom!.pan!.enabled = false;
            }
            else
            {
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
            if(this.zoomEnabled)
            {
              chart.options.plugins!.zoom!.zoom!.drag!.enabled = true;
              chart.options.plugins!.zoom!.pan!.enabled = false;
            }
            else
            {
              chart.options.plugins!.zoom!.zoom!.drag!.enabled = false;
              chart.options.plugins!.zoom!.pan!.enabled = true;
            }
            return true
          }
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
  }

  setupMouseEvents() {
    // Wait for chart to be ready
    setTimeout(() => {
      if (this.chart?.chart) {
        const canvas = this.chart.chart.canvas;
        
        // Remove existing listeners to avoid duplicates
        canvas.removeEventListener('click', this.handleCanvasClick.bind(this));
        canvas.removeEventListener('mousemove', this.handleMouseMove.bind(this));
        
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
      }
    }, 100);
  }

  handleCanvasClick(event: MouseEvent) {
    if (!this.chart?.chart) return;

    const rect = this.chart.chart.canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Convert pixel coordinates to chart coordinates
    const chartArea = this.chart.chart.chartArea;
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
    // Optional: Add visual feedback when hovering in drawing mode
    if (this._drawingMode !== DrawingMode.None && this.chart?.chart?.canvas) {
      this.chart.chart.canvas.style.cursor = 'crosshair';
    } else if (this.chart?.chart?.canvas) {
      this.chart.chart.canvas.style.cursor = 'default';
    }
  }

  addHorizontalLine(yValue: number) {
    // Round to 2 decimal places for cleaner display
    const roundedValue = Math.round(yValue * 100) / 100;
    
    // Clear existing lines and add the new one
    this._horizontalLines = [roundedValue];
    this.updateLines();
    console.log(`Placed horizontal line at Y = ${roundedValue}`);
  }

  addVerticalLine(xValue: number) {
    // Round to 2 decimal places for cleaner display
    const roundedValue = Math.round(xValue * 100) / 100;
    
    // Clear existing lines and add the new one
    this._verticalLines = [roundedValue];
    this.updateLines();
    console.log(`Placed vertical line at X = ${roundedValue}`);
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
      
      // Force chart update to apply zoom changes
      if (this.chart?.chart) {
        this.lineChartOptions = { ...this.lineChartOptions };
        setTimeout(() => {
          if (this.chart?.chart) {
            this.chart.chart.update('none');
          }
        }, 0);
      }
    }
  }

  calculateMargin(linesInfos: any)
  {
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
      if(this.lineChartOptions.scales && 
         this.lineChartOptions.scales['y'] &&
         this.lineChartOptions.scales['x'])
      {
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
    
    // Add horizontal lines as additional datasets
    const horizontalLineDatasets = this._horizontalLines.map((yValue, index) => ({
      label: `Linha Horizontal ${yValue}`,
      data: this.lineChartData.datasets[0]?.data?.map((point: any) => ({
        x: point.x,
        y: yValue
      })) || [],
      borderColor: 'rgba(255, 0, 0, 0.8)',
      backgroundColor: 'rgba(255, 0, 0, 0.1)',
      borderWidth: 2,
      borderDash: [5, 5],
      fill: false,
      pointRadius: 0,
      tension: 0
    }));

    // Add vertical lines as additional datasets
    const verticalLineDatasets = this._verticalLines.map((xValue, index) => ({
      label: `Linha Vertical ${ new Date(xValue).toLocaleString('pt-BR', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
      }) }`,
      data: [
        { x: xValue, y: this.minY },
        { x: xValue, y: this.maxY }
      ],
      borderColor: 'rgba(255, 0, 0, 0.8)',
      backgroundColor: 'rgba(255, 0, 0, 0.1)',
      borderWidth: 2,
      borderDash: [5, 5],
      fill: false,
      pointRadius: 0,
      tension: 0
    }));

    // Combine original datasets with line datasets
    const originalDatasets = this.lineChartData.datasets.filter(dataset => 
      !dataset.label?.startsWith('Linha Horizontal') && !dataset.label?.startsWith('Linha Vertical')
    );
    
    this.lineChartData = {
      datasets: [...originalDatasets, ...horizontalLineDatasets, ...verticalLineDatasets]
    };

    // Force chart update
    if (this.chart?.chart) {
      setTimeout(() => {
        if (this.chart?.chart) {
          this.chart.chart.update('none');
        }
      }, 0);
    }
  }
}
