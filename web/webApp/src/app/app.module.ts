import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

//Project Screen Components
import { MainScreenComponent } from 'src/panels/main-screen/main-screen.component';
import { NavbarComponent } from 'src/panels/navbar/navbar.component';

//Project Components
import { SensorAddWindowComponent } from 'src/components/sensor-add-window/sensor-add-window.component';
import { SensorComponent } from 'src/components/sensor/sensor.component';
import { SideNavOptionComponent } from 'src/components/side-nav-option/side-nav-option.component';

//Angular Material
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatIconModule} from '@angular/material/icon';
import {MatButtonModule} from '@angular/material/button'; 
import {MatDialogModule} from '@angular/material/dialog'; 

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
  declarations: [
    AppComponent,
    MainScreenComponent,
    SensorComponent,
    SideNavOptionComponent,
    NavbarComponent,
    SensorAddWindowComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,

    BrowserAnimationsModule,
    MatSidenavModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatDialogModule
  ],
  entryComponents: [SensorAddWindowComponent],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
