import { Injectable, Inject, InjectionToken } from '@angular/core';
import { UiPanelService } from './ui-panels.service'
import { v4 as uuidv4 } from 'uuid';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { SpinnerComponent } from '../components/spinner/spinner.component';
import { EventAlarmModule } from '../models/event-alarm-module';
import { DialogHelper } from './dialog-helper.service';

export const WS_URL_TOKEN = new InjectionToken<string>('wsUrl');

@Injectable({
  providedIn: 'root'
})
export class ServerConectorService {
  private socket: WebSocket | null;
  private wsUrl: string;

  private isConnecting: boolean = false

  //private reconnectAttempts: number = 0;
  private reconnectDelay: number = 2000;
  private alarmRequest: ((alarms: any) => void) | null = null;
  private addAlarmRequest: ((alarms: any) => void) | null = null;
  private removeAlarmRequest: ((alarms: any) => void) | null = null;
  private receivedEventsCallback: ((events: EventAlarmModule[], replaceValue: boolean) => void) | null = null;
  private afterConnectRequests: Function[] = []

  constructor(
    private uiPanelService: UiPanelService,
    private dialogHelper: DialogHelper,
    @Inject(WS_URL_TOKEN) wsUrl: string = 'ws://localhost:8888/websocket'
  ) {
    this.wsUrl = 'ws://localhost:8888/websocket';//wsUrl;
    this.socket = null
    setTimeout(() => {
      this.connectToServer();
    }, 100)
    this.addOnConnectCallback(() => {
      this.sendCommand("getGateways", {})
    })
  }

  addOnConnectCallback(callback: Function) {
    this.afterConnectRequests.push(callback)
  }

  private runOpenCommands() {
    for (var callback of this.afterConnectRequests) {
      callback();
    }
  }


  public setAlarmInfoCallback(callback: (alarms: any) => void): void {
    this.alarmRequest = callback;
  }

  public setAddAlarmCallback(callback: (alarm: any) => void): void {
    this.addAlarmRequest = callback;
  }

  public setRemoveAlarmCallback(callback: (alarm: any) => void): void {
    this.removeAlarmRequest = callback;
  }

  public setReceivedEventsCallback(callback: (data: any, replace: boolean) => void): void {
    this.receivedEventsCallback = callback;
  }

  private connectToServer(): void {
    this.dialogHelper.showSpinnerDialog();
    this.socket = new WebSocket(this.wsUrl);
    this.isConnecting = true

    this.socket.onmessage = (message) => { this.onMessage(message) }

    this.socket.onclose = () => { this.onDisconnection() }

    this.socket.onerror = (err) => { this.onError(err) }

    this.socket.onopen = () => {
      console.log('WebSocket connected successfully!');
    };
  }

  private onDisconnection() {
    if (this.handleReconnection) {
      this.handleReconnection();
    }

  }

  private handleReconnection() {
    setTimeout(() => {
      //console.log(`Attempting reconnection (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})...`);
      //this.reconnectAttempts++;
      this.connectToServer();
    }, this.reconnectDelay);
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

  public sendRequestForTableInfo(sensorInfos: Array<any>,
    group: string,
    beginDate?: Date | null,
    endDate?: Date | null,
    callback?: Function) {
    const requestId = uuidv4();
    let obj: any = { "sensorInfos": sensorInfos, "requestId": requestId }
    if (beginDate) {
      obj["beginDate"] = this.formatLocalDateToCustomString(beginDate)
      if (endDate) {
        obj["endDate"] = this.formatLocalDateToCustomString(endDate)
      }
    }

    this.uiPanelService.AddGraphRequest(sensorInfos, requestId, group, callback)
    this.sendCommand("getStatusHistory", obj)
  }

  public sendRequestForReportInfo(sensorInfos: Array<any>,
    group: string,
    beginDate?: Date | null,
    endDate?: Date | null) {
    const requestId = uuidv4();
    let obj: any = { "sensorInfos": sensorInfos, "requestId": requestId }
    if (beginDate) {
      obj["beginDate"] = this.formatLocalDateToCustomString(beginDate)
      if (endDate) {
        obj["endDate"] = this.formatLocalDateToCustomString(endDate)
      }
    }

    this.sendCommand("generaterReport", obj)
  }

  public sendCommand(commandName: string, payload: any) {
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

  private createEventModel(eventInfo: any) {
    var evt = new EventAlarmModule()
    var panel = this.uiPanelService.GetPanelById(eventInfo["panelId"])

    evt.id = eventInfo["id"]
    evt.name = eventInfo["name"]
    evt.alarmId = eventInfo["alarmId"]
    evt.panelId = eventInfo["panelId"]
    evt.value = eventInfo["value"]
    evt.timestamp = eventInfo["timestamp"]

    if (panel) {
      evt.panelType = panel.sensorType
      evt.panelName = panel.name
    }

    return evt;
  }

  private onMessage(message: any): void {
    console.log('Received message:', message);
    let data = JSON.parse(message["data"])
    if (data["status"] == "uiConfig") {
      this.uiPanelService.SetNewUiConfig(data["message"]["PanelsInfo"])

      if (data["message"]["calibrateUpdate"]) {
        this.dialogHelper.openInfoDialog("Novo valor calibrado no Sensor, verifique o valor.", "Calibração concluída")
      }

      if (this.isConnecting) {
        this.isConnecting = false
        this.dialogHelper.hideSpinnerDialog();
        this.runOpenCommands();
      }

    }
    else if (data["status"] == "sensorUpdate") {
      let message = data["message"]
      this.uiPanelService.OnSubscriptionUpdate(message["subStatusName"], message["data"])
    }
    else if (data["status"] == "statusInfo") {
      let message = data["message"]
      this.uiPanelService.OnStatusInfoUpdate(message["data"].requestId, message["data"].info)
    }
    else if (data["status"] == "alarmInfo") {
      let message = data["message"]
      if (this.alarmRequest) {
        this.alarmRequest(message['data'])
      }
    }
    else if (data["status"] == "alarmAdded") {
      let message = data["message"]
      if (this.addAlarmRequest) {
        this.addAlarmRequest(message['data'])
      }
    }
    else if (data["status"] == "alarmRemoved") {
      let message = data["message"]
      if (this.removeAlarmRequest) {
        this.removeAlarmRequest(message)
      }
    }
    else if (data["status"] == "gatewayStatus") {
      let message = data["message"]
      this.uiPanelService.UpdateGateways(message['data'])
    }
    else if (data["status"] == "eventListResponse") {
      let message = data["message"]
      if (this.receivedEventsCallback) {
        var events: Array<EventAlarmModule> = []

        message['data']["events"].forEach((x: any) => {
          events.push(this.createEventModel(x));
        })
        this.receivedEventsCallback(events, true)
      }
    }
    else if (data["status"] == "eventInfoUpdate") {
      let message = data["message"]
      if (this.receivedEventsCallback) {
        this.receivedEventsCallback([this.createEventModel(message)], false)
      }
    }
    else if (data["status"] == "report") {
      let message = data["message"];
      const link = document.createElement('a');
      link.href = `data:${message.mimetype};base64,${message.filedata}`;
      link.download = message.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
    else if (data["status"] == "error") {
      this.dialogHelper.openErrorDialog(data["message"]["data"])
    }
    else {
      console.log("Status " + data["status"] + " not found")
    }
  }

  // Handle WebSocket errors
  private onError(err: any): void {
    console.error('WebSocket error:', err);
    // You could reconnect here if necessary
  }
}
