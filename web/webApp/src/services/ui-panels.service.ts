import { Injectable } from '@angular/core';
import {SensorModule} from "../models/sensor-module"
type Panel = Array<SensorModule> 

@Injectable({
  providedIn: 'root'
})
export class UiPanelService {
    
    panels: {[id: string]:Panel} = {}
    
    constructor() 
    { 
        
    }

    SetNewUiConfig(uiConfig: Panel )
    {
        this.panels["base"] = uiConfig 
    }

    GetUiConfig()
    {
      return this.panels
    }

}
