import { Component, OnInit } from '@angular/core';

import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { IoCloudTableComponent } from '../../components/io-cloud-table/io-cloud-table.component';
import { MatDialog } from '@angular/material/dialog';
import { UiPanelService } from '../../services/ui-panels.service';
import { EventAlarmManagerService } from '../../services/event-alarm-manager.service';

@Component({
    selector: 'event-screen',
    templateUrl: './alarm-screen.component.html',
    styleUrls: ['./alarm-screen.component.scss'],
    imports: [CommonModule, 
              MatIconModule, 
              MatCardModule,
              IoCloudTableComponent],
    standalone: true
})
export class AlarmViewComponent implements OnInit {
  headerInfo: string[][] = [["panelName", "Sensor"], ["panelType", "Tipo"], ["value", "Valor"], ["timestamp", "Data"]]

  constructor(public dialog: MatDialog, 
    private eventsService: EventAlarmManagerService)
  {

  }

  ngOnInit(): void {

  }

  getEvents() {
    return this.eventsService.getEvents()
  }
}
