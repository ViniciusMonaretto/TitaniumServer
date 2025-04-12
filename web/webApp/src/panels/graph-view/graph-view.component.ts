import { Component, OnInit } from '@angular/core';
import { ServerConectorService } from "../../services/server-conector.service"
import { UiPanelService } from "../../services/ui-panels.service"
import { MatDialog } from '@angular/material/dialog';
import { GraphRequestWindowComponent } from 'src/components/graph-request-window/graph-request-window.component';

@Component({
  selector: 'graph-view',
  templateUrl: './graph-view.component.html',
  styleUrls: ['./graph-view.component.scss']
})
export class GraphViewComponent implements OnInit {

  constructor(public dialog: MatDialog, private serverConnector: ServerConectorService, private uiPanelService: UiPanelService) {
    //this.getTable()
  }

  resizeTrigger: boolean = false
  zoomWindowActivate: boolean = false
  lineChartData: Array<{ name: string, series: Array<any> }> = [];

  ngOnInit(): void { }

  onGraphUpdate: Function = (tableName: string, infoArr: Array<any>) => {
    let chartId = this.lineChartData.findIndex(x => x.name == tableName);

    if (chartId == -1) {
      this.lineChartData.push({
        name: tableName,
        series: []
      });
      chartId = this.lineChartData.length - 1;
    }

    let newSeries: { name: Date, value: number }[] = [];

    for (let info of infoArr) {
      let timestamp = info['timestamp'];
      if (timestamp && !isNaN(new Date(timestamp).getTime())) {
        let dt = new Date(timestamp);
        newSeries.push({ name: dt, value: info["value"] });
      } else {
        console.error('Invalid timestamp:', timestamp); // Debugging
      }
    }

    // Update chart data and trigger Angular change detection
    this.lineChartData[chartId].series = newSeries;

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
    this.serverConnector.sendRequestForTableInfo(sensorData['selectedSensors'], this.onGraphUpdate,)
  }

}
