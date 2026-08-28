# check_units.py
import ezdxf

doc = ezdxf.readfile(r'D:\Testing.dxf')

print("معلومات الوحدات:")
print(f"INSUNITS: {doc.header.get('$INSUNITS', 'غير محدد')}")
print(f"EXTMIN: {doc.header.get('$EXTMIN', 'غير محدد')}")
print(f"EXTMAX: {doc.header.get('$EXTMAX', 'غير محدد')}")

# حساب أبعاد الرسم
extmin = doc.header.get('$EXTMIN', (0, 0, 0))
extmax = doc.header.get('$EXTMAX', (0, 0, 0))

width = extmax[0] - extmin[0]
height = extmax[1] - extmin[1]

print(f"\nأبعاد الرسم:")
print(f"العرض: {width:.2f} وحدة")
print(f"الارتفاع: {height:.2f} وحدة")

# تقدير الوحدة المناسبة
if width > 10000:
    print("\nالتقدير: الملف مرسوم بالمليمتر (mm)")
    print("المساحة الفعلية: {:.2f} × {:.2f} متر".format(width/1000, height/1000))
elif width > 1000:
    print("\nالتقدير: الملف مرسوم بالسنتيمتر (cm)")
    print("المساحة الفعلية: {:.2f} × {:.2f} متر".format(width/100, height/100))
elif width > 100:
    print("\nالتقدير: الملف مرسوم بالمتر (m)")
    print("المساحة الفعلية: {:.2f} × {:.2f} متر".format(width, height))
elif width > 10:
    print("\nالتقدير: الملف مرسوم بالبوصة (inches)")
    print("المساحة الفعلية: {:.2f} × {:.2f} متر".format(width*0.0254, height*0.0254))
else:
    print("\nالتقدير: غير محدد")