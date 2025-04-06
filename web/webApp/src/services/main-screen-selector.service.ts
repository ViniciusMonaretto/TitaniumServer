import { Injectable } from '@angular/core';
import {SensorModule} from "../models/sensor-module"
import {MainScreenOptions} from "../enum/screen-type"
type Panel = Array<SensorModule> 

@Injectable({
  providedIn: 'root'
})
export class MainScreenSelector {
    
    screenOption: MainScreenOptions = MainScreenOptions.SENSORS
    selectedGroup: string|null = ""
    
    constructor() 
    { 
        
    }

    SelectScreen(option: MainScreenOptions, group: string|null)
    {
      this.screenOption = option
      this.selectedGroup = group
    }

    GetScreen()
    {
      return this.screenOption;
    }

}
