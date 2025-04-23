import { Component, ElementRef, Input, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  NgApexchartsModule,
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexYAxis,
  ApexDataLabels,
  ApexStroke,
  ApexTitleSubtitle,
  ApexTooltip,
  ApexMarkers
} from 'ng-apexcharts';

export type ChartOptions = {
  chart: ApexChart;
  xaxis: ApexXAxis;
  yaxis: ApexYAxis;
  dataLabels: ApexDataLabels;
  stroke: ApexStroke;
  title: ApexTitleSubtitle;
  tooltip: ApexTooltip;
  markers: ApexMarkers;
};

@Component({
  selector: 'graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss'],
  imports: [CommonModule,
    NgApexchartsModule
  ],
  standalone: true
})
export class GraphComponent {

  public chartOptions: ChartOptions = {
    chart: {
      type: "line",
      animations: {
        enabled: false
      },
      zoom: {
        enabled: true,
        type: "xy",
        autoScaleYaxis: true,
        zoomedArea: {
          fill: {
            color: "#90CAF9",
            opacity: 0.4,
          },
          stroke: {
            color: "#0D47A1",
            opacity: 0.4,
            width: 1,
          },
        },
      },
      toolbar: {
        autoSelected: "pan", // Set default to pan for smoother control
        tools: {
          zoom: true,
          zoomin: true,
          zoomout: true,
          pan: true,
          reset: true,
        },
      }
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      curve: "smooth",
      width: 2
    },
    title: {
      text: "Zoomable Line Chart",
      align: "left",
    },
    xaxis: {
      type: 'datetime',
      min: undefined,
      max: undefined
    },
    yaxis: {
      min: undefined,
      max: undefined
    },
    tooltip: {
      x: {
        format: "dd MMM yyyy",
      },
    },
    markers: {
      size: 0, // hide by default
      hover: {
        size: 5 // show on hover only
      }
    },
  };

  yAdjust = 0

  refreshing: boolean = false

  first: boolean = true

  lastMouseX = 0
  lastMouseY = 0

  isDragging: boolean = false

  filteredNames: any = {}

  lineChartData: ApexAxisChartSeries = [];
  filteredData: Array<{ name: string, series: Array<any> }> = [];

  @Input() set resize(trigger: boolean) {
    this.fitAllGraph()
  }
  @Input() zoomEnabled: boolean = false

  @Input() set inputInfo(newValue: ApexAxisChartSeries) {
    console.log('Novo info de gráfico recebido:');

    this.lineChartData = [...newValue]

    if (this.first) {
      this.first = false
      this.fitAllGraph()
    }
  }

  constructor() {

  }

  ngAfterViewInit() { }

  zoomToSelection(startX: number, endX: number, startY: number, endY: number, valueScale: any, dateScale: any) {
    if (Math.abs(startX - endX) < 30 || Math.abs(startY - endY) < 30) return;
    const minX = Math.min(startX, endX);
    const maxX = Math.max(startX, endX);
    const minY = Math.min(startY, endY);
    const maxY = Math.max(startY, endY);

    // Convert pixel values to date range


    let y1 = valueScale.invert(minY);
    let y2 = valueScale.invert(maxY);

    this.chartOptions.xaxis.min = dateScale.invert(minX);
    this.chartOptions.xaxis.max = dateScale.invert(maxX);

    this.chartOptions.yaxis.max = Math.max(y1, y2);
    this.chartOptions.yaxis.min = Math.min(y1, y2);
  }

  toggleSeries(seriesName: any, remove: boolean) {

  }

  fitAllGraph() {
    if (this.lineChartData.length > 0) {
      let minYaxis = Number.MAX_SAFE_INTEGER
      let maxYaxis = Number.MIN_SAFE_INTEGER

      let minXaxis = new Date(8640000000000000).getTime();
      let maxXaxis = new Date(-8640000000000000).getTime()
      for (var infos of this.lineChartData) {
        for (let info of infos.data) {
          if(typeof info === 'object' && info !== null && !Array.isArray(info))
          {
            let dt = info.x;
            let value = info.y

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
      }

      let marginY = (maxYaxis - minYaxis) * 0.2

      this.chartOptions.yaxis.max = maxYaxis + marginY
      this.chartOptions.yaxis.min = minYaxis - marginY

      if (marginY === 0) {
        this.chartOptions.yaxis.max += 1
        this.chartOptions.yaxis.min -= 1
      }

      this.chartOptions.xaxis.max = new Date(maxXaxis).getTime()
      this.chartOptions.xaxis.min = new Date(minXaxis).getTime()

    }

  }

  getXLimits(limit: any) {
    return limit
  }

  onMouseWheel(event: WheelEvent) {
    event.preventDefault(); // Prevent default scroll behavior

    const zoomFactor = 0.1; // Adjust zoom intensity
    const zoomIn = event.deltaY < 0; // If scrolling up, zoom in

    // Adjust X-Axis (Time)
    const xRange = (Number)(this.chartOptions.xaxis.max) - (Number)(this.chartOptions.xaxis.min);
    const xAdjust = xRange * zoomFactor;

    var ctrlPressed = event.ctrlKey
    var shiftPressed = event.shiftKey

    if (shiftPressed || !ctrlPressed) {
      if (zoomIn) {
        this.chartOptions.xaxis.min = new Date((Number)(this.chartOptions.xaxis.min) + xAdjust).getTime();
        this.chartOptions.xaxis.max = new Date((Number)(this.chartOptions.xaxis.max) - xAdjust).getTime();
      } else {
        this.chartOptions.xaxis.min = new Date((Number)(this.chartOptions.xaxis.min) - xAdjust).getTime();
        this.chartOptions.xaxis.max =  new Date((Number)(this.chartOptions.xaxis.max) + xAdjust).getTime();
      }
    }

    if (ctrlPressed || !shiftPressed) {
      const yRange = (Number)(this.chartOptions.yaxis.max) - (Number)(this.chartOptions.yaxis.min);
      this.yAdjust = yRange * zoomFactor;

      if (zoomIn) {
        this.chartOptions.yaxis.min = (Number)(this.chartOptions.yaxis.min) + this.yAdjust;
        this.chartOptions.yaxis.max = (Number)(this.chartOptions.yaxis.max) - this.yAdjust;
      } else {
        this.chartOptions.yaxis.min = (Number)(this.chartOptions.yaxis.min) - this.yAdjust;
        this.chartOptions.yaxis.max = (Number)(this.chartOptions.yaxis.max) + this.yAdjust;
      }
    }

  }

  onMouseDown(event: MouseEvent) {
    if (this.zoomEnabled) return;
    this.isDragging = true;
    this.lastMouseX = event.clientX;
    this.lastMouseY = event.clientY;
  }

  onMouseMove(event: MouseEvent) {
    if (this.zoomEnabled) return;
    if (!this.isDragging) return;
    const deltaX = event.clientX - this.lastMouseX;
    const deltaY = event.clientY - this.lastMouseY;

    this.lastMouseX = event.clientX;
    this.lastMouseY = event.clientY;

    // Adjust X-Axis (Time)
    const xRange = (Number)(this.chartOptions.xaxis.max) - (Number)(this.chartOptions.xaxis.min);
    const xMoveFactor = xRange * (deltaX / 700); // 700px = chart width
90
    this.chartOptions.xaxis.min = (Number)(this.chartOptions.xaxis.min) - xMoveFactor;
    this.chartOptions.xaxis.max = (Number)(this.chartOptions.xaxis.max) - xMoveFactor;

    // Adjust Y-Axis (Temperature)
    const yRange = (Number)(this.chartOptions.yaxis.max) - (Number)(this.chartOptions.yaxis.min);
    const yMoveFactor = yRange * (deltaY / 400); // 400px = chart height

    this.chartOptions.yaxis.min = (Number)(this.chartOptions.yaxis.min) + yMoveFactor;
    this.chartOptions.yaxis.max = (Number)(this.chartOptions.yaxis.max) + yMoveFactor;
  }

  /** 📌 Mouse Drag End **/
  onMouseUp(event: MouseEvent) {
    this.isDragging = false;
  }
}
