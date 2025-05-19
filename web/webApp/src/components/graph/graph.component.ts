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

  @Input() blockFitAll: boolean = false

  @Input() set resize(trigger: boolean) {
    this.fitAllGraph()
  }
  @Input() zoomEnabled: boolean = true

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

  lineChartOptions: ChartOptions<'line'> = {
    responsive: true,
    animation: false,
    maintainAspectRatio: false,
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
          text: 'Value',
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

  first: boolean = true

  public lineChartData: ChartData<'line'> = {
    datasets: [
      
    ]
  };
  filteredData: Array<{ name: string, series: Array<any> }> = [];

  constructor() { }

  ngAfterViewInit() {
  }

  fitAllGraph() {
    if (this.lineChartData && !this.blockFitAll) {
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
}
