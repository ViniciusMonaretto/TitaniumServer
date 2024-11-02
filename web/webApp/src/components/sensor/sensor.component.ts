import { Component, OnInit, Input } from '@angular/core';
import { SensorModule } from 'src/models/sensor-module';

@Component({
  selector: 'sensor',
  templateUrl: './sensor.component.html',
  styleUrls: ['./sensor.component.scss']
})
export class SensorComponent implements OnInit {
  @Input() sensorInfo: SensorModule = new SensorModule()
  constructor() { }

  ngOnInit(): void {
  }

}
