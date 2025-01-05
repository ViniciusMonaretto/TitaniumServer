import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'info-table',
  templateUrl: './info-table.component.html',
  styleUrls: ['./info-table.component.scss']
})
export class InfoTableComponent {

  @Input() tableInfo: Array<any> = []
  @Input() fieldsInfo: Array<string> = []

  constructor() { }

}
