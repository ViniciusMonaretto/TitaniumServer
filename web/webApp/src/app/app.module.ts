import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms'; // Import FormsModule

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

//Project Screen Components
import { MainScreenComponent } from 'src/panels/main-screen/main-screen.component';
import { SensorGroupComponent } from 'src/panels/sensor-group/sensor-group.component';
import { NavbarComponent } from 'src/panels/navbar/navbar.component';

//Project Components
import { SensorAddWindowComponent } from 'src/components/sensor-add-window/sensor-add-window.component';
import { SensorComponent } from 'src/components/sensor/sensor.component';
import { SideNavOptionComponent } from 'src/components/side-nav-option/side-nav-option.component';
import { GroupOfSensorsComponent } from 'src/components/group-of-sensors/group-of-sensors.component';

//Angular Material
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatIconModule} from '@angular/material/icon';
import {MatButtonModule} from '@angular/material/button'; 
import {MatDialogModule} from '@angular/material/dialog'; 
import {MatFormFieldModule} from '@angular/material/form-field'; 
import { MatSelectModule } from '@angular/material/select'; 
import { MatInputModule } from '@angular/material/input'; 
import {MatCardModule} from '@angular/material/card'; 


import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
  declarations: [
    AppComponent,
    MainScreenComponent,
    SensorComponent,
    SideNavOptionComponent,
    NavbarComponent,
    SensorAddWindowComponent,
    SensorGroupComponent,
    GroupOfSensorsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,

    BrowserAnimationsModule,
    MatSidenavModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatCardModule
  ],
  entryComponents: [SensorAddWindowComponent],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
