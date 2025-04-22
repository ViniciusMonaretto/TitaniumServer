import { Component, OnInit } from '@angular/core';
import {MainScreenSelector} from "../../services/main-screen-selector.service"
import {ServerConectorService} from "../../services/server-conector.service"
import {MainScreenOptions} from "../../enum/screen-type"

import { CommonModule } from '@angular/common';

import { GraphViewComponent } from '../graph-view/graph-view.component';
import { SensorGroupComponent } from '../sensor-group/sensor-group.component';

@Component({
    selector: 'app-main-screen',
    templateUrl: './main-screen.component.html',
    styleUrls: ['./main-screen.component.scss'],
    imports: [CommonModule, GraphViewComponent, SensorGroupComponent],
    standalone: true
})
export class MainScreenComponent implements OnInit {

  constructor(private mainScreenSelectorServce: MainScreenSelector, private serverConnector: ServerConectorService) { }

  ngOnInit(): void {
  }

  isSensorSelected()
  {
    return this.mainScreenSelectorServce.GetScreen() === MainScreenOptions.SENSORS
  }

  isStatusLogSelected()
  {
    return this.mainScreenSelectorServce.GetScreen() === MainScreenOptions.STATUS_LOG
  }

}
