"""Seed database with realistic engineering data.

Creates a power distribution system with components, parameters, traces, and constraints.
"""

from app.database import SessionLocal, init_db
from app.models.models import Item, Parameter, Trace, Constraint, ConstraintSource
from datetime import datetime


def seed_database():
    """Populate database with realistic engineering data."""
    init_db()
    db = SessionLocal()

    try:
        # Clear existing data
        db.query(Constraint).delete()
        db.query(ConstraintSource).delete()
        db.query(Trace).delete()
        db.query(Parameter).delete()
        db.query(Item).delete()
        db.commit()

        print("Creating items...")

        # Create items (engineering components)
        psu = Item(
            short_id="PWR-001",
            name="Power Supply Unit (PSU)",
            item_type="Hardware Spec",
            domain="electrical",
            description="48V 500W power supply unit for main system",
            tracespace_item_id=None,
            tracespace_org=None,
        )

        motor_ctrl = Item(
            short_id="CTRL-001",
            name="Motor Controller",
            item_type="Hardware Spec",
            domain="electrical",
            description="48V DC motor drive controller, 320W capable",
            tracespace_item_id=None,
            tracespace_org=None,
        )

        dc_dc = Item(
            short_id="CONV-001",
            name="DC-DC Converter",
            item_type="Hardware Spec",
            domain="electrical",
            description="48V to 24V converter, 100W max with 92% efficiency",
            tracespace_item_id=None,
            tracespace_org=None,
        )

        sensor_array = Item(
            short_id="SENS-001",
            name="Sensor Array",
            item_type="Hardware Spec",
            domain="electrical",
            description="Temperature, voltage, and current sensors (24V powered)",
            tracespace_item_id=None,
            tracespace_org=None,
        )

        cooling = Item(
            short_id="COOL-001",
            name="Cooling System",
            item_type="Hardware Spec",
            domain="thermal",
            description="Liquid cooling system for motor controller, 150W dissipation",
            tracespace_item_id=None,
            tracespace_org=None,
        )

        battery = Item(
            short_id="BATT-001",
            name="Battery Pack",
            item_type="Hardware Spec",
            domain="electrical",
            description="48V 200Ah lithium battery pack, 50kg mass",
            tracespace_item_id=None,
            tracespace_org=None,
        )

        system = Item(
            short_id="SYS-001",
            name="Power Distribution System",
            item_type="System Requirement",
            domain="systems",
            description="Top-level power distribution and control system",
            tracespace_item_id=None,
            tracespace_org=None,
        )

        for item in [psu, motor_ctrl, dc_dc, sensor_array, cooling, battery, system]:
            db.add(item)
        db.commit()

        print("Creating parameters...")

        # PSU parameters
        psu_voltage = Parameter(
            item_id=psu.id,
            name="Output Voltage",
            value=48.0,
            unit="V",
            param_type="parameter",
            tracespace_field_name=None,
        )
        psu_max_power = Parameter(
            item_id=psu.id,
            name="Max Power Output",
            value=500.0,
            unit="W",
            param_type="parameter",
            tracespace_field_name=None,
        )
        psu_efficiency = Parameter(
            item_id=psu.id,
            name="Efficiency",
            value=94.0,
            unit="%",
            param_type="parameter",
            tracespace_field_name=None,
        )

        # Motor Controller parameters
        motor_voltage_req = Parameter(
            item_id=motor_ctrl.id,
            name="Input Voltage Required",
            value=48.0,
            unit="V",
            param_type="parameter",
            tracespace_field_name=None,
        )
        motor_max_power = Parameter(
            item_id=motor_ctrl.id,
            name="Max Power Draw",
            value=320.0,
            unit="W",
            param_type="parameter",
            tracespace_field_name=None,
        )
        motor_temp_max = Parameter(
            item_id=motor_ctrl.id,
            name="Max Operating Temperature",
            value=85.0,
            unit="°C",
            param_type="parameter",
            tracespace_field_name=None,
        )
        motor_temp_current = Parameter(
            item_id=motor_ctrl.id,
            name="Current Operating Temperature",
            value=68.0,
            unit="°C",
            param_type="parameter",
            tracespace_field_name=None,
        )

        # DC-DC Converter parameters
        dcdc_input_voltage = Parameter(
            item_id=dc_dc.id,
            name="Input Voltage",
            value=48.0,
            unit="V",
            param_type="parameter",
            tracespace_field_name=None,
        )
        dcdc_output_voltage = Parameter(
            item_id=dc_dc.id,
            name="Output Voltage",
            value=24.0,
            unit="V",
            param_type="parameter",
            tracespace_field_name=None,
        )
        dcdc_max_power = Parameter(
            item_id=dc_dc.id,
            name="Max Power Output",
            value=100.0,
            unit="W",
            param_type="parameter",
            tracespace_field_name=None,
        )
        dcdc_efficiency = Parameter(
            item_id=dc_dc.id,
            name="Efficiency",
            value=92.0,
            unit="%",
            param_type="parameter",
            tracespace_field_name=None,
        )

        # Sensor Array parameters
        sensor_voltage_req = Parameter(
            item_id=sensor_array.id,
            name="Input Voltage Required",
            value=24.0,
            unit="V",
            param_type="parameter",
            tracespace_field_name=None,
        )
        sensor_power = Parameter(
            item_id=sensor_array.id,
            name="Power Consumption",
            value=75.0,
            unit="W",
            param_type="parameter",
            tracespace_field_name=None,
        )

        # Cooling System parameters
        cooling_dissipation = Parameter(
            item_id=cooling.id,
            name="Heat Dissipation Capacity",
            value=150.0,
            unit="W",
            param_type="parameter",
            tracespace_field_name=None,
        )
        cooling_ambient_max = Parameter(
            item_id=cooling.id,
            name="Max Ambient Temperature",
            value=45.0,
            unit="°C",
            param_type="parameter",
            tracespace_field_name=None,
        )

        # Battery parameters
        battery_voltage = Parameter(
            item_id=battery.id,
            name="Nominal Voltage",
            value=48.0,
            unit="V",
            param_type="parameter",
            tracespace_field_name=None,
        )
        battery_capacity = Parameter(
            item_id=battery.id,
            name="Capacity",
            value=200.0,
            unit="Ah",
            param_type="parameter",
            tracespace_field_name=None,
        )
        battery_mass = Parameter(
            item_id=battery.id,
            name="Mass",
            value=50.0,
            unit="kg",
            param_type="parameter",
            tracespace_field_name=None,
        )

        # System parameters
        system_total_power = Parameter(
            item_id=system.id,
            name="Total Power Available",
            value=500.0,
            unit="W",
            param_type="parameter",
            tracespace_field_name=None,
        )
        system_total_drawn = Parameter(
            item_id=system.id,
            name="Total Power Drawn",
            value=395.0,  # 320 + 75, leaves 105W margin
            unit="W",
            param_type="parameter",
            tracespace_field_name=None,
        )

        for param in [
            psu_voltage, psu_max_power, psu_efficiency,
            motor_voltage_req, motor_max_power, motor_temp_max, motor_temp_current,
            dcdc_input_voltage, dcdc_output_voltage, dcdc_max_power, dcdc_efficiency,
            sensor_voltage_req, sensor_power,
            cooling_dissipation, cooling_ambient_max,
            battery_voltage, battery_capacity, battery_mass,
            system_total_power, system_total_drawn,
        ]:
            db.add(param)
        db.commit()

        print("Creating traces...")

        # Create traces (relationships)
        trace_psu_to_motor = Trace(
            source_item_id=psu.id,
            target_item_id=motor_ctrl.id,
            trace_type="powers",
            description="PSU supplies power to motor controller",
            tracespace_trace_id=None,
        )

        trace_psu_to_dcdc = Trace(
            source_item_id=psu.id,
            target_item_id=dc_dc.id,
            trace_type="powers",
            description="PSU supplies input to DC-DC converter",
            tracespace_trace_id=None,
        )

        trace_dcdc_to_sensor = Trace(
            source_item_id=dc_dc.id,
            target_item_id=sensor_array.id,
            trace_type="powers",
            description="DC-DC converter supplies 24V to sensor array",
            tracespace_trace_id=None,
        )

        trace_motor_cooled = Trace(
            source_item_id=cooling.id,
            target_item_id=motor_ctrl.id,
            trace_type="cooled_by",
            description="Cooling system removes heat from motor controller",
            tracespace_trace_id=None,
        )

        trace_battery_powers = Trace(
            source_item_id=battery.id,
            target_item_id=psu.id,
            trace_type="powers",
            description="Battery pack provides input to PSU",
            tracespace_trace_id=None,
        )

        trace_system_contains = Trace(
            source_item_id=system.id,
            target_item_id=psu.id,
            trace_type="contains",
            description="System contains PSU",
            tracespace_trace_id=None,
        )

        for trace in [trace_psu_to_motor, trace_psu_to_dcdc, trace_dcdc_to_sensor,
                      trace_motor_cooled, trace_battery_powers, trace_system_contains]:
            db.add(trace)
        db.commit()

        print("Creating constraints...")

        # CONSTRAINT 1: PSU output voltage must equal required voltage
        constraint1 = Constraint(
            name="PSU Voltage Match",
            description="PSU output voltage must match motor controller requirement",
            rule_type="eq",
            severity="critical",
            source_parameter_id=psu_voltage.id,
            target_parameter_id=motor_voltage_req.id,
            domain_descriptions={
                "electrical": "PSU output voltage equals motor controller input requirement"
            },
        )

        # CONSTRAINT 2: Motor power draw must not exceed PSU capacity
        constraint2 = Constraint(
            name="Motor Power Budget",
            description="Motor power consumption must not exceed PSU maximum output",
            rule_type="lte",
            severity="error",
            source_parameter_id=motor_max_power.id,
            target_parameter_id=psu_max_power.id,
            domain_descriptions={
                "electrical": "Motor draw <= PSU max power"
            },
        )

        # CONSTRAINT 3: DC-DC converter input must match PSU output
        constraint3 = Constraint(
            name="DC-DC Input Voltage",
            description="DC-DC converter input voltage must match PSU output",
            rule_type="eq",
            severity="critical",
            source_parameter_id=dcdc_input_voltage.id,
            target_parameter_id=psu_voltage.id,
            domain_descriptions={
                "electrical": "DC-DC input matches PSU output"
            },
        )

        # CONSTRAINT 4: Sensor voltage must match DC-DC output
        constraint4 = Constraint(
            name="Sensor Supply Voltage",
            description="Sensor array supply voltage must match DC-DC output",
            rule_type="eq",
            severity="error",
            source_parameter_id=sensor_voltage_req.id,
            target_parameter_id=dcdc_output_voltage.id,
            domain_descriptions={
                "electrical": "Sensor input matches DC-DC output"
            },
        )

        # CONSTRAINT 5: Total system power draw cannot exceed available power
        constraint5 = Constraint(
            name="System Power Budget",
            description="Total power drawn must not exceed PSU capacity",
            rule_type="lte",
            severity="error",
            source_parameter_id=system_total_drawn.id,
            target_parameter_id=system_total_power.id,
            domain_descriptions={
                "electrical": "Total system draw <= available power"
            },
        )

        # CONSTRAINT 6: Motor operating temperature must not exceed limit
        constraint6 = Constraint(
            name="Motor Temperature Limit",
            description="Motor controller operating temperature must stay below maximum",
            rule_type="lte",
            severity="warning",
            source_parameter_id=motor_temp_current.id,
            target_parameter_id=motor_temp_max.id,
            domain_descriptions={
                "thermal": "Current temperature <= max rated temperature"
            },
        )

        # CONSTRAINT 7: Motor temperature must be cooled properly (tolerance)
        constraint7 = Constraint(
            name="Motor Temperature Control",
            description="Motor operating temperature should stay within 15°C of ambient",
            rule_type="tolerance",
            severity="warning",
            source_parameter_id=motor_temp_current.id,
            target_parameter_id=cooling_ambient_max.id,
            tolerance_value=15.0,
            domain_descriptions={
                "thermal": "Temperature difference between motor and ambient <= 15°C"
            },
        )

        # CONSTRAINT 8: Cooling capacity must exceed motor heat generation
        constraint8 = Constraint(
            name="Heat Removal Capacity",
            description="Cooling system dissipation must exceed motor power losses",
            rule_type="gte",
            severity="error",
            source_parameter_id=cooling_dissipation.id,
            target_parameter_id=motor_max_power.id,
            domain_descriptions={
                "thermal": "Cooling capacity >= motor power for safe operation"
            },
        )

        # CONSTRAINT 9: DC-DC output power plus sensors must not exceed DC-DC max
        constraint9 = Constraint(
            name="DC-DC Power Limit",
            description="Combined 24V draw must not exceed DC-DC converter max output",
            rule_type="sum_lte",
            severity="error",
            target_parameter_id=dcdc_max_power.id,
            domain_descriptions={
                "electrical": "sum(24V loads) <= DC-DC max output"
            },
        )

        # CONSTRAINT 10: Battery voltage must match PSU input requirement
        constraint10 = Constraint(
            name="Battery Supply Voltage",
            description="Battery nominal voltage must supply PSU input requirement",
            rule_type="eq",
            severity="critical",
            source_parameter_id=battery_voltage.id,
            target_parameter_id=psu_voltage.id,
            domain_descriptions={
                "electrical": "Battery voltage matches PSU input requirement"
            },
        )

        for constraint in [constraint1, constraint2, constraint3, constraint4,
                          constraint5, constraint6, constraint7, constraint8,
                          constraint9, constraint10]:
            db.add(constraint)
        db.commit()

        # Add constraint sources for constraint9 (DC-DC sum)
        source1 = ConstraintSource(
            constraint_id=constraint9.id,
            parameter_id=sensor_power.id,
            role="source",
        )
        db.add(source1)
        db.commit()

        print("✓ Database seeded successfully!")
        print(f"  - 7 items created")
        print(f"  - 19 parameters created")
        print(f"  - 6 traces created")
        print(f"  - 10 constraints created")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
