import { Component, OnInit } from '@angular/core';
import {ServerConectorService} from "../../services/server-conector.service"

@Component({
  selector: 'table-view',
  templateUrl: './table-view.component.html',
  styleUrls: ['./table-view.component.scss']
})
export class TableViewComponent implements OnInit {

  constructor(private serverConnector: ServerConectorService) { 
    //this.getTable()
  }

  refreshing: boolean = false
  array: Array<any> = []
  /*[
    {"person": 'Thomas Turbando', "time": new Date(Date.now()).toISOString()},
    {"person": 'Jalin Habei', "time": new Date(Date.now()).toISOString()},
    {"person": 'Oscar Alho', "time": new Date(Date.now()).toISOString()},
    {"person": 'Paula Noku', "time": new Date(Date.now()).toISOString()},
    {"person": 'Cuca Beludo', "time": new Date(Date.now()).toISOString()},
    {"person": 'Ana Konda', "time": new Date(Date.now()).toISOString()},
    {"person": 'Caio Pinto', "time": new Date(Date.now()).toISOString()}
  ]*/
  headerInfo: Array<any> = [["value", "Pessoa"], ["timestamp","Data"]]//['value', 'timestamp']
  gateway: string = ""
  table: string = "tag"

  ngOnInit(): void {}

  getTable(): void{
    this.refreshing = true
    this.serverConnector.sendRequestForTableInfo(this.gateway, this.table, (value: any)=>{
      this.array = value.info
      this.refreshing = false
    })

  }

}
