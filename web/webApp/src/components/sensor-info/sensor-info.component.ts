import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
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
  @Input() currentReading: string = ""
  @Input() tableArray: any[] = []

  @Output() onLoad: EventEmitter<any> = new EventEmitter()
  @Output() onExit: EventEmitter<any> = new EventEmitter()

  headerInfo: Array<any> = [["value", "Pessoa"], ["timestamp","Data"]]
  refreshing = false

  constructor() { }

  ngOnInit(): void {
    this.getStatusHistory()
  }

  return()
  {
    this.onExit.emit()
  }

  getCurrentValue()
  {
    return this.currentReading && this.currentReading != "" ? this.currentReading:"???" 
  }

  getStatusHistory()
  {
    let gtw = this.sensorInfo.gateway=="*"?"":this.sensorInfo.gateway 
    this.onLoad.emit({"gateway": gtw, "table": this.sensorInfo.topic})
  }

}
