import { Injectable } from '@angular/core';
import {UiPanelService} from './ui-panels.service'
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { SensorModule } from 'src/models/sensor-module';

@Injectable({
  providedIn: 'root'
})
export class ServerConectorService {
  private socket: WebSocket | null;
  private wsUrl = 'ws://localhost:8888/websocket'

  private tableCallbacks = new Map<string, Array<Function>>()

  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;
  private reconnectDelay: number = 2000;
  constructor(private uiPanelService: UiPanelService) { 
    this.socket = null
    setTimeout(()=>{
      this.connectToServer();
    }, 100)
    
  }

  private connectToServer(): void {
    this.socket = new WebSocket(this.wsUrl);

    this.socket.onmessage = (message) => {this.onMessage(message)}

    this.socket.onclose = () => {this.onDisconnection()}

    this.socket.onerror = (err) => {this.onError(err)}

    this.tableCallbacks =  new Map<string, Array<Function>>()

    this.socket.onopen = () => {
      console.log('WebSocket connected successfully!');
      this.reconnectAttempts = 0;  // Reset reconnect attempts on successful connection
    };
  }

  private onDisconnection()
  {
    if(this.handleReconnection)
    {
      this.handleReconnection();
    }
      
  }

  private handleReconnection() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        console.log(`Attempting reconnection (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})...`);
        this.reconnectAttempts++;
        this.connectToServer();
      }, this.reconnectDelay);
      this.reconnectDelay *= 2; // Exponential backoff
    } else {
      console.error('Max reconnection attempts reached.');
    }
  }

  public addCallbackTable(gateway: string| null, table: string, callback: Function)
  {
    let tableFullName = gateway == ""?table:gateway + '-' + table
    if(!this.tableCallbacks.has(tableFullName))
    {
      this.tableCallbacks.set(tableFullName, [])
    }
    this.tableCallbacks.get(tableFullName)?.push(callback)
    return 
  }

  public sendRequestForTableInfo(gateway: string| null, table: string, callback: Function)
  {
    this.addCallbackTable(gateway, table, callback)
    this.sendCommand("getStatusHistory", {"gateway": gateway, "table": table})
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
    }
    else if(data["status"] == "sensorUpdate")
    {
      let message = data["message"]
      this.uiPanelService.OnSubscriptionUpdate(message["subStatusName"], message["data"])
    }
    else if(data["status"] == "statusInfo")
    {
      let message = data["message"]
      if(this.tableCallbacks.has(message["data"]["tableName"]))
      { 
        this.tableCallbacks.get(message["data"]["tableName"])?.forEach(tableCallback => {
          tableCallback(message["data"])
        });
        
      }
    }
  }

  // Handle WebSocket errors
  private onError(err: any): void {
    console.error('WebSocket error:', err);
    // You could reconnect here if necessary
  }
}
