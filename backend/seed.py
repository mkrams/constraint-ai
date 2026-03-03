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
                "electrical": "The power supply must deliver exactly the voltage the motor controller expects. A mismatch means the controller either won't start or could be damaged by overvoltage. This is a hard compatibility requirement with no tolerance band.",
                "systems": "Critical interface contract between two subsystems. If the PSU and motor controller are sourced from different vendors, this must be verified at integration. Changing either side requires a full interface review.",
                "thermal": "Voltage mismatch causes the motor controller's internal regulators to work harder, generating excess heat. Overvoltage can overwhelm thermal derating.",
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
                "electrical": "The motor controller's peak power draw (320W) must stay within the PSU's 500W capacity. If the motor tries to pull more, the PSU will current-limit or shut down, causing an uncontrolled motor stop. Current margin: 180W (36% headroom).",
                "systems": "This is the single biggest power consumer. If motor power requirements grow during development, the PSU must be upsized or other loads shed. This constraint directly gates the system's maximum performance envelope.",
                "mechanical": "Motor power determines available torque and speed. If this constraint becomes tight, mechanical performance is sacrificed first — slower acceleration, lower top speed, or reduced load capacity.",
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
                "electrical": "The DC-DC converter must accept the PSU's output voltage as its input. This is a fixed compatibility requirement — the converter's input stage is designed for a specific voltage rail. Wrong voltage = component destruction.",
                "systems": "The DC-DC converter bridges the 48V power bus and the 24V sensor bus. Any change to the main bus voltage cascades here and breaks the secondary power domain.",
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
                "electrical": "The sensor array needs exactly 24V. Sensors are sensitive to supply voltage — even small deviations cause measurement drift or damage.",
                "systems": "Sensors are the system's eyes. If this voltage is wrong, you get bad data everywhere downstream. This is often the first thing to check when sensor readings seem off.",
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
                "electrical": "Total system power consumption (395W across all loads) must stay under the PSU's 500W capacity. The 105W margin (21%) provides headroom for transient spikes and future growth, but it's not generous.",
                "systems": "This is the master power budget. Every new subsystem or feature eats into this margin. Below 15% margin, the system becomes fragile to load spikes. Power budget is typically the first constraint that blocks new features.",
                "thermal": "Higher total power means more waste heat in the enclosure. Even if individual components are within thermal limits, aggregate heat load pushes ambient temperature up, tightening every thermal constraint.",
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
                "thermal": "The motor controller runs at 68°C with an 85°C maximum. That's 17°C margin (20%). Margin shrinks in hot environments, under sustained loads, or if cooling degrades. Below 10°C margin, thermal throttling engages.",
                "electrical": "As the controller approaches its temperature limit, power handling is derated. At 80°C, expect ~10% less available power. Thermal throttling reduces performance without warning.",
                "mechanical": "Motor controller temperature directly affects available torque. Thermal throttling reduces motor current, meaning less force at the output shaft. In high-duty-cycle applications, this is the real performance bottleneck.",
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
                "thermal": "The temperature rise from ambient to motor controller should not exceed 15°C. Currently the delta is 23°C (68°C - 45°C), which EXCEEDS the tolerance. The cooling system is undersized or the thermal path has high resistance.",
                "systems": "A high temperature delta indicates the cooling system isn't keeping up. Either increase cooling capacity, decrease motor power dissipation, or improve the thermal interface.",
                "mechanical": "Excessive temperature rise often points to poor thermal contact — check mounting torque, thermal paste application, and airflow paths before redesigning the cooling system.",
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
                "thermal": "The cooling system removes 150W but the motor can generate 320W. This is FAILING — cooling is dramatically undersized. The motor doesn't always run at full power, but peak thermal events can still cause damage.",
                "electrical": "Since cooling can't handle full motor power, the electrical system must limit peak motor current (reducing performance) or accept that sustained high-power operation triggers thermal shutdown.",
                "systems": "Critical system-level mismatch. Either upgrade cooling to 320W+, derate motor maximum power, or add active power management that monitors temperature and reduces motor current before thermal limits are reached.",
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
                "electrical": "All 24V loads combined (sensor array at 75W) must stay under the DC-DC converter's 100W capacity. 25W margin (25%) for additional 24V devices. Adding more sensors or actuators eats into this budget.",
                "systems": "The 24V bus is a secondary power domain. Engineers tend to pile loads onto it because it's easier than 48V. Watch this margin — it erodes faster than expected as the design matures.",
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
                "electrical": "The battery must deliver the voltage the PSU expects. This is the root of the entire power chain — if battery voltage doesn't match, nothing downstream works. Battery voltage also sags under load, so nominal matching isn't always sufficient.",
                "systems": "This is the foundational power interface. Battery selection drives PSU selection, which drives everything else. Changing battery chemistry or configuration requires redesigning the entire power distribution.",
                "mechanical": "Battery voltage determines cell count and pack configuration, directly affecting physical size, weight (50kg), and mounting requirements. A voltage change means a new battery enclosure design.",
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
