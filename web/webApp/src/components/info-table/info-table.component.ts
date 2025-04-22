import { Component, OnInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';

@Component({
    selector: 'info-table',
    templateUrl: './info-table.component.html',
    styleUrls: ['./info-table.component.scss'],
    imports: [CommonModule, MatTableModule],
    standalone: true
})
export class InfoTableComponent {

  @Input() tableInfo: Array<any> = []
  @Input() fieldsInfo: Array<Array<string>> = []

  constructor() { }

  getFieldsInfo()
  {
    let array = []
    for(let field of this.fieldsInfo)
    {
      array.push(field[0])
    }

    return array;
  }

}
