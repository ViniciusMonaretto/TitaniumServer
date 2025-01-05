import { Component, OnInit } from '@angular/core';
import {ServerConectorService} from "../../services/server-conector.service"

@Component({
  selector: 'table-view',
  templateUrl: './table-view.component.html',
  styleUrls: ['./table-view.component.scss']
})
export class TableViewComponent implements OnInit {

  constructor(private serverConnector: ServerConectorService) { }

  array: Array<any> = []
  headerInfo: Array<any> = ['value', 'timestamp']

  ngOnInit(): void {
  }

  getTAble(): void{
    this.serverConnector.sendRequestForTableInfo("1C692031BE04", "temperature", (value: any)=>{
      this.array = value.info
    })

  }

}
