import { Component, Input } from '@angular/core';

@Component({
  selector: 'graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss']
})
export class GraphComponent {

  yAdjust = 0
  yScaleMin = 0
  yScaleMax = 0
  xScaleMin: any = new Date()
  xScaleMax: any = new Date()
  refreshing: boolean = false

  moved= false

  first: boolean = true

  lastMouseX = 0
  lastMouseY = 0

  isDragging: boolean = false

  filteredNames: any = {}
  lineChartData: Array<{ name: string, series: Array<any> }> = [];
  filteredData: Array<{ name: string, series: Array<any> }> = [];

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
      
      let infos = this.lineChartData[0]
      let minYaxis = Number.MAX_SAFE_INTEGER
      let maxYaxis = Number.MIN_SAFE_INTEGER

      let minXaxis = new Date(8640000000000000);
      let maxXaxis = new Date(-8640000000000000)

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

      this.moved = false
    }

  }

  getXLimits(limit: any)
  {
    return this.moved? limit:null
  }

  onMouseWheel(event: WheelEvent) {
    this.moved = true
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
    this.isDragging = true;
    this.lastMouseX = event.clientX;
    this.lastMouseY = event.clientY;
  }

  onMouseMove(event: MouseEvent) {
   
    if (!this.isDragging) return;
    this.moved = true
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
