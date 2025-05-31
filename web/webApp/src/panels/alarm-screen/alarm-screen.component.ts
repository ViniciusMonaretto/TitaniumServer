import { Component, OnInit } from '@angular/core';

import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { IoCloudTableComponent } from '../../components/io-cloud-table/io-cloud-table.component';
import { MatDialog } from '@angular/material/dialog';
import { AlarmAddWindowComponent } from '../../components/alarm-add-window/alarm-add-window.component';
import { UiPanelService } from '../../services/ui-panels.service';

@Component({
    selector: 'alert-screen',
    templateUrl: './alarm-screen.component.html',
    styleUrls: ['./alarm-screen.component.scss'],
    imports: [CommonModule, 
              MatIconModule, 
              MatCardModule,
              IoCloudTableComponent],
    standalone: true
})
export class AlarmViewComponent implements OnInit {
  headerInfo: string[][] = [["Panel", "Medição"], ["Trigger", "Trigger"], ["Value", "Valor"]]
  alarms: any = []

  constructor(public dialog: MatDialog, private uiPanelService: UiPanelService)
  {

  }

  ngOnInit(): void {
   
  }

  addAlarm(): void {
      const dialogRef = this.dialog.open(AlarmAddWindowComponent, {
        width: '300px',
        data: {callback: (sensorData: any)=>{
          
        },
         uiConfig: this.uiPanelService.GetUiConfig()
      }
      });
    }
}
