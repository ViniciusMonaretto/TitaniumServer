import { Injectable } from '@angular/core';
import {SensorModule} from "../models/sensor-module"
import {MainScreenOptions} from "../enum/screen-type"
type Panel = Array<SensorModule> 

@Injectable({
  providedIn: 'root'
})
export class MainScreenSelector {
    
    screenOption: MainScreenOptions = MainScreenOptions.STATUS_LOG
    
    constructor() 
    { 
        
    }

    SelectScreen(option: MainScreenOptions)
    {
      this.screenOption = option
    }

    GetScreen()
    {
      return this.screenOption;
    }

}
