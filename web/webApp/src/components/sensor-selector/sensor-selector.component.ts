import { Component, EventEmitter, Input, OnChanges, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { GetSensorTypeLabel, SensorModule } from '../../models/sensor-module';
import { SensorTypesEnum } from '../../enum/sensor-type';
import { GroupInfo } from '../../services/ui-panels.service';

/** One collapsible sensor section: the sensors of a single type inside a single group. */
export interface SensorSection {
  group: GroupInfo
  sensorType: SensorTypesEnum
  sensors: Array<SensorModule>
}

/** A group and its type sections, the outer fold of the sensor list. */
export interface SensorGroupSection {
  group: GroupInfo
  sections: Array<SensorSection>
}

/**
 * Groups -> sensor types -> sensors picker, shared by the graph and report dialogs.
 * Several groups can be picked at once, so one graph can mix panels of different groups.
 * The sensor list folds twice: a group row holds the type rows, and a type row holds its
 * sensors. Only the type rows carry a "select all" — a group has no single meaningful one.
 */
@Component({
  selector: 'sensor-selector',
  templateUrl: './sensor-selector.component.html',
  styleUrls: ['./sensor-selector.component.scss'],
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatIconModule,
    MatCheckboxModule
  ],
  standalone: true
})
export class SensorSelectorComponent implements OnChanges {

  @Input() uiConfig: { [id: string]: GroupInfo } = {}

  @Input() groups: Array<GroupInfo> = []
  @Output() groupsChange = new EventEmitter<Array<GroupInfo>>()

  @Input() sensors: Array<SensorModule> = []
  @Output() sensorsChange = new EventEmitter<Array<SensorModule>>()

  /** Selected sensor types; only their sensors are offered. */
  options: Array<SensorTypesEnum> = []

  /** Groups unfolded in the sensor selector, by group id; every group starts folded. */
  expandedGroups: Set<string> = new Set()

  /** Sections unfolded in the sensor selector, by section key; every section starts folded. */
  expandedSections: Set<string> = new Set()

  /**
   * Rebuilt only when the selection changes: the template iterates it, and fresh
   * objects on every change detection pass would tear down the options mat-select
   * holds the selection against.
   */
  groupSections: Array<SensorGroupSection> = []

  ngOnChanges(): void {
    this.buildSections()
  }

  getAvailableGroups(): GroupInfo[] {
    return Object.values(this.uiConfig)
  }

  /** Every sensor of a group, regardless of which panel bucket holds it. */
  private getGroupSensors(group: GroupInfo): Array<SensorModule> {
    return [
      ...group.panels.temperature,
      ...group.panels.pressure,
      ...group.panels.power
    ]
  }

  /** Every sensor of the selected groups, in the order the groups were listed. */
  private getSelectedGroupsSensors(): Array<SensorModule> {
    const sensors: Array<SensorModule> = []
    for (const group of this.getSelectedGroups()) {
      sensors.push(...this.getGroupSensors(group))
    }
    return sensors
  }

  /** Selected groups in the order the config lists them, so sections keep a stable order. */
  getSelectedGroups(): Array<GroupInfo> {
    return this.getAvailableGroups().filter(x => this.groups.includes(x))
  }

  /** Sensor types actually present in the selected groups, in the order they appear. */
  getAvailableTypes(): Array<SensorTypesEnum> {
    const types: Array<SensorTypesEnum> = []
    for (const sensor of this.getSelectedGroupsSensors()) {
      if (!types.includes(sensor.sensorType)) {
        types.push(sensor.sensorType)
      }
    }
    return types
  }

  getTypeLabel(sensorType: SensorTypesEnum): string {
    return GetSensorTypeLabel(sensorType)
  }

  /** With several types picked, the sensor list needs to say which is which. */
  getSensorOptionLabel(sensor: SensorModule): string {
    if (this.options.length < 2) {
      return sensor.name
    }
    return `${sensor.name} — ${this.getTypeLabel(sensor.sensorType)}`
  }

  /**
   * One row per selected group, holding one section per type that group actually has.
   * A group with no sensor of any selected type is left out entirely.
   */
  private buildSections(): void {
    const groupSections: Array<SensorGroupSection> = []

    for (const group of this.getSelectedGroups()) {
      const sections: Array<SensorSection> = []

      for (const sensorType of this.getAvailableTypes()) {
        if (!this.options.includes(sensorType)) {
          continue
        }
        const sensors = this.getGroupSensors(group).filter(x => x.sensorType == sensorType)
        if (sensors.length > 0) {
          sections.push({ group: group, sensorType: sensorType, sensors: sensors })
        }
      }

      if (sections.length > 0) {
        groupSections.push({ group: group, sections: sections })
      }
    }

    this.groupSections = groupSections
  }

  private getGroupKey(groupSection: SensorGroupSection): string {
    return String(groupSection.group.id)
  }

  private getSectionKey(section: SensorSection): string {
    return `${section.group.id}:${section.sensorType}`
  }

  countSensorsOfGroup(groupSection: SensorGroupSection): number {
    return groupSection.sections.reduce((total, x) => total + x.sensors.length, 0)
  }

  countSelectedOfGroup(groupSection: SensorGroupSection): number {
    return groupSection.sections.reduce((total, x) => total + this.countSelectedOfSection(x), 0)
  }

  isGroupCollapsed(groupSection: SensorGroupSection): boolean {
    return !this.expandedGroups.has(this.getGroupKey(groupSection))
  }

  toggleGroupCollapsed(groupSection: SensorGroupSection): void {
    const key = this.getGroupKey(groupSection)
    if (this.expandedGroups.has(key)) {
      this.expandedGroups.delete(key)
    } else {
      this.expandedGroups.add(key)
    }
  }

  countSelectedOfSection(section: SensorSection): number {
    return section.sensors.filter(x => this.sensors.includes(x)).length
  }

  isSectionCollapsed(section: SensorSection): boolean {
    return !this.expandedSections.has(this.getSectionKey(section))
  }

  toggleSectionCollapsed(section: SensorSection): void {
    const key = this.getSectionKey(section)
    if (this.expandedSections.has(key)) {
      this.expandedSections.delete(key)
    } else {
      this.expandedSections.add(key)
    }
  }

  areAllOfSectionSelected(section: SensorSection): boolean {
    return this.countSelectedOfSection(section) == section.sensors.length
  }

  setAllOfSectionSelected(section: SensorSection, selected: boolean): void {
    const others = this.sensors.filter(x => !section.sensors.includes(x))
    this.setSensors(selected ? [...others, ...section.sensors] : others)
  }

  onGroupsChange(groups: Array<GroupInfo>): void {
    this.groups = groups
    this.groupsChange.emit(groups)

    // Keep what still has a group behind it; a dropped group takes its types and sensors with it
    const available = this.getAvailableTypes()
    this.options = this.options.filter(x => available.includes(x))
    this.expandedGroups = new Set(
      [...this.expandedGroups].filter(x => groups.some(g => String(g.id) == x)))
    const remaining = this.getSelectedGroupsSensors()
    this.setSensors(this.sensors.filter(x => remaining.includes(x) && this.options.includes(x.sensorType)))
    this.buildSections()
  }

  onTypesChange(): void {
    // Drop sensors whose type is no longer selected, so they can't ride along unseen
    this.setSensors(this.sensors.filter(x => this.options.includes(x.sensorType)))
    this.buildSections()
  }

  setSensors(sensors: Array<SensorModule>): void {
    this.sensors = sensors
    this.sensorsChange.emit(sensors)
  }
}
