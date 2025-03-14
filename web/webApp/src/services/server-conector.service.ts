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


  public sendRequestForTableInfo(gateway: string| null, table: string, timestamp?: Date | null)
  {
    let obj: any = {"gateway": gateway, "table": table}
    if(timestamp)
    {
      obj["timestamp"] = this.formatLocalDateToCustomString(timestamp)
    }
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
    }
    else if(data["status"] == "sensorUpdate")
    {
      let message = data["message"]
      this.uiPanelService.OnSubscriptionUpdate(message["subStatusName"], message["data"])
    }
    else if(data["status"] == "statusInfo")
    {
      let message = data["message"]
      this.uiPanelService.OnSubscriptionUpdate(message["data"].tableName, message["data"].info)
    }
  }

  // Handle WebSocket errors
  private onError(err: any): void {
    console.error('WebSocket error:', err);
    // You could reconnect here if necessary
  }
}
