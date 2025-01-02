import { Component, OnInit } from '@angular/core';
import {MainScreenSelector} from "../../services/main-screen-selector.service"
import {MainScreenOptions} from "../../enum/screen-type"

@Component({
  selector: 'app-main-screen',
  templateUrl: './main-screen.component.html',
  styleUrls: ['./main-screen.component.scss']
})
export class MainScreenComponent implements OnInit {

  constructor(private mainScreenSelectorServce: MainScreenSelector) { }

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
