import { Injectable } from '@angular/core';
import {UiPanelService} from './ui-panels.service'
import { v4 as uuidv4 } from 'uuid';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { ErrorDialogComponent } from 'src/components/error-dialog/error-dialog.component';
import { SpinnerComponent } from 'src/components/spinner/spinner.component';

@Injectable({
  providedIn: 'root'
})
export class ServerConectorService {
  private socket: WebSocket | null;
  private wsUrl = 'ws://localhost:8888/websocket'

  //private reconnectAttempts: number = 0;
  private reconnectDelay: number = 2000;

  private dialogRef: MatDialogRef<SpinnerComponent> | null = null;

  constructor(private uiPanelService: UiPanelService, private dialog: MatDialog) { 
    this.socket = null
    setTimeout(()=>{
      this.connectToServer();
    }, 100)
    
  }

  private connectToServer(): void {
    this.showSpinnerDialog();
    this.socket = new WebSocket(this.wsUrl);

    this.socket.onmessage = (message) => {this.onMessage(message)}

    this.socket.onclose = () => {this.onDisconnection()}

    this.socket.onerror = (err) => {this.onError(err)}

    this.socket.onopen = () => {
      console.log('WebSocket connected successfully!');
      //this.reconnectAttempts = 0;  // Reset reconnect attempts on successful connection
    };
  }

  private showSpinnerDialog(): void {
    if(!this.dialogRef) {
      this.dialogRef = this.dialog.open(SpinnerComponent, {
        disableClose: true,
        panelClass: 'transparent-dialog',
        backdropClass: 'dimmed-backdrop',
      });
    }
   
  }

  private hideSpinnerDialog(): void {
    this.dialogRef?.close();
    this.dialogRef = null;
  }

  private onDisconnection()
  {
    if(this.handleReconnection)
    {
      this.handleReconnection();
    }
      
  }

  private handleReconnection() {
    setTimeout(() => {
      //console.log(`Attempting reconnection (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})...`);
      //this.reconnectAttempts++;
      this.connectToServer();
    }, this.reconnectDelay);
    this.reconnectDelay *= 2; // Exponential backoff
  }

  private openErrorDialog(message: string): void {
    this.dialog.open(ErrorDialogComponent, {
      width: '400px',
      data: { message },
    });
  }

  public formatLocalDateToCustomString(date: Date) {
    // Get local time components
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // months are 0-based
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    const milliseconds = String(date.getMilliseconds()).padStart(3, '0');
  
    // Generate microseconds (can be random or based on more precise sources)
    const microseconds = '000000'; // You could generate this or extract from more precise sources
  
    // Combine them into the required format
    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${milliseconds}${microseconds}`;
  }


  public sendRequestForTableInfo(sensorInfos: Array<any>, callback?: Function, beginDate?: Date|null, endDate?: Date|null)
  {
    const requestId = uuidv4();
    let obj: any = {"sensorInfos": sensorInfos, "requestId": requestId}
    if(beginDate)
    {
      obj["beginDate"] = this.formatLocalDateToCustomString(beginDate)
      if(endDate)
      {
        obj["endDate"] = this.formatLocalDateToCustomString(endDate)
      }
    }

    this.uiPanelService.AddGraphRequest(sensorInfos, requestId, callback)
    this.sendCommand("getStatusHistory", obj)
  }

  public sendCommand(commandName: string, payload: any)
  {
    if (this.socket?.readyState === WebSocket.OPEN) {
      let obj = {
        "commandName": commandName,
        "payload": payload
      }
      this.socket?.send(JSON.stringify(obj));
    } else {
      console.error('WebSocket is not open. Message not sent.');
    }
  }

  private onMessage(message: any): void {
    console.log('Received message:', message);
    let data = JSON.parse(message["data"])
    if(data["status"] == "uiConfig")
    {
      this.uiPanelService.SetNewUiConfig(data["message"])
      this.hideSpinnerDialog();
    }
    else if(data["status"] == "sensorUpdate")
    {
      let message = data["message"]
      this.uiPanelService.OnSubscriptionUpdate(message["subStatusName"], message["data"])
    }
    else if(data["status"] == "statusInfo")
    {
      let message = data["message"]
      this.uiPanelService.OnStatusInfoUpdate(message["data"].requestId, message["data"].info)
    }
    else if(data["status"] == "error")
    {
      this.openErrorDialog(data["message"])
    }
    else
    {
      console.log("Status " + data["status"] + " not found")
    }
  }

  // Handle WebSocket errors
  private onError(err: any): void {
    console.error('WebSocket error:', err);
    // You could reconnect here if necessary
  }
}
