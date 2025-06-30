import { Component, OnInit } from '@angular/core';

import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { IoCloudTableComponent } from '../../components/io-cloud-table/io-cloud-table.component';
import { MatDialog } from '@angular/material/dialog';
import { UiPanelService } from '../../services/ui-panels.service';
import { EventAlarmManagerService } from '../../services/event-alarm-manager.service';
import { DialogHelper } from '../../services/dialog-helper.service';

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

  constructor(private dialogHelper: DialogHelper, 
    private eventsService: EventAlarmManagerService)
  {

  }

  eraseAllEvents()
  {
    this.dialogHelper.openQuestionDialog("Apagar eventos", 
      "Deseja limpar todos os eventos?",
      () =>
      {
        this.eventsService.removeAllEvents()
      })
  }

  ngOnInit(): void {

  }

  getEvents() {
    return this.eventsService.getEvents()
  }
}
