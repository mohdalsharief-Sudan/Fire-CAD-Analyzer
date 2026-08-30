# src/gas_data.py
"""
أسعار أنظمة الإطفاء بالغاز - ريال سعودي
"""

GAS_COSTS = {
    'FM-200': {
        'per_kg': 350,                    # ريال/كجم
        'cylinder_small': 8500,           # أسطوانة 16-32 كجم
        'cylinder_medium': 15000,         # أسطوانة 45-64 كجم
        'cylinder_large': 25000,          # أسطوانة 100+ كجم
        'control_panel': 12000,           # لوحة تحكم
        'detector': 450,                  # كاشف
        'nozzle': 350,                    # فوهة
        'pipe_per_meter': 180,            # ماسورة/متر
        'installation_ratio': 0.30,       # نسبة التركيب
    },
    'Novec 1230': {
        'per_kg': 500,
        'cylinder_small': 12000,
        'cylinder_medium': 20000,
        'cylinder_large': 32000,
        'control_panel': 15000,
        'detector': 500,
        'nozzle': 400,
        'pipe_per_meter': 200,
        'installation_ratio': 0.32,
    },
    'CO2': {
        'per_kg': 80,
        'cylinder_small': 5000,
        'cylinder_medium': 9000,
        'cylinder_large': 15000,
        'control_panel': 8000,
        'detector': 300,
        'nozzle': 250,
        'pipe_per_meter': 120,
        'installation_ratio': 0.28,
    }
}