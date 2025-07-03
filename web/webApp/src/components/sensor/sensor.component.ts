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
  @Input() canEdit: boolean = false
  @Input() sensorInfo: SensorModule = new SensorModule()
  @Output() clickCallback: EventEmitter<any> = new EventEmitter();
  @Output() deleteCallback: EventEmitter<any> = new EventEmitter();
  
  public sensorTypes = Object.values(SensorTypesEnum);
  
  constructor() { }

  getMeasureIcon(): String
  {
    if(this.sensorInfo.sensorType == SensorTypesEnum.PREASSURE)
    {
      return "Pa"
    }
    if(this.sensorInfo.sensorType == SensorTypesEnum.TEMPERATURE)
    {
        return "ºC"
    }
    if(this.sensorInfo.sensorType == SensorTypesEnum.POWER)
    {
        return "Kw"
    }

    return ""
  }

  ngOnInit(): void {
    this.sensorInfo.name
  }

  getColorOfSensor()
  {
    var value = this.sensorInfo?.value
    var maxValue = this.sensorInfo?.maxAlarm?.threshold
    var minValue = this.sensorInfo?.minAlarm?.threshold

    if (!value)
    {
      return 'none';
    }

    if (maxValue && value > maxValue)
    {
      return 'red'
    }

    if (minValue && value < minValue)
    {
      return 'red'
    }

    return 'none';
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
