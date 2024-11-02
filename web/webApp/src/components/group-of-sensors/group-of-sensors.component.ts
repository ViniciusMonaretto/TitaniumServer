import { Component, OnInit, Input } from '@angular/core';
import { SensorModule } from "../../models/sensor-module"

@Component({
  selector: 'group-of-sensors',
  templateUrl: './group-of-sensors.component.html',
  styleUrls: ['./group-of-sensors.component.scss']
})
export class GroupOfSensorsComponent implements OnInit {

  @Input() name: string = "";
  @Input() sensorArray: Array<SensorModule> = [];

  constructor() { }

  ngOnInit(): void {
  }

}
