import { Component, OnInit } from '@angular/core';
import {ServerConectorService} from "../../services/server-conector.service"
import {UiPanelService} from "../../services/ui-panels.service"

@Component({
  selector: 'table-view',
  templateUrl: './table-view.component.html',
  styleUrls: ['./table-view.component.scss']
})
export class TableViewComponent implements OnInit {

  constructor(private serverConnector: ServerConectorService, private uiPanelService: UiPanelService) { 
    //this.getTable()
  }

  minYaxis =  Number.MAX_SAFE_INTEGER
  maxYaxis =  Number.MIN_SAFE_INTEGER

  marginMaxY = 0
  marginMinY = 0
  refreshing: boolean = false
  array: Array<any> = []

  selectedDate: Date | null = null

  colorScheme: any = {
    domain: ['#3366CC']
  };

  
  headerInfo: Array<any> = [["value", "Pessoa"], ["timestamp","Data"]]//['value', 'timestamp']
  gateway: string = "1C692031BE04"
  table: string = "temperature"

  lineChartData: Array<{name: string, series: Array<any>}> = [

  ];

  onGraphUpdate: Function = (tableName: string) => {
    let chartId = this.lineChartData.findIndex(x => x.name == tableName);
    
    if (chartId == -1) {
        this.lineChartData.push({
            name: tableName,
            series: []
        });
        chartId = this.lineChartData.length - 1;
    }

    let newSeries: { name: Date, value: number }[] = [];
    let infos = this.uiPanelService.GetTableInfoFromTablename(tableName) || []; // Ensure it's not null

    for (let info of infos) {
        let timestamp = info['timestamp'];
        if (timestamp && !isNaN(new Date(timestamp).getTime())) {
            let dt = new Date(timestamp);
            newSeries.push({ name: dt, value: info["value"] });

            if(this.minYaxis > info["value"])
            { 
              this.minYaxis = info["value"]
            }
            if(this.maxYaxis < info["value"])
            { 
              this.maxYaxis = info["value"]
            }
        } else {
            console.error('Invalid timestamp:', timestamp); // Debugging
        }
    }
    let margin = (this.maxYaxis - this.minYaxis) * 0.2
    if(margin != 0)
    {
      this.marginMaxY = Math.floor(this.maxYaxis + margin)
      this.marginMinY = Math.floor(this.minYaxis - margin)
    }
    else
    {
      this.marginMaxY =  this.minYaxis + 1
      this.marginMinY = this.minYaxis - 1
    }


    // Update chart data and trigger Angular change detection
    this.lineChartData[chartId].series = [...newSeries]; 
    this.lineChartData = [...this.lineChartData]; // Force UI update
};

  // Color scheme
  
  ngOnInit(): void {}

  getTable(): void{ 
    this.refreshing = true
    this.uiPanelService.AddSubscriptionFromGraph(this.gateway, this.table, this.onGraphUpdate)
    this.serverConnector.sendRequestForTableInfo(this.gateway, this.table, this.selectedDate)

  }

  setTime(event: any, selectedDateTime: Date | null) {
    if (selectedDateTime) {
      const [hours, minutes] = event.target.value.split(':');
      selectedDateTime.setHours(parseInt(hours, 10), parseInt(minutes, 10));
    }
  }

  getTableInfo()
  {
    return this.uiPanelService.GetTableInfo(this.gateway, this.table)
  }

}
