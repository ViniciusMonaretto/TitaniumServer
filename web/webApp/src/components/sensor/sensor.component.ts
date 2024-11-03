import { Component, OnInit, Input } from '@angular/core';
import { SensorModule } from 'src/models/sensor-module';
import { SensorTypesEnum } from 'src/enum/sensor-type';

@Component({
  selector: 'sensor',
  templateUrl: './sensor.component.html',
  styleUrls: ['./sensor.component.scss']
})
export class SensorComponent implements OnInit {
  @Input() sensorInfo: SensorModule = new SensorModule()
  @Input() value: number | null = null
  
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
        return "c"
    }

    return ""
  }

  ngOnInit(): void {
    this.sensorInfo.name
  }

  getCurrentReading()
  {
    return this.value ? this.value : "--"
  }

}
