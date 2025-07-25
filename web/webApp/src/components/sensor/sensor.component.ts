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
    if(this.sensorInfo.sensorType == SensorTypesEnum.CURRENT)
    {
        return "A"
    }
    if(this.sensorInfo.sensorType == SensorTypesEnum.TENSION)
    {
        return "V"
    }
    if(this.sensorInfo.sensorType == SensorTypesEnum.POWER_FACTOR)
    {
        return "%"
    }

    return ""
  }

  ngOnInit(): void {
    this.sensorInfo.name
  }

  getStatusMessageOfSensor()
  {
    var value = this.sensorInfo?.value
    var maxValue = this.sensorInfo?.maxAlarm?.threshold
    var minValue = this.sensorInfo?.minAlarm?.threshold

    if (!value)
    {
      return 'OK';
    }

    if (maxValue && value > maxValue)
    {
      return 'Valor Muito Alto'
    }

    if (minValue && value < minValue)
    {
      return 'Valor Muito Baixo'
    }

    return 'none';
  }

  getColorOfSensor()
  {
    var value = this.sensorInfo?.value
    var maxValue = this.sensorInfo?.maxAlarm?.threshold
    var minValue = this.sensorInfo?.minAlarm?.threshold

    if (!value)
    {
      return '#22C55E';
    }

    if (maxValue && value > maxValue)
    {
      return '#FA3838'
    }

    if (minValue && value < minValue)
    {
      return 'rgb(31 31 141)'
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
