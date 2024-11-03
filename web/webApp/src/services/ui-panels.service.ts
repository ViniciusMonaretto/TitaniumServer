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

    SetNewUiConfig(uiConfig: {'panels': Panel} )
    {
        this.panels["base"] = uiConfig['panels']
    }

    GetUiConfig()
    {
      return this.panels
    }

}
