import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { SensorModule } from 'src/models/sensor-module';
import { SensorTypesEnum } from 'src/enum/sensor-type';

@Component({
  selector: 'sensor',
  templateUrl: './sensor.component.html',
  styleUrls: ['./sensor.component.scss']
})
export class SensorComponent implements OnInit {
  @Input() sensorInfo: SensorModule = new SensorModule()
  @Output() deleteCallback: EventEmitter<any> = new EventEmitter();
  
  public sensorTypes = Object.values(SensorTypesEnum);
  
  constructor() { }

  getMeasureIcon(): String
  {
    if(this.sensorInfo.sensorType == SensorTypesEnum.PREASSURE)
    {
      return "Psa"
    }
    if(this.sensorInfo.sensorType == SensorTypesEnum.TEMPERATURE)
    {
        return "C"
    }
    if(this.sensorInfo.sensorType == SensorTypesEnum.HUMIDITY)
    {
        return "%"
    }

    return ""
  }

  ngOnInit(): void {
    this.sensorInfo.name
  }

  deletePanel()
  {
    this.deleteCallback.emit(this.sensorInfo.id)
  }

  getCurrentReading()
  {
    return this.sensorInfo?.value ? this.sensorInfo?.value : "--"
  }

}
