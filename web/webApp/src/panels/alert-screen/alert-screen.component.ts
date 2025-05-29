import { Component, OnInit } from '@angular/core';

import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { IoCloudTableComponent } from '../../components/io-cloud-table/io-cloud-table.component';

@Component({
    selector: 'alert-screen',
    templateUrl: './alert-screen.component.html',
    styleUrls: ['./alert-screen.component.scss'],
    imports: [CommonModule, 
              MatIconModule, 
              MatCardModule,
              IoCloudTableComponent],
    standalone: true
})
export class AlertViewComponent implements OnInit {
  headerInfo: string[][] = [["Panel", "Medição"], ["Trigger", "Trigger"], ["Value", "Valor"]]
  alarms: any = []

  ngOnInit(): void {
   
  }
}
