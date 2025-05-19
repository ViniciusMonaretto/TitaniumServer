import { Component, OnInit } from '@angular/core';
import { ServerConectorService } from "../../services/server-conector.service"
import { UiPanelService } from "../../services/ui-panels.service"
import { MatDialog } from '@angular/material/dialog';

import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

import { GraphComponent } from '../../components/graph/graph.component';

import { GraphRequestWindowComponent } from '../../components/graph-request-window/graph-request-window.component';

@Component({
    selector: 'graph-view',
    templateUrl: './graph-view.component.html',
    styleUrls: ['./graph-view.component.scss'],
    imports: [CommonModule, MatIconModule, GraphComponent],
    standalone: true
})
export class GraphViewComponent implements OnInit {

  constructor(public dialog: MatDialog, private serverConnector: ServerConectorService, private uiPanelService: UiPanelService) {
    //this.getTable()
  }

  resizeTrigger: boolean = false
  zoomWindowActivate: boolean = true
  lineChartData: Array<any> = [];

  ngOnInit(): void { }

  onGraphUpdate: Function = (tableInfo: {name: string, realName: string, color: string}, infoArr: Array<any>) => {
    let chartId = this.lineChartData.findIndex(x => x.realName == tableInfo.realName);

    if (chartId == -1) {
      this.lineChartData.push({
        label: tableInfo.name,
        type: 'line',
        realName: tableInfo.realName,
        borderColor: tableInfo.color,
        backgroundColor: tableInfo.color + '0A',
        tension: 0.3,
        fill: false,
        data: []
      });
      chartId = this.lineChartData.length - 1;
    }

    let newSeries: { x: number, y: number }[] = [];

    for (let info of infoArr) {
      let timestamp = info['timestamp'];
      if (timestamp && !isNaN(new Date(timestamp).getTime())) {
        let dt = new Date(timestamp);
        newSeries.push({ x: dt.getTime(), y: info["value"] });
      } else {
        console.error('Invalid timestamp:', timestamp); // Debugging
      }
    }

    // Update chart data and trigger Angular change detection
    this.lineChartData[chartId].data = newSeries;

    this.lineChartData = [...this.lineChartData ]
  };

  toggleZoomWindowActivate()
  {
    this.zoomWindowActivate = !this.zoomWindowActivate
  }

  openAddWindow()
  {
    const dialogRef = this.dialog.open(GraphRequestWindowComponent, {
      width: '500px',
      data: {
        "uiConfig": this.uiPanelService.GetUiConfig(),
        callback: (sensorData: any)=>{
          this.getTable(sensorData)
        }
      }
    });
  }

  removeAllLines()
  {
    this.lineChartData = []
  }

  getTable(sensorData: any): void {
    this.serverConnector.sendRequestForTableInfo(sensorData['selectedSensors'],
                                                 sensorData['group'], 
                                                 sensorData['startDate'],
                                                 sensorData['endDate'],
                                                 this.onGraphUpdate)
  }

}
