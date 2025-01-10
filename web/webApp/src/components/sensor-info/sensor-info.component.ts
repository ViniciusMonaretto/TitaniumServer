import { Component, OnInit, Input } from '@angular/core';
import {ServerConectorService} from "../../services/server-conector.service"
import {UiPanelService} from "../../services/ui-panels.service"
import { SensorModule } from 'src/models/sensor-module';

@Component({
  selector: 'sensor-info',
  templateUrl: './sensor-info.component.html',
  styleUrls: ['./sensor-info.component.scss']
})
export class SensorInfoComponent implements OnInit {

  @Input() sensorInfo: SensorModule = new SensorModule()
  @Input() set currentReading(value: string|null)
  {
    if(value !== null)
    {
      this.currentReadingInternal = value
      this.array.push({"value": value, "timestamp": new Date(Date.now()).toISOString()})
      
      this.array = this.array.slice()
      this.currentReading = null
    }
    
  }

  currentReadingInternal = ""

  headerInfo: Array<any> = [["value", "Pessoa"], ["timestamp","Data"]]//['value', 'timestamp']
  array: Object[] = []
  refreshing = false

  constructor(private serverConnector: ServerConectorService, private uiPanelService: UiPanelService) { }

  ngOnInit(): void {
    this.getStatusHistory()
  }

  return()
  {
    this.uiPanelService.setelectSensor(null)
  }

  getStatusHistory()
  {
    let gtw = this.sensorInfo.gateway=="*"?"":this.sensorInfo.gateway 
    this.refreshing = true
    this.serverConnector.sendRequestForTableInfo(gtw, this.sensorInfo.topic, (value: any)=>{
      this.array = value.info
      this.refreshing = false
    })
  }

}
