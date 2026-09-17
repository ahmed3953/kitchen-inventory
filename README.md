# kitchen-inventory
import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox


# ================= البيانات والملفات =================

المخزون = {}

مجلد_البرنامج = os.path.dirname(__file__)
DATA_FILE = os.path.join(مجلد_البرنامج, "inventory_data.json")
HISTORY_FILE = os.path.join(مجلد_البرنامج, "inventory_history.json")
WASTE_FILE = os.path.join(مجلد_البرنامج, "waste_history.json")
CONSUMPTION_FILE = os.path.join(مجلد_البرنامج, "consumption_history.json")

UNIT_OPTIONS = [
    "كجم", "جرام", "علبة", "كيس",
    "قطعة", "زجاجة", "معلبة", "رطل"
]


# ================= التعامل مع الملفات =================

def تحميل_ملف(اسم_الملف, القيمة_الافتراضية):
    try:
        with open(اسم_الملف, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return القيمة_الافتراضية


def حفظ_ملف(اسم_الملف, البيانات):
    with open(اسم_الملف, "w", encoding="utf-8") as file:
        json.dump(البيانات, file, ensure_ascii=False, indent=2)


def تحميل_المخزون():
    global المخزون
    المخزون = تحميل_ملف(DATA_FILE, {})


def حفظ_المخزون():
    حفظ_ملف(DATA_FILE, المخزون)


# ================= أدوات عامة =================

def قراءة_الكمية(الحقل, اسم_الحقل="الكمية"):
    try:
        الكمية = float(الحقل.get())
    except ValueError:
        messagebox.showerror("خطأ", f"{اسم_الحقل} غير صحيحة")
        return None

    if الكمية < 0:
        messagebox.showerror("خطأ", f"{اسم_الحقل} لا يمكن أن تكون سالبة")
        return None

    return الكمية


def الحصول_على_الصنف():
    اسم = اسم_الصنف.get().strip()

    if not اسم:
        messagebox.showerror("خطأ", "أدخل اسم الصنف")
        return None

    if اسم not in المخزون:
        messagebox.showerror("خطأ", "الصنف غير موجود")
        return None

    return اسم


def مسح_الحقول():
    اسم_الصنف.delete(0, "end")
    كمية_الصنف.delete(0, "end")
    كمية_الهالك.delete(0, "end")
    وحدة_الصنف.set("كجم")


def تحديث_الجدول():
    for row in tree.get_children():
        tree.delete(row)

    for اسم, بيانات in sorted(المخزون.items()):
        tree.insert(
            "",
            "end",
            values=(اسم, بيانات["كمية"], بيانات["وحدة"])
        )


# ================= حفظ اليوم =================

def حفظ_إغلاق_اليوم():
    اليوم = datetime.now().strftime("%Y-%m-%d")
    السجل = تحميل_ملف(HISTORY_FILE, {})

    السجل[اليوم] = {
        اسم: بيانات["كمية"]
        for اسم, بيانات in المخزون.items()
    }

    حفظ_ملف(HISTORY_FILE, السجل)

    messagebox.showinfo(
        "تم",
        f"تم حفظ مخزون يوم {اليوم}"
    )


# ================= الاستهلاك =================

def تسجيل_الاستهلاك(اسم, الكمية):
    اليوم = datetime.now().strftime("%Y-%m-%d")
    السجل = تحميل_ملف(CONSUMPTION_FILE, {})

    السجل.setdefault(اليوم, {})
    السجل[اليوم][اسم] = السجل[اليوم].get(اسم, 0) + الكمية

    حفظ_ملف(CONSUMPTION_FILE, السجل)


def عرض_الاستهلاك_اليومي():
    اسم = الحصول_على_الصنف()

    if اسم is None:
        return

    الشهر = datetime.now().strftime("%Y-%m")
    السجل = تحميل_ملف(CONSUMPTION_FILE, {})
    الوحدة = المخزون[اسم]["وحدة"]

    التقرير = []
    الإجمالي = 0

    for اليوم in sorted(
        تاريخ for تاريخ in السجل
        if تاريخ.startswith(الشهر)
    ):
        الكمية = السجل[اليوم].get(اسم, 0)

        if الكمية > 0:
            التقرير.append(f"{اليوم}: {الكمية} {الوحدة}")
            الإجمالي += الكمية

    if not التقرير:
        messagebox.showinfo(
            "الاستهلاك اليومي",
            "لا توجد بيانات استهلاك هذا الشهر"
        )
        return

    التقرير.append("")
    التقرير.append(f"الإجمالي الشهري: {الإجمالي} {الوحدة}")

    messagebox.showinfo(
        "الاستهلاك اليومي",
        "\n".join(التقرير)
    )


# ================= إدارة المخزون =================

def اضافة_صنف():
    اسم = اسم_الصنف.get().strip()
    وحدة = وحدة_الصنف.get() or "كجم"

    if not اسم:
        messagebox.showerror("خطأ", "أدخل اسم الصنف")
        return

    الكمية = قراءة_الكمية(كمية_الصنف)

    if الكمية is None:
        return

    if اسم in المخزون:
        المخزون[اسم]["كمية"] += الكمية
    else:
        المخزون[اسم] = {
            "كمية": الكمية,
            "وحدة": وحدة
        }

    حفظ_المخزون()
    تحديث_الجدول()
    مسح_الحقول()

    messagebox.showinfo("تم", "تمت إضافة الصنف بنجاح")


def اضافة_كمية():
    اسم = الحصول_على_الصنف()

    if اسم is None:
        return

    الكمية = قراءة_الكمية(كمية_الصنف)

    if الكمية is None or الكمية <= 0:
        messagebox.showerror(
            "خطأ",
            "يجب أن تكون الكمية أكبر من صفر"
        )
        return

    المخزون[اسم]["كمية"] += الكمية

    حفظ_المخزون()
    تحديث_الجدول()
    مسح_الحقول()

    messagebox.showinfo("تم", "تمت إضافة الكمية بنجاح")


def تعديل_الكمية():
    اسم = الحصول_على_الصنف()

    if اسم is None:
        return

    الكمية = قراءة_الكمية(كمية_الصنف)

    if الكمية is None:
        return

    المخزون[اسم]["كمية"] = الكمية

    حفظ_المخزون()
    تحديث_الجدول()
    مسح_الحقول()

    messagebox.showinfo("تم", "تم تعديل الكمية بنجاح")


def سحب_الكمية():
    اسم = الحصول_على_الصنف()

    if اسم is None:
        return

    الكمية = قراءة_الكمية(كمية_الصنف)

    if الكمية is None or الكمية <= 0:
        messagebox.showerror(
            "خطأ",
            "يجب أن تكون الكمية أكبر من صفر"
        )
        return

    if الكمية > المخزون[اسم]["كمية"]:
        messagebox.showwarning(
            "تنبيه",
            f"المتاح فقط: {المخزون[اسم]['كمية']} "
            f"{المخزون[اسم]['وحدة']}"
        )
        return

    المخزون[اسم]["كمية"] -= الكمية
    تسجيل_الاستهلاك(اسم, الكمية)

    حفظ_المخزون()
    تحديث_الجدول()
    مسح_الحقول()

    messagebox.showinfo(
        "تم",
        "تم سحب الكمية وتسجيل الاستهلاك"
    )


def حذف_الصنف():
    اسم = الحصول_على_الصنف()

    if اسم is None:
        return

    if not messagebox.askyesno(
        "تأكيد الحذف",
        f"هل تريد حذف الصنف {اسم}؟"
    ):
        return

    del المخزون[اسم]

    حفظ_المخزون()
    تحديث_الجدول()
    مسح_الحقول()

    messagebox.showinfo("تم", "تم حذف الصنف بنجاح")


def تنبيه_النواقص():
    try:
        الحد = float(حد_النواقص.get())
    except ValueError:
        messagebox.showerror("خطأ", "حد التنبيه غير صحيح")
        return

    الأصناف = []

    for اسم, بيانات in المخزون.items():
        if بيانات["كمية"] <= الحد:
            الأصناف.append(
                f"{اسم}: {بيانات['كمية']} {بيانات['وحدة']}"
            )

    if الأصناف:
        messagebox.showwarning(
            "الأصناف الناقصة",
            "\n".join(الأصناف)
        )
    else:
        messagebox.showinfo(
            "حالة المخزون",
            "لا توجد أصناف قريبة من النفاد"
        )


# ================= الهالك =================

def إضافة_هالك():
    اسم = الحصول_على_الصنف()

    if اسم is None:
        return

    الكمية = قراءة_الكمية(
        كمية_الهالك,
        "كمية الهالك"
    )

    if الكمية is None or الكمية <= 0:
        messagebox.showerror(
            "خطأ",
            "يجب أن تكون كمية الهالك أكبر من صفر"
        )
        return

    if الكمية > المخزون[اسم]["كمية"]:
        messagebox.showwarning(
            "تنبيه",
            "كمية الهالك أكبر من الكمية الموجودة"
        )
        return

    اليوم = datetime.now().strftime("%Y-%m-%d")
    السجل = تحميل_ملف(WASTE_FILE, {})

    السجل.setdefault(اليوم, {})
    السجل[اليوم][اسم] = السجل[اليوم].get(اسم, 0) + الكمية

    المخزون[اسم]["كمية"] -= الكمية

    حفظ_ملف(WASTE_FILE, السجل)
    حفظ_المخزون()
    تحديث_الجدول()

    كمية_الهالك.delete(0, "end")

    messagebox.showinfo(
        "تم",
        f"تم تسجيل الهالك: {الكمية} "
        f"{المخزون[اسم]['وحدة']}"
    )


def هالك_الشهر():
    الشهر = datetime.now().strftime("%Y-%m")
    السجل = تحميل_ملف(WASTE_FILE, {})
    الإجماليات = {}

    for اليوم, الأصناف in السجل.items():
        if اليوم.startswith(الشهر):
            for اسم, كمية in الأصناف.items():
                الإجماليات[اسم] = (
                    الإجماليات.get(اسم, 0) + كمية
                )

    if not الإجماليات:
        messagebox.showinfo(
            "هالك الشهر",
            "لا توجد بيانات هالك هذا الشهر"
        )
        return

    التقرير = []

    for اسم, كمية in sorted(الإجماليات.items()):
        الوحدة = المخزون.get(
            اسم,
            {}
        ).get("وحدة", "وحدة")

        التقرير.append(
            f"{اسم}: {كمية} {الوحدة}"
        )

    messagebox.showinfo(
        "إجمالي هالك الشهر",
        "\n".join(التقرير)
    )


# ================= تقرير يوم محدد =================

def تقرير_يوم_محدد():
    التاريخ = تاريخ_التقرير.get().strip()

    try:
        datetime.strptime(التاريخ, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror(
            "خطأ",
            "اكتب التاريخ بهذا الشكل:\n2026-09-18"
        )
        return

    سجل_الاستهلاك = تحميل_ملف(CONSUMPTION_FILE, {})
    سجل_الهالك = تحميل_ملف(WASTE_FILE, {})
    سجل_المخزون = تحميل_ملف(HISTORY_FILE, {})

    استهلاك_اليوم = سجل_الاستهلاك.get(التاريخ, {})
    هالك_اليوم = سجل_الهالك.get(التاريخ, {})
    مخزون_اليوم = سجل_المخزون.get(التاريخ, {})

    التقرير = [
        f"تقرير يوم: {التاريخ}",
        "",
        "الاستهلاك:"
    ]

    if استهلاك_اليوم:
        for اسم, كمية in استهلاك_اليوم.items():
            الوحدة = المخزون.get(
                اسم,
                {}
            ).get("وحدة", "وحدة")

            التقرير.append(
                f"- {اسم}: {كمية} {الوحدة}"
            )
    else:
        التقرير.append("- لا يوجد استهلاك")

    التقرير.append("")
    التقرير.append("الهالك:")

    if هالك_اليوم:
        for اسم, كمية in هالك_اليوم.items():
            الوحدة = المخزون.get(
                اسم,
                {}
            ).get("وحدة", "وحدة")

            التقرير.append(
                f"- {اسم}: {كمية} {الوحدة}"
            )
    else:
        التقرير.append("- لا يوجد هالك")

    التقرير.append("")
    التقرير.append("مخزون نهاية اليوم:")

    if مخزون_اليوم:
        for اسم, كمية in مخزون_اليوم.items():
            الوحدة = المخزون.get(
                اسم,
                {}
            ).get("وحدة", "وحدة")

            التقرير.append(
                f"- {اسم}: {كمية} {الوحدة}"
            )
    else:
        التقرير.append("- لم يتم حفظ إغلاق هذا اليوم")

    messagebox.showinfo(
        "تقرير اليوم",
        "\n".join(التقرير)
    )


# ================= الواجهة =================

root = tk.Tk()
root.title("الاصلي لإدارة المخزون")
root.geometry("1000x720")
root.configure(bg="#f3f3f3")

العنوان = tk.Label(
    root,
    text="الاصلي لإدارة المخزون",
    font=("Arial", 18, "bold"),
    bg="#f3f3f3"
)
العنوان.pack(pady=10)


إطار_الإدخال = tk.Frame(
    root,
    bg="white",
    bd=2,
    relief="groove",
    padx=15,
    pady=15
)
إطار_الإدخال.pack(fill="x", padx=20)


tk.Label(
    إطار_الإدخال,
    text="اسم الصنف",
    font=("Arial", 12),
    bg="white"
).grid(row=0, column=0, padx=8, pady=8)

اسم_الصنف = tk.Entry(
    إطار_الإدخال,
    width=22,
    font=("Arial", 12)
)
اسم_الصنف.grid(row=0, column=1, padx=8, pady=8)


tk.Label(
    إطار_الإدخال,
    text="الكمية",
    font=("Arial", 12),
    bg="white"
).grid(row=0, column=2, padx=8, pady=8)

كمية_الصنف = tk.Entry(
    إطار_الإدخال,
    width=15,
    font=("Arial", 12)
)
كمية_الصنف.grid(row=0, column=3, padx=8, pady=8)


tk.Label(
    إطار_الإدخال,
    text="الوحدة",
    font=("Arial", 12),
    bg="white"
).grid(row=1, column=0, padx=8, pady=8)

وحدة_الصنف = ttk.Combobox(
    إطار_الإدخال,
    values=UNIT_OPTIONS,
    width=19,
    state="readonly"
)
وحدة_الصنف.set("كجم")
وحدة_الصنف.grid(row=1, column=1, padx=8, pady=8)


tk.Label(
    إطار_الإدخال,
    text="حد التنبيه",
    font=("Arial", 12),
    bg="white"
).grid(row=1, column=2, padx=8, pady=8)

حد_النواقص = tk.Entry(
    إطار_الإدخال,
    width=15,
    font=("Arial", 12)
)
حد_النواقص.insert(0, "2")
حد_النواقص.grid(row=1, column=3, padx=8, pady=8)


tk.Label(
    إطار_الإدخال,
    text="الهالك",
    font=("Arial", 12),
    bg="white"
).grid(row=2, column=0, padx=8, pady=8)

كمية_الهالك = tk.Entry(
    إطار_الإدخال,
    width=15,
    font=("Arial", 12)
)
كمية_الهالك.grid(row=2, column=1, padx=8, pady=8)


tk.Label(
    إطار_الإدخال,
    text="تاريخ التقرير",
    font=("Arial", 12),
    bg="white"
).grid(row=3, column=0, padx=8, pady=8)

تاريخ_التقرير = tk.Entry(
    إطار_الإدخال,
    width=15,
    font=("Arial", 12)
)
تاريخ_التقرير.insert(
    0,
    datetime.now().strftime("%Y-%m-%d")
)
تاريخ_التقرير.grid(row=3, column=1, padx=8, pady=8)


# ================= الأزرار =================

إطار_الأزرار = tk.Frame(
    root,
    bg="#f3f3f3"
)
إطار_الأزرار.pack(pady=12)


def إنشاء_زر(النص, الدالة, النمط, الصف, العمود):
    زر = ttk.Button(
        إطار_الأزرار,
        text=النص,
        command=الدالة,
        style=f"{النمط}.TButton",
        width=18
    )
    زر.grid(
        row=الصف,
        column=العمود,
        padx=6,
        pady=6,
        ipadx=3,
        ipady=2
    )


إنشاء_زر(
    "إضافة صنف",
    اضافة_صنف,
    "Green",
    0,
    0
)

إنشاء_زر(
    "إضافة الكمية",
    اضافة_كمية,
    "Blue",
    0,
    1
)

إنشاء_زر(
    "تعديل الكمية",
    تعديل_الكمية,
    "Orange",
    0,
    2
)

إنشاء_زر(
    "سحب الكمية",
    سحب_الكمية,
    "Red",
    0,
    3
)

إنشاء_زر(
    "حذف الصنف",
    حذف_الصنف,
    "Purple",
    1,
    0
)

إنشاء_زر(
    "تنبيه النواقص",
    تنبيه_النواقص,
    "Gray",
    1,
    1
)

إنشاء_زر(
    "حفظ اليوم",
    حفظ_إغلاق_اليوم,
    "Teal",
    1,
    2
)

إنشاء_زر(
    "الاستهلاك الشهري",
    عرض_الاستهلاك_اليومي,
    "Purple",
    1,
    3
)

إنشاء_زر(
    "إضافة هالك",
    إضافة_هالك,
    "Pink",
    2,
    0
)

إنشاء_زر(
    "هالك الشهر",
    هالك_الشهر,
    "Blue",
    2,
    1
)

إنشاء_زر(
    "تقرير يوم محدد",
    تقرير_يوم_محدد,
    "Orange",
    2,
    2
)

إنشاء_زر(
    "تحديث العرض",
    تحديث_الجدول,
    "Gray",
    2,
    3
)

إنشاء_زر(
    "مسح الحقول",
    مسح_الحقول,
    "Cyan",
    3,
    0
)


# ================= جدول المخزون =================

الأعمدة = ("الصنف", "الكمية", "الوحدة")

tree = ttk.Treeview(
    root,
    columns=الأعمدة,
    show="headings",
    height=15
)

for عمود in الأعمدة:
    tree.heading(عمود, text=عمود)
    tree.column(
        عمود,
        anchor="center",
        width=250
    )

tree.pack(
    pady=10,
    padx=20,
    fill="both",
    expand=True
)


# ================= التشغيل =================

تحميل_المخزون()
تحديث_الجدول()
root.mainloop()