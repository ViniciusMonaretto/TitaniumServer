import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

@Injectable({
  providedIn: 'root'
})
export class ServerConectorService {
  private socket: WebSocketSubject<any>;
  private wsUrl = 'http://localhost:8888/websocket'

  constructor() { 
    this.socket = webSocket(this.wsUrl);
    this.connect();
  }

  private connect(): void {
    

    // Handle incoming messages
    this.socket.subscribe({
      next: (message) => this.onMessage(message),
      error: (err) => this.onError(err),
      complete: () => console.log('WebSocket connection closed')
    });
  }

  private onMessage(message: any): void {
    console.log('Received message:', message);
    // Process the message as needed
  }

  // Handle WebSocket errors
  private onError(err: any): void {
    console.error('WebSocket error:', err);
    // You could reconnect here if necessary
  }
}
