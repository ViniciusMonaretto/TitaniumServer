import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { MainScreenComponent } from 'src/panels/main-screen/main-screen.component';

const routes: Routes = [
  { path: 'main', component: MainScreenComponent }, // Define the route for MyComponent
  { path: '', redirectTo: '/main', pathMatch: 'full' } // Redirect to a default route
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
