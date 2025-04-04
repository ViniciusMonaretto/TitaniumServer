import { Component, ElementRef, Input, ViewChild } from '@angular/core';
import * as d3 from 'd3'

@Component({
  selector: 'graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss']
})
export class GraphComponent {
  @ViewChild('overlay') overlayRef!: ElementRef;
  @ViewChild('chartContainer') chartContainerRef!: ElementRef;
  @ViewChild('tooltip') tooltipRef!: ElementRef;

  yAdjust = 0
  yScaleMin = 0
  yScaleMax = 0
  xScaleMin: any = new Date()
  xScaleMax: any = new Date()
  refreshing: boolean = false

  first: boolean = true

  lastMouseX = 0
  lastMouseY = 0

  isDragging: boolean = false

  filteredNames: any = {}
  lineChartData: Array<{ name: string, series: Array<any> }> = [];
  filteredData: Array<{ name: string, series: Array<any> }> = [];

  @Input() set resize(trigger: boolean) {
    this.fitAllGraph()
  }
  @Input() zoomEnabled: boolean = false

  @Input() set inputInfo(newValue: Array<{ name: string, series: Array<any> }> ) {
    console.log('Novo info de gráfico recebido:');

    this.lineChartData = newValue
    this.remakeLineFilter()

    if(this.first)
    {
      this.first = false
      this.fitAllGraph()
    }
  }

  constructor() { }

  ngAfterViewInit() {
    const svg = d3.select(this.chartContainerRef.nativeElement);
    const overlay = d3.select(this.overlayRef.nativeElement);
    const tooltip = d3.select(this.tooltipRef.nativeElement);
    let startX: number, startY: number, endX: number, endY: number;

    let dateScale: d3.ScaleTime<number, number, never>;

    let valueScale: d3.ScaleLinear<number, number, never>;

    svg.on('mousedown', (event: MouseEvent) => {
      if (!this.zoomEnabled) return;
      const graphWidth = this.chartContainerRef.nativeElement.querySelector('svg').clientWidth; 
      const graphHeight = this.chartContainerRef.nativeElement.querySelector('svg').clientHeight; // Get actual SVG width
      dateScale = d3.scaleTime()
                    .domain([this.xScaleMin, this.xScaleMax])
                    .range([0, graphWidth]);
      valueScale = d3.scaleLinear()
                     .domain([this.yScaleMin, this.yScaleMax])
                     .range([graphHeight, 0])

      const rect = this.chartContainerRef.nativeElement.getBoundingClientRect()
      startX = event.clientX - rect.left
      startY = event.clientY - rect.top
      overlay.style('display', 'block')
             .style('left', `${startX}px`)
             .style('top', `${startY}px`)
             .style('width', '0px')
             .style('height', '0px');
      tooltip.style('display', 'block')
             .style('left', `${startX}px`)
             .style('top', `${startY - 20}px`)
             .text(`Start: (${dateScale.invert(startX).toISOString()}, ${valueScale.invert(startY).toFixed(2)})`);
    });

    svg.on('mousemove', (event: MouseEvent) => {
      if (!this.zoomEnabled || startX === undefined) return;
      const rect = this.chartContainerRef.nativeElement.getBoundingClientRect()
      endX = event.clientX - rect.left
      endY = event.clientY - rect.top
      overlay.style('width', `${Math.abs(endX - startX)}px`)
             .style('height', `${Math.abs(endY - startY)}px`)
             .style('left', `${Math.min(startX, endX)}px`)
             .style('top', `${Math.min(startY, endY)}px`)
             .style('display', 'block');
      tooltip.style('display', 'block')
             .style('left', `${endX}px`)
             .style('top', `${endY - 20}px`)
             .text(`Start: (${dateScale.invert(endX).toISOString()}, ${valueScale.invert(endY).toFixed(2)})`);
    });

    svg.on('mouseup', () => {
      if (!this.zoomEnabled || startX === undefined || endX === undefined || startY === undefined || endY === undefined) return;
      this.zoomToSelection(startX, endX, startY, endY, valueScale, dateScale);
      overlay.style('display', 'none');
      tooltip.style('display', 'none');
      startX = startY = endX = endY = <any>undefined;
    });
  }

  zoomToSelection(startX: number, endX: number, startY: number, endY: number, valueScale: any, dateScale: any) {
    if (Math.abs(startX-endX) < 30 || Math.abs(startY-endY) < 30 ) return; 
    const minX = Math.min(startX, endX);
    const maxX = Math.max(startX, endX);
    const minY = Math.min(startY, endY);
    const maxY = Math.max(startY, endY);
    
    // Convert pixel values to date range
    

    let y1 = valueScale.invert(minY);
    let y2 = valueScale.invert(maxY); 
    
    this.xScaleMin = dateScale.invert(minX);
    this.xScaleMax = dateScale.invert(maxX);

    this.yScaleMax = Math.max(y1, y2);
    this.yScaleMin = Math.min(y1, y2);
  }

  remakeLineFilter()
  {
    this.filteredData = []
    for(let dataChart of this.lineChartData)
    {
      if(!this.filteredNames[dataChart.name])
      {
        this.filteredData.push({
          "name": dataChart.name,
          "series": [...dataChart.series]
        })
      }
    }
  }

  toggleSeries(seriesName: any, remove: boolean) {
    if (remove) {
      // Completely remove from dataset
      this.lineChartData = this.lineChartData.filter(s => s.name !== seriesName);
      this.filteredData = this.filteredData.filter(s => s.name !== seriesName);
    } else {
      // Just filter out (hide)
      const index = this.filteredData.findIndex(s => s.name === seriesName);
      if (index !== -1) {
        this.filteredData.splice(index, 1); // Remove from display
        this.filteredNames[seriesName] = true
      } else {
        const originalSeries = this.lineChartData.find(s => s.name === seriesName);
        if (originalSeries) this.filteredData.push(originalSeries); // Re-add
        this.filteredNames[seriesName] = false
      }
    }
    this.filteredData = [...this.filteredData]; // Force change detection
  } 

  fitAllGraph() {
    if (this.lineChartData.length > 0) {
      let minYaxis = Number.MAX_SAFE_INTEGER
      let maxYaxis = Number.MIN_SAFE_INTEGER

      let minXaxis = new Date(8640000000000000);
      let maxXaxis = new Date(-8640000000000000)
      for(var infos of this.lineChartData)
      {
        for (let info of infos.series) {

          let dt = info["name"];
          let value = info["value"]

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
      
      let marginY = (maxYaxis - minYaxis)*0.2
      
      this.yScaleMax = maxYaxis + marginY
      this.yScaleMin = minYaxis - marginY

      if(marginY === 0)
      {
        this.yScaleMax += 1
        this.yScaleMin -= 1
      }

      this.xScaleMax = new Date(maxXaxis)
      this.xScaleMin = new Date(minXaxis)

    }

  }

  getXLimits(limit: any)
  {
    return limit
  }

  onMouseWheel(event: WheelEvent) {
    event.preventDefault(); // Prevent default scroll behavior

    const zoomFactor = 0.1; // Adjust zoom intensity
    const zoomIn = event.deltaY < 0; // If scrolling up, zoom in

    // Adjust X-Axis (Time)
    const xRange = this.xScaleMax.getTime() - this.xScaleMin.getTime();
    const xAdjust = xRange * zoomFactor;

    var ctrlPressed = event.ctrlKey
    var shiftPressed = event.shiftKey

    if(shiftPressed || !ctrlPressed)
    {
      if (zoomIn) {
        this.xScaleMin = new Date(this.xScaleMin.getTime() + xAdjust);
        this.xScaleMax = new Date(this.xScaleMax.getTime() - xAdjust);
      } else {
        this.xScaleMin = new Date(this.xScaleMin.getTime() - xAdjust);
        this.xScaleMax = new Date(this.xScaleMax.getTime() + xAdjust);
      }
    }
    
    if(ctrlPressed || !shiftPressed )
    {
      const yRange = this.yScaleMax - this.yScaleMin;
      this.yAdjust = yRange * zoomFactor;

      if (zoomIn) {
        this.yScaleMin += this.yAdjust;
        this.yScaleMax -= this.yAdjust;
      } else {
        this.yScaleMin -= this.yAdjust;
        this.yScaleMax += this.yAdjust;
      }
    }
    
  }

  onMouseDown(event: MouseEvent) {
    if(this.zoomEnabled) return;
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
    const xRange = this.xScaleMax.getTime() - this.xScaleMin.getTime();
    const xMoveFactor = xRange * (deltaX / 700); // 700px = chart width

    this.xScaleMin = new Date(this.xScaleMin.getTime() - xMoveFactor);
    this.xScaleMax = new Date(this.xScaleMax.getTime() - xMoveFactor);

    // Adjust Y-Axis (Temperature)
    const yRange = this.yScaleMax - this.yScaleMin;
    const yMoveFactor = yRange * (deltaY / 400); // 400px = chart height

    this.yScaleMin += yMoveFactor;
    this.yScaleMax += yMoveFactor;
  }

  /** 📌 Mouse Drag End **/
  onMouseUp(event: MouseEvent) {
    this.isDragging = false;
  }
}
