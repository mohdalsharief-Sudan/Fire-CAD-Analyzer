"""
الثوابت والمعايير الهندسية
وفقاً للمعايير الأمريكية NFPA والكود السعودي
"""


class NFPA13:
    """معايير NFPA 13 لأنظمة الرشاشات"""
    
    # التباعد الأقصى للرشاشات (متر)
    MAX_SPACING = {
        'light_hazard': 4.6,
        'ordinary_hazard': 4.6,
        'extra_hazard': 3.7,
    }
    
    # المساحة القصوى المغطاة لكل رشاش (متر مربع)
    MAX_COVERAGE = {
        'light_hazard': 18.6,
        'ordinary_hazard': 12.1,
        'extra_hazard': 9.3,
    }
    
    # معاملات K القياسية
    STANDARD_K_FACTORS = [5.6, 8.0, 11.2, 14.0, 16.8, 25.2]
    
    # المسافة من الجدران (متر)
    MAX_WALL_DISTANCE = 2.3
    
    # أقطار المواسير القياسية (مم)
    PIPE_DIAMETERS = [25, 32, 40, 50, 65, 80, 100, 150, 200, 250, 300]


class NFPA14:
    """معايير NFPA 14 لأنظمة الخراطيم"""
    
    MIN_PRESSURE = 100  # PSI
    MIN_FLOW_RATE = 250  # GPM


class NFPA20:
    """معايير NFPA 20 لمضخات الحريق"""
    
    MIN_PUMP_CAPACITY = 500  # GPM
    MIN_PUMP_PRESSURE = 40  # PSI


class SaudiCode:
    """الكود السعودي للحماية من الحريق (SBC 801)"""
    
    MIN_WATER_STORAGE = 30  # دقيقة
    TEMPERATURE_RANGE = (-10, 60)
    
    BUILDING_TYPES = [
        'residential',
        'commercial',
        'industrial',
        'healthcare',
        'educational',
        'high_rise',
    ]
    
    @staticmethod
    def get_min_sprinkler_flow(building_type):
        """الحصول على الحد الأدنى للتدفق حسب نوع المبنى"""
        flows = {
            'residential': 30,
            'commercial': 50,
            'industrial': 75,
            'healthcare': 60,
            'educational': 50,
            'high_rise': 100,
        }
        return flows.get(building_type, 50)


# طبقات AutoCAD الفعلية
FIRE_LAYERS = {
    'sprinklers': [
        'FF-SPRIN', 'SPRINKLER', 'SPRINKLERS', 'FIRE-SPRINKLER',
        'FIRE_SPRINKLER', 'رشاش', 'رشاشات',
        'SPR-HEAD', 'SPRINKLER-HEAD', 'PENDANT SP.'
    ],
    'pipes': [
        'FF-WBRA-LINE', 'FF-WET-LINE', 'FF-DRY-LINE', 'FF-SPLN',
        'FF-NETWORK', 'PIPE', 'PIPES', 'FIRE-PIPE', 'FIRE_PIPE',
        'PIPING', 'FIRE-PIPING', 'مواسير', 'أنابيب',
        'PIPE-FIRE', 'P-PIPE', 'FIRE-PIPING-SYSTEM'
    ],
    'pumps': [
        'FF-PUMP', 'FIRE-PUMP', 'FIRE_PUMP', 'PUMP', 'PUMP-ROOM',
        'مضخة', 'مضخات', 'FIRE-PUMP-ROOM',
        'ELEC PUMP', 'DIESEL PUMP', 'JOCKEY PUMP'
    ],
    'valves': [
        'VALVE', 'VALVES', 'FIRE-VALVE', 'CONTROL-VALVE',
        'صمام', 'صمامات', 'ZONE-CONTROL-VALVE', 'ZCV'
    ],
    'tanks': [
        'WATER-TANK', 'TANK', 'STORAGE-TANK', 'FIRE-TANK',
        'خزان', 'خزانات', 'WATER-STORAGE'
    ],
    'gas_systems': [
        'FM-200', 'FM200', 'FM 200', 'NOVEC', 'NOVEC 1230',
        'INERGEN', 'CO2', 'غاز', 'GAS'
    ],
    'hose_cabinets': [
        'FHC', 'FIRE HOSE', 'HOSE REEL', 'HOSE CABINET',
        'خرطوم', 'FIRE-HOSE'
    ],
    'fire_alarm': [
        'FIRE ALARM', 'FIRE-ALARM', 'ALARM', 'DETECTOR',
        'إنذار', 'حريق-إنذار'
    ]
}

# أنواع المضخات
PUMP_TYPES = {
    'ELEC PUMP': 'electric',
    'DIESEL PUMP': 'diesel',
    'JOCKEY PUMP': 'jockey',
    'FIRE-PUMP': 'main',
    'FF-PUMP': 'main'
}

# أنواع الرشاشات
SPRINKLER_TYPES = {
    'PENDANT': 'pendant',
    'UPRIGHT': 'upright',
    'SIDE WALL': 'sidewall',
    'CONCEALED': 'concealed',
    'S': 'standard',
    'SP.': 'sprinkler'
}