import { Component, ElementRef, Input, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ChartData, ChartOptions, Point } from 'chart.js';
import 'chartjs-adapter-date-fns';
import zoomPlugin from 'chartjs-plugin-zoom';
import { BaseChartDirective } from 'ng2-charts';
import 'chartjs-adapter-date-fns';

@Component({
  selector: 'graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss'],
  imports: [CommonModule, BaseChartDirective],
  standalone: true
})
export class GraphComponent {
  @ViewChild(BaseChartDirective) chart?: BaseChartDirective;

  lineChartOptions: ChartOptions<'line'> = {
    responsive: true,
    animation: false,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: 'time',
        title: {
          display: true,
          text: 'Time',
        },
        min: undefined,
        max: undefined
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Value',
        },
        min: undefined,
        max: undefined
      },
    },
    plugins: {
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

            return true
          }
        },
        pan: {
          enabled: true,
          mode: 'x', // Pan direction: 'x', 'y', or 'xy'
        },
      },
    },
  };

  yAdjust = 0

  refreshing: boolean = false

  first: boolean = true

  lastMouseX = 0
  lastMouseY = 0

  isDragging: boolean = false

  filteredNames: any = {}

  public lineChartData: ChartData<'line'> = {
    datasets: [
      {
        label: 'Temperature Over Time',
        data: [
          { x: new Date('2025-01-01').getTime(), y: 22 },
          { x: new Date('2025-01-05').getTime(), y: 24 },
          { x: new Date('2025-01-10').getTime(), y: 19 },
          { x: new Date('2025-01-15').getTime(), y: 25 },
        ],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.3,
        fill: false,
      },
    ]
  };
  filteredData: Array<{ name: string, series: Array<any> }> = [];

  @Input() set resize(trigger: boolean) {
    this.fitAllGraph()
  }
  @Input() zoomEnabled: boolean = false

  @Input() set inputInfo(newValue: any) {
    console.log('Novo info de gráfico recebido:');
    this.lineChartData = 
    {
      datasets: [...newValue]
    }

    if (this.first) {
      this.first = false
      this.fitAllGraph()
    }
  }

  constructor() {

  }

  ngAfterViewInit() {
    //this.addKeyEventListeners();
  }

  // Add key event listeners for Ctrl and Shift keys
  addKeyEventListeners() {
    window.addEventListener('keydown', (event) => this.onKeyDown(event));
    window.addEventListener('keyup', (event) => this.onKeyUp(event));
  }

  onKeyDown(event: KeyboardEvent) {
    if (event.ctrlKey) {
      // Zoom only on X axis when Ctrl is pressed
      this.updateZoomMode('x');
    } else if (event.shiftKey) {
      // Zoom only on Y axis when Shift is pressed
      this.updateZoomMode('y');
    }
  }

  // Reset zoom mode when Ctrl or Shift key is released
  onKeyUp(event: KeyboardEvent) {
    if (!event.ctrlKey && !event.shiftKey) {
      // Reset to zoom on both axes when neither key is pressed
      this.updateZoomMode('xy');
    }
  }

  // Update the zoom mode dynamically
  updateZoomMode(mode: 'x' | 'y' | 'xy') {
    this.lineChartOptions.plugins!.zoom!.zoom!.mode = mode;
    this.lineChartOptions.plugins!.zoom!.pan!.mode = mode;

    // Update the chart after modifying the options
    this.chart?.chart?.update('none');
  }

  toggleSeries(seriesName: any, remove: boolean) {

  }

  fitAllGraph() {
    if (this.lineChartData) {
      let minYaxis = Number.MAX_SAFE_INTEGER
      let maxYaxis = Number.MIN_SAFE_INTEGER

      let minXaxis = new Date(8640000000000000).getTime();
      let maxXaxis = new Date(-8640000000000000).getTime()
      for (var infos of this.lineChartData.datasets) {
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

      let marginY = (maxYaxis - minYaxis) * 0.2

      if(this.lineChartOptions && 
         this.lineChartOptions.scales && 
         this.lineChartOptions.scales['y'] &&
         this.lineChartOptions.scales['x'])
      {
        this.lineChartOptions.scales['y'].max = maxYaxis + marginY
        this.lineChartOptions.scales['y'].min = minYaxis - marginY

        if (marginY === 0) {
          this.lineChartOptions.scales['y'].max += 1
          this.lineChartOptions.scales['y'].min -= 1
        }

        this.lineChartOptions.scales['x'].max = new Date(maxXaxis).getTime()
        this.lineChartOptions.scales['x'].min = new Date(minXaxis).getTime()
      }

    }

    this.chart?.chart?.resetZoom();

  }

  getXLimits(limit: any) {
    return limit
  }

  onMouseWheel(event: WheelEvent) {
    // event.preventDefault(); // Prevent default scroll behavior

    // const zoomFactor = 0.1; // Adjust zoom intensity
    // const zoomIn = event.deltaY < 0; // If scrolling up, zoom in

    // // Adjust X-Axis (Time)
    // const xRange = (Number)(this.chartOptions.xaxis.max) - (Number)(this.chartOptions.xaxis.min);
    // const xAdjust = xRange * zoomFactor;

    // var ctrlPressed = event.ctrlKey
    // var shiftPressed = event.shiftKey

    // if (shiftPressed || !ctrlPressed) {
    //   if (zoomIn) {
    //     this.chartOptions.xaxis.min = new Date((Number)(this.chartOptions.xaxis.min) + xAdjust).getTime();
    //     this.chartOptions.xaxis.max = new Date((Number)(this.chartOptions.xaxis.max) - xAdjust).getTime();
    //   } else {
    //     this.chartOptions.xaxis.min = new Date((Number)(this.chartOptions.xaxis.min) - xAdjust).getTime();
    //     this.chartOptions.xaxis.max =  new Date((Number)(this.chartOptions.xaxis.max) + xAdjust).getTime();
    //   }
    // }

    // if (ctrlPressed || !shiftPressed) {
    //   const yRange = (Number)(this.chartOptions.yaxis.max) - (Number)(this.chartOptions.yaxis.min);
    //   this.yAdjust = yRange * zoomFactor;

    //   if (zoomIn) {
    //     this.chartOptions.yaxis.min = (Number)(this.chartOptions.yaxis.min) + this.yAdjust;
    //     this.chartOptions.yaxis.max = (Number)(this.chartOptions.yaxis.max) - this.yAdjust;
    //   } else {
    //     this.chartOptions.yaxis.min = (Number)(this.chartOptions.yaxis.min) - this.yAdjust;
    //     this.chartOptions.yaxis.max = (Number)(this.chartOptions.yaxis.max) + this.yAdjust;
    //   }
    // }

  }

  onMouseDown(event: MouseEvent) {
    if (this.zoomEnabled) return;
    this.isDragging = true;
    this.lastMouseX = event.clientX;
    this.lastMouseY = event.clientY;
  }

  onMouseMove(event: MouseEvent) {
    //     if (this.zoomEnabled) return;
    //     if (!this.isDragging) return;
    //     const deltaX = event.clientX - this.lastMouseX;
    //     const deltaY = event.clientY - this.lastMouseY;

    //     this.lastMouseX = event.clientX;
    //     this.lastMouseY = event.clientY;

    //     // Adjust X-Axis (Time)
    //     const xRange = (Number)(this.chartOptions.xaxis.max) - (Number)(this.chartOptions.xaxis.min);
    //     const xMoveFactor = xRange * (deltaX / 700); // 700px = chart width
    // 90
    //     this.chartOptions.xaxis.min = (Number)(this.chartOptions.xaxis.min) - xMoveFactor;
    //     this.chartOptions.xaxis.max = (Number)(this.chartOptions.xaxis.max) - xMoveFactor;

    //     // Adjust Y-Axis (Temperature)
    //     const yRange = (Number)(this.chartOptions.yaxis.max) - (Number)(this.chartOptions.yaxis.min);
    //     const yMoveFactor = yRange * (deltaY / 400); // 400px = chart height

    //     this.chartOptions.yaxis.min = (Number)(this.chartOptions.yaxis.min) + yMoveFactor;
    //     this.chartOptions.yaxis.max = (Number)(this.chartOptions.yaxis.max) + yMoveFactor;
  }

  /** 📌 Mouse Drag End **/
  onMouseUp(event: MouseEvent) {
    this.isDragging = false;
  }
}
