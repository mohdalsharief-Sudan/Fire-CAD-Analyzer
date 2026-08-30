# src/manufacturers.py
"""
قاعدة بيانات مصنعي أنظمة الإطفاء بالغاز
"""

MANUFACTURERS = {
    'NAFFCO': {
        'country': 'الإمارات',
        'gas_types': ['FM-200', 'Novec 1230', 'CO2'],
        'cylinder_sizes': {
            'FM-200': [4, 8, 16, 32, 42, 80, 120],
            'Novec 1230': [16, 32, 45, 64, 100],
            'CO2': [30, 45, 68, 100],
        },
        'price_factor': 0.85,  # أسعار تنافسية
    },
    'SFFECO': {
        'country': 'السعودية',
        'gas_types': ['FM-200', 'Novec 1230', 'CO2'],
        'cylinder_sizes': {
            'FM-200': [16, 32, 45, 64, 100, 150],
            'Novec 1230': [16, 32, 64, 100],
            'CO2': [30, 45, 68, 100, 150],
        },
        'price_factor': 0.90,
    },
    'FIKE': {
        'country': 'أمريكا',
        'gas_types': ['FM-200', 'Novec 1230', 'CO2'],
        'cylinder_sizes': {
            'FM-200': [16, 32, 52, 106, 147, 180],
            'Novec 1230': [16, 32, 52, 106],
            'CO2': [30, 50, 75, 100, 150],
        },
        'price_factor': 1.15,  # أسعار أعلى (جودة)
    },
    'CHEMGUARD': {
        'country': 'أمريكا',
        'gas_types': ['FM-200', 'Novec 1230', 'CO2'],
        'cylinder_sizes': {
            'FM-200': [16, 32, 67, 125, 150],
            'Novec 1230': [16, 32, 67, 125],
            'CO2': [30, 45, 68, 100, 150],
        },
        'price_factor': 1.10,
    },
}


def get_manufacturer(name: str):
    """الحصول على معلومات مصنع"""
    return MANUFACTURERS.get(name.upper(), None)


def list_manufacturers():
    """عرض المصنعين المتاحين"""
    print("\nالمصنعون المتاحون:")
    print("-" * 50)
    for name, info in MANUFACTURERS.items():
        print(f"  {name:12} - {info['country']}")
        print(f"    غازات: {', '.join(info['gas_types'])}")
        print(f"    أحجام FM-200: {info['cylinder_sizes']['FM-200']}")
        print()