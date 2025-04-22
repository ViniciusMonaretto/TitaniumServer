import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { SensorModule } from '../../models/sensor-module';
import { SensorTypesEnum } from '../../enum/sensor-type';

import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
    selector: 'sensor',
    templateUrl: './sensor.component.html',
    styleUrls: ['./sensor.component.scss'],
    imports: [CommonModule, MatIconModule],
    standalone: true
})
export class SensorComponent implements OnInit {
  @Input() sensorInfo: SensorModule = new SensorModule()
  @Output() clickCallback: EventEmitter<any> = new EventEmitter();
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
        return "ºC"
    }
    if(this.sensorInfo.sensorType == SensorTypesEnum.POTENCY)
    {
        return "Kw"
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

  infoCLick()
  {
    this.clickCallback.emit(this.sensorInfo)
  }

  getCurrentReading()
  {
    return this.sensorInfo?.value ? this.sensorInfo?.value : "--"
  }

}
