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
  zoomWindowActivate: boolean = false
  lineChartData: Array<any> = [];

  ngOnInit(): void { }

  onGraphUpdate: Function = (tableName: string, infoArr: Array<any>) => {
    let chartId = this.lineChartData.findIndex(x => x.label == tableName);

    if (chartId == -1) {
      this.lineChartData.push({
        label: tableName,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
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
                                                   this.onGraphUpdate,
                                                   sensorData['startDate'],
                                                   sensorData['endDate'])
  }

}
