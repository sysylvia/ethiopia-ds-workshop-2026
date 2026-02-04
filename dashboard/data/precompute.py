#!/usr/bin/env python3
"""
Pre-compute ABM scenario data for the animated dashboard.

This script runs all 8 scenarios and exports per-month data including:
- Stock levels at each supply chain level
- Shipment flows between nodes
- Shortage counts by medicine type
- Deaths by age group
- Wastage by medicine type
- Treatment rates

Usage:
    python precompute.py

Output:
    JSON files in ./scenarios/ directory
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

import numpy as np
import pandas as pd

# Add notebook directory to path to import ABM classes
NOTEBOOK_DIR = Path(__file__).parent.parent.parent / "notebooks"
sys.path.insert(0, str(NOTEBOOK_DIR))

# ============================================================================
# ABM Configuration (from notebook)
# ============================================================================

n_facilities = 100
n_months = 60
antibiotic_classes = ['Penicillins', 'Macrolides', 'Fluoroquinolones']
facility_ids = [f'CHC_{i:03d}' for i in range(1, n_facilities + 1)]

np.random.seed(42)
facility_populations = {fid: np.random.randint(5000, 50001) for fid in facility_ids}

class_params = {
    'Penicillins': {'base_demand_per_1000': 15, 'seasonal_amplitude': 0.3, 'peak_month': 1, 'trend': 0.02},
    'Macrolides': {'base_demand_per_1000': 8, 'seasonal_amplitude': 0.4, 'peak_month': 12, 'trend': 0.03},
    'Fluoroquinolones': {'base_demand_per_1000': 4, 'seasonal_amplitude': 0.1, 'peak_month': 7, 'trend': 0.01}
}

CONFIG = {
    'n_manufacturers': 2,
    'n_central_stores': 1,
    'n_hospitals': 3,
    'n_chcs': 100,
    'n_months': 60,
    'transit_time': 2,
    'order_lead_time': 2,
    'medicine_shelf_life': 12,
    'health_worker_absenteeism': 0.10,
    'incidence': {'child': 8.0, 'elderly': 5.0, 'adult': 2.0},
    'death_rates': {'elderly': 0.08, 'child': 0.05, 'adult': 0.02},
    'demographics': {'child': 0.35, 'adult': 0.55, 'elderly': 0.10},
    'manufacturer_capacity': 50000,
    'central_store_capacity': 100000,
    'hospital_capacity': 20000,
    'chc_capacity': 2000,
    'initial_stock_pct': 0.5,
    'antibiotic_classes': antibiotic_classes
}

# Assign CHCs to hospitals
def assign_chcs_to_hospitals(n_chcs: int, n_hospitals: int) -> Dict[int, List[str]]:
    assignments = {i: [] for i in range(n_hospitals)}
    chc_ids = [f'CHC_{i:03d}' for i in range(1, n_chcs + 1)]
    for idx, chc_id in enumerate(chc_ids):
        hospital_idx = idx % n_hospitals
        assignments[hospital_idx].append(chc_id)
    return assignments

CHC_HOSPITAL_ASSIGNMENTS = assign_chcs_to_hospitals(CONFIG['n_chcs'], CONFIG['n_hospitals'])


# ============================================================================
# Simplified ABM Classes (with shipment tracking)
# ============================================================================

class MedicineStatus(Enum):
    IN_TRANSIT = 'in_transit'
    IN_STOCK = 'in_stock'
    DISPENSED = 'dispensed'
    EXPIRED = 'expired'


class MedicineBatch:
    def __init__(self, medicine_type: str, quantity: int, manufacture_month: int, shelf_life: int = 12):
        self.medicine_type = medicine_type
        self.quantity = quantity
        self.manufacture_month = manufacture_month
        self.expiry_month = manufacture_month + shelf_life
        self.status = MedicineStatus.IN_STOCK

    def is_expired(self, current_month: int) -> bool:
        return current_month >= self.expiry_month


def generate_monthly_forecast(facility_id: str, month: int, year: int,
                              abx_class: str, outbreak_multiplier: float = 1.0) -> dict:
    population = facility_populations[facility_id]
    params = class_params[abx_class]
    base = params['base_demand_per_1000'] * (population / 1000)
    seasonal = params['seasonal_amplitude'] * np.sin(2 * np.pi * (month - params['peak_month']) / 12)
    years_from_start = (year - 1) + (month - 1) / 12
    trend = 1 + params['trend'] * years_from_start
    demand = base * (1 + seasonal) * trend * outbreak_multiplier
    return {'expected_demand': int(max(1, demand))}


class LocationAgent:
    def __init__(self, unique_id: str, model, capacity: int, location_type: str):
        self.unique_id = unique_id
        self.model = model
        self.capacity = capacity
        self.location_type = location_type
        self.inventory: Dict[str, List[MedicineBatch]] = defaultdict(list)
        self.incoming_shipments: List[Tuple[int, MedicineBatch]] = []
        self.total_expired = defaultdict(int)

    def get_stock_level(self, medicine_type: str) -> int:
        return sum(batch.quantity for batch in self.inventory[medicine_type]
                   if batch.status == MedicineStatus.IN_STOCK)

    def get_total_stock(self) -> int:
        return sum(self.get_stock_level(med) for med in CONFIG['antibiotic_classes'])

    def receive_shipment(self, batch: MedicineBatch):
        batch.status = MedicineStatus.IN_STOCK
        self.inventory[batch.medicine_type].append(batch)

    def process_incoming_shipments(self, current_month: int):
        arrived = []
        still_in_transit = []
        for arrival_month, batch in self.incoming_shipments:
            if current_month >= arrival_month:
                self.receive_shipment(batch)
                arrived.append(batch)
            else:
                still_in_transit.append((arrival_month, batch))
        self.incoming_shipments = still_in_transit
        return arrived

    def ship_to(self, destination: 'LocationAgent', medicine_type: str,
                quantity: int, transit_time: int, current_month: int) -> int:
        available_batches = sorted(
            [b for b in self.inventory[medicine_type]
             if b.status == MedicineStatus.IN_STOCK and b.quantity > 0],
            key=lambda b: b.expiry_month
        )
        shipped = 0
        for batch in available_batches:
            if shipped >= quantity:
                break
            take = min(batch.quantity, quantity - shipped)
            batch.quantity -= take
            shipped += take
            shipped_batch = MedicineBatch(
                medicine_type=medicine_type,
                quantity=take,
                manufacture_month=batch.manufacture_month,
                shelf_life=batch.expiry_month - batch.manufacture_month
            )
            shipped_batch.status = MedicineStatus.IN_TRANSIT
            arrival_month = current_month + transit_time
            destination.incoming_shipments.append((arrival_month, shipped_batch))
        self.inventory[medicine_type] = [b for b in self.inventory[medicine_type] if b.quantity > 0]

        # Track shipment for dashboard
        if shipped > 0:
            self.model.record_shipment(self.unique_id, destination.unique_id, medicine_type, shipped)

        return shipped

    def process_expiry(self, current_month: int) -> Dict[str, int]:
        expired = defaultdict(int)
        for med_type in list(self.inventory.keys()):
            valid_batches = []
            for batch in self.inventory[med_type]:
                if batch.is_expired(current_month):
                    expired[med_type] += batch.quantity
                    self.total_expired[med_type] += batch.quantity
                else:
                    valid_batches.append(batch)
            self.inventory[med_type] = valid_batches
        return dict(expired)


class ManufacturerAgent(LocationAgent):
    def __init__(self, unique_id: str, model, capacity: int):
        super().__init__(unique_id, model, capacity, 'manufacturer')
        self.monthly_production_capacity = capacity
        self.operational = True
        self.recovery_month = None

    def produce(self, current_month: int) -> Dict[str, int]:
        if not self.operational:
            if self.recovery_month and current_month >= self.recovery_month:
                self.operational = True
            else:
                return {}
        production_split = {'Penicillins': 0.60, 'Macrolides': 0.30, 'Fluoroquinolones': 0.10}
        produced = {}
        for med_type, pct in production_split.items():
            qty = int(self.monthly_production_capacity * pct)
            batch = MedicineBatch(med_type, qty, current_month, self.model.config['medicine_shelf_life'])
            self.inventory[med_type].append(batch)
            produced[med_type] = qty
        return produced

    def fail(self, current_month: int, recovery_months: int):
        self.operational = False
        self.recovery_month = current_month + recovery_months


class CentralMedicalStoreAgent(LocationAgent):
    def __init__(self, unique_id: str, model, capacity: int):
        super().__init__(unique_id, model, capacity, 'central_store')

    def distribute_to_hospitals(self, hospitals: List['HospitalAgent'], current_month: int, transit_time: int):
        for med_type in self.model.config['antibiotic_classes']:
            available = self.get_stock_level(med_type)
            if available == 0:
                continue
            total_chcs = sum(len(h.served_chcs) for h in hospitals)
            for hospital in hospitals:
                share = len(hospital.served_chcs) / total_chcs if total_chcs > 0 else 0
                allocation = int(available * share * 0.8)
                if allocation > 0:
                    self.ship_to(hospital, med_type, allocation, transit_time, current_month)


class HospitalAgent(LocationAgent):
    def __init__(self, unique_id: str, model, capacity: int, served_chc_ids: List[str]):
        super().__init__(unique_id, model, capacity, 'hospital')
        self.served_chc_ids = served_chc_ids
        self.served_chcs: List['CommunityHealthCenterAgent'] = []

    def distribute_to_chcs(self, current_month: int, transit_time: int):
        for med_type in self.model.config['antibiotic_classes']:
            available = self.get_stock_level(med_type)
            if available == 0:
                continue
            total_demand = sum(chc.get_forecast(current_month, med_type)['expected_demand'] for chc in self.served_chcs)
            if total_demand == 0:
                continue
            for chc in self.served_chcs:
                forecast = chc.get_forecast(current_month, med_type)
                share = forecast['expected_demand'] / total_demand
                allocation = int(available * share * 0.9)
                if allocation > 0:
                    self.ship_to(chc, med_type, allocation, transit_time, current_month)


class CommunityHealthCenterAgent(LocationAgent):
    def __init__(self, unique_id: str, model, capacity: int, population_served: int):
        super().__init__(unique_id, model, capacity, 'chc')
        self.population_served = population_served
        self.health_worker_present = True
        self.patients_treated = defaultdict(int)
        self.patients_untreated = defaultdict(int)
        self.deaths = defaultdict(int)
        self.shortages = defaultdict(int)

    def get_forecast(self, month: int, medicine_type: str) -> dict:
        year = (month - 1) // 12 + 1
        month_of_year = ((month - 1) % 12) + 1
        outbreak_mult = 1.0
        if hasattr(self.model, 'outbreak_chcs') and self.unique_id in self.model.outbreak_chcs:
            outbreak_mult = self.model.outbreak_multiplier
        return generate_monthly_forecast(self.unique_id, month_of_year, year, medicine_type, outbreak_mult)

    def get_actual_demand(self, current_month: int) -> Dict[str, Dict[str, int]]:
        demands = {}
        config = self.model.config
        for abx_class in config['antibiotic_classes']:
            forecast = self.get_forecast(current_month, abx_class)
            total_demand = forecast['expected_demand']
            demands[abx_class] = {}
            for age_group, pct in config['demographics'].items():
                demands[abx_class][age_group] = int(total_demand * pct)
        return demands

    def process_demand(self, current_month: int) -> Dict:
        results = {'treated': defaultdict(int), 'untreated': defaultdict(int), 'deaths': defaultdict(int)}
        config = self.model.config

        if not self.health_worker_present:
            return results

        demands = self.get_actual_demand(current_month)

        for abx_class, age_demands in demands.items():
            available = self.get_stock_level(abx_class)

            # Handle AMR scenario
            if abx_class == 'Penicillins' and hasattr(self.model, 'amr_active') and self.model.amr_active:
                for age_group, demand in age_demands.items():
                    resistant_cases = int(demand * self.model.amr_resistance_rate)
                    if resistant_cases > 0:
                        macro_available = self.get_stock_level('Macrolides')
                        macro_served = min(resistant_cases, macro_available)
                        macro_unserved = resistant_cases - macro_served
                        self._consume_stock('Macrolides', macro_served)
                        results['treated'][age_group] += macro_served
                        if macro_unserved > 0:
                            results['untreated'][age_group] += macro_unserved
                            self.shortages['Macrolides'] += macro_unserved
                            death_rate = config['death_rates'][age_group]
                            deaths = int(macro_unserved * death_rate)
                            results['deaths'][age_group] += deaths
                            self.deaths[age_group] += deaths
                        demand = demand - resistant_cases
                        age_demands[age_group] = demand

            for age_group, demand in age_demands.items():
                # Handle private sector diversion
                if hasattr(self.model, 'private_sector_diversion') and self.model.private_sector_diversion > 0:
                    diverted = int(demand * self.model.private_sector_diversion)
                    demand = demand - diverted

                served = min(demand, available)
                unmet = demand - served
                available -= served

                results['treated'][age_group] += served
                self.patients_treated[age_group] += served

                if unmet > 0:
                    results['untreated'][age_group] += unmet
                    self.patients_untreated[age_group] += unmet
                    self.shortages[abx_class] += unmet
                    death_rate = config['death_rates'][age_group]
                    deaths = int(unmet * death_rate)
                    results['deaths'][age_group] += deaths
                    self.deaths[age_group] += deaths

                self._consume_stock(abx_class, served)

        return results

    def _consume_stock(self, medicine_type: str, quantity: int):
        remaining = quantity
        for batch in sorted(self.inventory[medicine_type], key=lambda b: b.expiry_month):
            if remaining <= 0:
                break
            if batch.quantity > 0:
                take = min(batch.quantity, remaining)
                batch.quantity -= take
                remaining -= take
        self.inventory[medicine_type] = [b for b in self.inventory[medicine_type] if b.quantity > 0]


class HealthWorkerAgent:
    def __init__(self, assigned_chc: CommunityHealthCenterAgent, absenteeism_rate: float = 0.10):
        self.assigned_chc = assigned_chc
        self.absenteeism_rate = absenteeism_rate

    def determine_attendance(self):
        self.assigned_chc.health_worker_present = np.random.random() > self.absenteeism_rate


# ============================================================================
# Supply Chain Model with Shipment Tracking
# ============================================================================

class EthiopiaSupplyChainModel:
    def __init__(self, config: dict = None, scenario: str = 'base'):
        self.config = config or CONFIG.copy()
        self.scenario = scenario
        self.current_month = 0

        # Shipment tracking for visualization
        self.month_shipments = []  # Shipments for current month

        self._apply_scenario(scenario)
        self._create_agents()
        self.metrics_history = []

    def record_shipment(self, from_id: str, to_id: str, medicine_type: str, quantity: int):
        """Record a shipment for visualization."""
        self.month_shipments.append({
            'from': from_id,
            'to': to_id,
            'medicine_type': medicine_type,
            'quantity': quantity
        })

    def _apply_scenario(self, scenario: str):
        self.outbreak_chcs = set()
        self.outbreak_multiplier = 1.0
        self.amr_active = False
        self.amr_resistance_rate = 0.0
        self.private_sector_diversion = 0.0
        self.manufacturer_failure_month = None
        self.manufacturer_failure_id = None
        self.manufacturer_recovery_months = 12

        if scenario == 'base':
            pass
        elif scenario == 'weather_delays':
            self.config['transit_time'] = 4
        elif scenario == 'disease_outbreak':
            all_chcs = [f'CHC_{i:03d}' for i in range(1, self.config['n_chcs'] + 1)]
            self.outbreak_chcs = set(np.random.choice(all_chcs, size=25, replace=False))
            self.outbreak_multiplier = 3.0
        elif scenario == 'advance_ordering':
            self.config['order_lead_time'] = 4
        elif scenario == 'manufacturer_failure':
            self.manufacturer_failure_month = 12
            self.manufacturer_failure_id = 0
            self.manufacturer_recovery_months = 12
        elif scenario == 'optimization_challenge':
            self.config['order_lead_time'] = 3
            self.config['transit_time'] = 2
        elif scenario == 'amr_substitution':
            self.amr_active = False
            self.amr_resistance_rate = 0.30
            self.amr_start_month = 24
        elif scenario == 'private_sector':
            self.private_sector_diversion = 0.25

    def _create_agents(self):
        self.manufacturers = []
        for i in range(self.config['n_manufacturers']):
            mfr = ManufacturerAgent(f'MFR_{i}', self, self.config['manufacturer_capacity'])
            self.manufacturers.append(mfr)

        self.central_stores = []
        for i in range(self.config['n_central_stores']):
            cms = CentralMedicalStoreAgent(f'CMS_{i}', self, self.config['central_store_capacity'])
            self.central_stores.append(cms)

        self.hospitals = []
        for i in range(self.config['n_hospitals']):
            served_chcs = CHC_HOSPITAL_ASSIGNMENTS[i]
            hosp = HospitalAgent(f'HOSP_{i}', self, self.config['hospital_capacity'], served_chcs)
            self.hospitals.append(hosp)

        self.chcs = []
        self.chc_lookup = {}
        for i in range(1, self.config['n_chcs'] + 1):
            chc_id = f'CHC_{i:03d}'
            chc = CommunityHealthCenterAgent(chc_id, self, self.config['chc_capacity'], facility_populations[chc_id])
            self.chcs.append(chc)
            self.chc_lookup[chc_id] = chc

        for hosp in self.hospitals:
            hosp.served_chcs = [self.chc_lookup[chc_id] for chc_id in hosp.served_chc_ids]

        self.health_workers = []
        for chc in self.chcs:
            hw = HealthWorkerAgent(chc, self.config['health_worker_absenteeism'])
            self.health_workers.append(hw)

        self._initialize_inventory()

    def _initialize_inventory(self):
        initial_pct = self.config['initial_stock_pct']
        for agent_list in [self.manufacturers, self.central_stores, self.hospitals, self.chcs]:
            for agent in agent_list:
                for med_type in self.config['antibiotic_classes']:
                    initial_qty = int(agent.capacity * initial_pct / 3)
                    batch = MedicineBatch(med_type, initial_qty, 0, self.config['medicine_shelf_life'])
                    agent.inventory[med_type].append(batch)

    def step(self):
        self.current_month += 1
        self.month_shipments = []  # Reset shipment tracking

        # Check for events
        if self.manufacturer_failure_month and self.current_month == self.manufacturer_failure_month:
            self.manufacturers[self.manufacturer_failure_id].fail(self.current_month, self.manufacturer_recovery_months)

        if hasattr(self, 'amr_start_month') and self.current_month >= self.amr_start_month:
            self.amr_active = True

        month_metrics = {
            'month': self.current_month,
            'shortages': defaultdict(int),
            'wastage': defaultdict(int),
            'deaths': defaultdict(int),
            'patients_treated': defaultdict(int),
            'patients_total': defaultdict(int)
        }

        # 1. Production
        for mfr in self.manufacturers:
            mfr.produce(self.current_month)

        # 2. Process arrivals
        for agent_list in [self.central_stores, self.hospitals, self.chcs]:
            for agent in agent_list:
                agent.process_incoming_shipments(self.current_month)

        # 3. Manufacturer -> Central Store
        for mfr in self.manufacturers:
            for cms in self.central_stores:
                for med_type in self.config['antibiotic_classes']:
                    available = mfr.get_stock_level(med_type)
                    if available > 0:
                        mfr.ship_to(cms, med_type, available, 1, self.current_month)

        # 4. Central Store -> Hospitals
        transit_time = self.config['transit_time'] // 2
        for cms in self.central_stores:
            cms.distribute_to_hospitals(self.hospitals, self.current_month, transit_time)

        # 5. Hospitals -> CHCs
        for hosp in self.hospitals:
            hosp.distribute_to_chcs(self.current_month, transit_time)

        # 6. Health worker attendance
        for hw in self.health_workers:
            hw.determine_attendance()

        # 7. Process demand
        for chc in self.chcs:
            results = chc.process_demand(self.current_month)
            for age in ['child', 'adult', 'elderly']:
                month_metrics['patients_treated'][age] += results['treated'][age]
                month_metrics['patients_total'][age] += results['treated'][age] + results['untreated'][age]
                month_metrics['deaths'][age] += results['deaths'][age]
            for med_type, count in chc.shortages.items():
                month_metrics['shortages'][med_type] += count
            chc.shortages = defaultdict(int)

        # 8. Process expiry
        for agent_list in [self.manufacturers, self.central_stores, self.hospitals, self.chcs]:
            for agent in agent_list:
                expired = agent.process_expiry(self.current_month)
                for med_type, qty in expired.items():
                    month_metrics['wastage'][med_type] += qty

        # Collect stock levels for dashboard
        month_metrics['stock_levels'] = self._collect_stock_levels()
        month_metrics['shipments'] = self.month_shipments.copy()

        # Calculate treatment rate
        total_treated = sum(month_metrics['patients_treated'].values())
        total_patients = sum(month_metrics['patients_total'].values())
        month_metrics['treatment_rate'] = total_treated / total_patients if total_patients > 0 else 1.0

        # Convert defaultdicts
        month_metrics['shortages'] = dict(month_metrics['shortages'])
        month_metrics['wastage'] = dict(month_metrics['wastage'])
        month_metrics['deaths'] = dict(month_metrics['deaths'])
        month_metrics['patients_treated'] = dict(month_metrics['patients_treated'])
        month_metrics['patients_total'] = dict(month_metrics['patients_total'])

        self.metrics_history.append(month_metrics)

    def _collect_stock_levels(self):
        """Collect stock levels for all agents, aggregating CHCs into regions."""
        stock_levels = {
            'manufacturers': [],
            'central_stores': [],
            'hospitals': [],
            'chc_regions': []
        }

        for mfr in self.manufacturers:
            stock_levels['manufacturers'].append({
                'id': mfr.unique_id,
                'stock': mfr.get_total_stock(),
                'capacity': mfr.capacity,
                'operational': mfr.operational if hasattr(mfr, 'operational') else True
            })

        for cms in self.central_stores:
            stock_levels['central_stores'].append({
                'id': cms.unique_id,
                'stock': cms.get_total_stock(),
                'capacity': cms.capacity
            })

        for hosp in self.hospitals:
            stock_levels['hospitals'].append({
                'id': hosp.unique_id,
                'stock': hosp.get_total_stock(),
                'capacity': hosp.capacity
            })

        # Aggregate CHCs into 3 regions (matching hospitals)
        for i, hosp in enumerate(self.hospitals):
            region_stock = sum(self.chc_lookup[chc_id].get_total_stock() for chc_id in hosp.served_chc_ids)
            region_capacity = sum(self.chc_lookup[chc_id].capacity for chc_id in hosp.served_chc_ids)
            stock_levels['chc_regions'].append({
                'id': f'CHC_Region_{i}',
                'stock': region_stock,
                'capacity': region_capacity,
                'num_chcs': len(hosp.served_chc_ids)
            })

        return stock_levels

    def run(self, n_months: int = None):
        if n_months is None:
            n_months = self.config['n_months']
        for _ in range(n_months):
            self.step()


# ============================================================================
# Main: Run all scenarios and export
# ============================================================================

SCENARIOS = [
    ('base', 'Base Case'),
    ('weather_delays', 'Weather Delays'),
    ('disease_outbreak', 'Disease Outbreak'),
    ('advance_ordering', 'Advance Ordering'),
    ('manufacturer_failure', 'Manufacturer Failure'),
    ('optimization_challenge', 'Optimized Policy'),
    ('amr_substitution', 'AMR Substitution'),
    ('private_sector', 'Private Sector')
]


def export_scenario(scenario_id: str, scenario_name: str, output_dir: Path):
    """Run a scenario and export to JSON."""
    print(f"Running: {scenario_name}...")

    np.random.seed(42)  # Reset seed for reproducibility

    model = EthiopiaSupplyChainModel(scenario=scenario_id)
    model.run(60)

    # Build export data
    export_data = {
        'scenario_id': scenario_id,
        'scenario_name': scenario_name,
        'n_months': 60,
        'months': []
    }

    for m in model.metrics_history:
        month_data = {
            'month': m['month'],
            'stock_levels': m['stock_levels'],
            'shortages': m['shortages'],
            'deaths': m['deaths'],
            'wastage': m['wastage'],
            'treatment_rate': m['treatment_rate'],
            'shipments': m['shipments']
        }
        export_data['months'].append(month_data)

    # Calculate totals
    export_data['totals'] = {
        'shortages': sum(sum(m['shortages'].values()) for m in model.metrics_history),
        'deaths': sum(sum(m['deaths'].values()) for m in model.metrics_history),
        'wastage': sum(sum(m['wastage'].values()) for m in model.metrics_history)
    }

    output_file = output_dir / f'{scenario_id}.json'
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"  Exported to {output_file}")
    print(f"  Total shortages: {export_data['totals']['shortages']:,}")
    print(f"  Total deaths: {export_data['totals']['deaths']:,}")

    return export_data


def main():
    output_dir = Path(__file__).parent / 'scenarios'
    output_dir.mkdir(exist_ok=True)

    print("="*60)
    print("Pre-computing ABM scenarios for dashboard")
    print("="*60)

    all_scenarios = {}
    for scenario_id, scenario_name in SCENARIOS:
        data = export_scenario(scenario_id, scenario_name, output_dir)
        all_scenarios[scenario_id] = {
            'name': scenario_name,
            'totals': data['totals']
        }
        print()

    # Export index file
    index_file = output_dir / 'index.json'
    with open(index_file, 'w') as f:
        json.dump(all_scenarios, f, indent=2)

    print("="*60)
    print(f"All scenarios exported to {output_dir}")
    print("="*60)


if __name__ == '__main__':
    main()
