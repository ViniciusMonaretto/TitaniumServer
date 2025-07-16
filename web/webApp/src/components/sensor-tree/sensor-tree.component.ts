import { Component, Input, Output } from '@angular/core';
import { MatTreeModule, MatTreeNestedDataSource } from '@angular/material/tree';
import {MatCheckboxModule} from '@angular/material/checkbox';
import { CommonModule } from '@angular/common';
import { PanelInfo } from '../../services/ui-panels.service';
import { SensorModule } from '../../models/sensor-module';
import { NestedTreeControl } from '@angular/cdk/tree';
import { SelectionModel } from '@angular/cdk/collections';
import {MatIconModule} from '@angular/material/icon';
import { SensorTypesEnum } from '../../enum/sensor-type';

export interface TreeNode {
  name: string;
  icon: string;
  object?: SensorModule|SensorModule[]|null;
  children?: TreeNode[];
}

@Component({
  selector: 'sensor-tree',
  imports: [CommonModule,
            MatTreeModule,
            MatCheckboxModule,
            MatIconModule],
  templateUrl: './sensor-tree.component.html',
  styleUrl: './sensor-tree.component.scss',
  standalone: true
})
export class SensorTreeComponent {
  treeControl = new NestedTreeControl<TreeNode>(node => node.children);
  dataSource = new MatTreeNestedDataSource<TreeNode>();
  
  @Input() panelsInfo: { [id: string]: PanelInfo } = {};
  @Input() selectedSensors!: { [id: string]: SensorModule }; // mutable

  constructor()
  {

  }

  ngOnInit(): void {
    this.buildTreeData();
  }

  hasChild = (_: number, node: TreeNode) => !!node.children?.length;

  isSelected(node: TreeNode): boolean {
    return this.selectedSensors[node.name] !== undefined;
  }

  toggleNodeSelection(node: TreeNode): void {
    if (node.object) {
      if (Array.isArray(node.object) || false) {
        
      } else {
        if (this.selectedSensors[node.object.name] === undefined) {
          this.selectedSensors[node.object.name] = node.object;
        } else {
          delete this.selectedSensors[node.object.name];
        }
      }
    }
  }

  private getPanelSensors(panel: PanelInfo): SensorModule[] {
    return [...panel.temperature, ...panel.pressure, ...panel.power];
  }

  private buildTreeData(): void {
    const tree: TreeNode[] = []

    for (const panelId in this.panelsInfo) {
      const panel = this.panelsInfo[panelId];
      const panelNode: TreeNode = {
        name: panelId,
        icon: "dashboard",
        object: this.getPanelSensors(panel),
        children: [
          {
            name: "Temperatura",
            object: panel.temperature,
            icon: "whatshot",
            children: panel.temperature.map(sensor => ({
              name: sensor.name,
              icon: "av_timer",
              object: sensor
            }))
          },
          {
            name: "Pressão",
            object: panel.pressure,
            icon: "av_timer",
            children: panel.pressure.map(sensor => ({
              name: sensor.name,  
              object: sensor,
              icon: "av_timer"
            }))
          },
          {
            name: "Potência", 
            object: panel.power,
            icon: "offline_bolt",
            children: panel.power.map(sensor => ({
              name: sensor.name,
              icon: "av_timer",
              object: sensor
            }))
          }
        ]
      };
      tree.push(panelNode);
    }

    this.dataSource.data = tree;
  }
}
