"""
بيانات التكاليف - أسعار المواد حسب النوع والسعة
قابلة للتعديل بالكامل
"""

# ============ الرشاشات ============
SPRINKLER_COSTS = {
    'pendant': {
        'standard': 45,        # ريال
        'concealed': 85,
        'high_temp': 65,
    },
    'upright': {
        'standard': 45,
        'high_temp': 65,
    },
    'sidewall': {
        'standard': 55,
    }
}

# ============ المواسير ============
# السعر بالمتر حسب القطر (مم) والجدول (Schedule)
PIPE_COSTS = {
    'steel': {
        # (القطر مم): {sch10: سعر, sch40: سعر}
        25: {'sch10': 25, 'sch40': 35},
        32: {'sch10': 32, 'sch40': 45},
        40: {'sch10': 40, 'sch40': 55},
        50: {'sch10': 50, 'sch40': 70},
        65: {'sch10': 65, 'sch40': 90},
        80: {'sch10': 75, 'sch40': 110},
        100: {'sch10': 95, 'sch40': 140},
        150: {'sch10': 140, 'sch40': 200},
        200: {'sch10': 190, 'sch40': 280},
        250: {'sch10': 240, 'sch40': 350},
        300: {'sch10': 300, 'sch40': 450},
    },
    'cpvc': {
        25: {'blaze': 35},
        32: {'blaze': 45},
        40: {'blaze': 55},
        50: {'blaze': 70},
        65: {'blaze': 90},
        80: {'blaze': 110},
    }
}

# ============ المضخات ============
PUMP_COSTS = {
    'electric': {
        250: 35000,   # GPM : ريال
        500: 45000,
        750: 55000,
        1000: 65000,
        1500: 85000,
    },
    'diesel': {
        250: 50000,
        500: 65000,
        750: 80000,
        1000: 95000,
        1500: 120000,
    },
    'jockey': {
        50: 8000,
        100: 12000,
        150: 15000,
    }
}

# ============ أنظمة الغاز ============
GAS_SYSTEM_COSTS = {
    'FM-200': {
        'per_kg': 350,           # ريال/كجم
        'cylinder_small': 8500,   # أسطوانة صغيرة
        'cylinder_large': 15000,  # أسطوانة كبيرة
        'control_panel': 12000,
    },
    'Novec 1230': {
        'per_kg': 500,
        'cylinder_small': 12000,
        'cylinder_large': 20000,
        'control_panel': 15000,
    },
    'CO2': {
        'per_kg': 80,
        'cylinder_small': 5000,
        'cylinder_large': 9000,
        'control_panel': 8000,
    }
}

# ============ خزانات الخراطيم ============
HOSE_CABINET_COSTS = {
    'standard': 850,
    'recessed': 1200,
    'stainless': 1800,
}

# ============ الصمامات ============
VALVE_COSTS = {
    'zone_control': 350,
    'butterfly': 500,
    'check': 400,
    'gate': 300,
    'alarm_check': 2500,
}

# ============ Landing Valves ============
LANDING_VALVE_COSTS = {
    'standard': 1200,
    'angle': 1500,
    'brass': 2000,
}

# ============ الهيدرانت ============
HYDRANT_COSTS = {
    'standard': 3500,
    'double': 5500,
    'with_pillar': 8000,
}

# ============ تكاليف إضافية ============
ADDITIONAL_COSTS = {
    'labor_ratio': 0.35,        # نسبة التركيب من تكلفة المواد (35%)
    'engineering_ratio': 0.10,  # نسبة التصميم والهندسة (10%)
    'overhead_ratio': 0.15,     # المصاريف الإدارية (15%)
    'profit_margin': 0.20,      # هامش الربح (20%)
    'contingency': 0.05,        # احتياطي (5%)
}

# ============ عملة ============
CURRENCY = 'ريال سعودي'