from hydraulic_calculator import HydraulicCalculator

calc = HydraulicCalculator()

results = calc.calculate_complete_system(
    density=6.0,           # OH2
    design_area=72.0,      # مساحة تصميمية
    landing_valves=10,     # سيستخدم 2 فقط
    hydrants=5,            # سيستخدم 1 فقط
    hose_cabinets=20,      # سيستخدم 2 فقط
    pipe_length_m=100,
    elevation_m=15,
    duration_min=30
)

calc.print_results(results)