import { Injectable } from '@angular/core';
import {SensorModule} from "../models/sensor-module"
import {MainScreenOptions} from "../enum/screen-type"
import { UiPanelService } from './ui-panels.service';
type Panel = Array<SensorModule> 

@Injectable({
  providedIn: 'root'
})
export class MainScreenSelector {
    
    canEdit = false
    screenOption: MainScreenOptions = MainScreenOptions.SENSORS
     
    constructor(private UiPanelsService: UiPanelService,) 
    { 
        
    }

    SelectScreen(option: MainScreenOptions, group: string|null)
    {
      this.screenOption = option
      if(group)
        this.UiPanelsService.SelectGroup(group)
    }

    GetScreen()
    {
      return this.screenOption;
    }

    toogleEdit()
    {
      this.canEdit = !this.canEdit
    }

    CanEdit()
    {
      return this.canEdit
    }

}
