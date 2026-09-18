import streamlit as st
import json
import os

st.set_page_config(page_title="مخزون المطعم", page_icon="🍽️", layout="centered")

st.markdown(
    """
    <style>
    .stApp, .stApp * { direction: rtl; text-align: right; }
    div[data-testid="stMetricValue"] { direction: ltr; text-align: right; }
    </style>
    """,
    unsafe_allow_html=True,
)

ملف_البيانات = "inventory.json"


def تحميل_المخزون():
    if os.path.exists(ملف_البيانات):
        with open(ملف_البيانات, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def حفظ_المخزون():
    with open(ملف_البيانات, "w", encoding="utf-8") as f:
        json.dump(st.session_state.مخزون, f, ensure_ascii=False, indent=2)


if "مخزون" not in st.session_state:
    st.session_state.مخزون = تحميل_المخزون()


def اضافة_صنف(اسم, كمية, وحدة="كجم"):
    if اسم in st.session_state.مخزون:
        st.session_state.مخزون[اسم]["كمية"] += كمية
    else:
        st.session_state.مخزون[اسم] = {"كمية": كمية, "وحدة": وحدة}
    حفظ_المخزون()
    st.success(f"تم إضافة {كمية} {st.session_state.مخزون[اسم]['وحدة']} من {اسم}. الكمية الحالية: {st.session_state.مخزون[اسم]['كمية']}")


def صرف_صنف(اسم, كمية):
    if اسم not in st.session_state.مخزون:
        st.error(f"الصنف '{اسم}' مش موجود في المخزون.")
        return
    if st.session_state.مخزون[اسم]["كمية"] < كمية:
        st.warning(f"تنبيه: الكمية المطلوبة أكبر من المتاح! المتاح فقط {st.session_state.مخزون[اسم]['كمية']} {st.session_state.مخزون[اسم]['وحدة']}")
        return
    st.session_state.مخزون[اسم]["كمية"] -= كمية
    حفظ_المخزون()
    st.success(f"تم صرف {كمية} {st.session_state.مخزون[اسم]['وحدة']} من {اسم}. الباقي: {st.session_state.مخزون[اسم]['كمية']}")


def حذف_صنف(اسم):
    if اسم in st.session_state.مخزون:
        del st.session_state.مخزون[اسم]
        حفظ_المخزون()
        st.success(f"تم حذف {اسم} من المخزون.")


st.title("🍽️ نظام إدارة مخزون المطعم")

تبويب_اضافة, تبويب_صرف, تبويب_عرض = st.tabs(["➕ إضافة صنف", "➖ صرف صنف", "📋 المخزون الحالي"])

with تبويب_اضافة:
    st.subheader("إضافة أو تزويد صنف")
    with st.form("نموذج_اضافة", clear_on_submit=True):
        اسم_جديد = st.text_input("اسم الصنف")
        كمية_جديدة = st.number_input("الكمية", min_value=0.0, step=0.5)
        وحدة_جديدة = st.selectbox("الوحدة", ["كجم", "جرام", "لتر", "قطعة", "علبة"])
        زر_اضافة = st.form_submit_button("إضافة")
        if زر_اضافة:
            if اسم_جديد.strip() == "":
                st.error("لازم تكتب اسم الصنف.")
            else:
                اضافة_صنف(اسم_جديد.strip(), كمية_جديدة, وحدة_جديدة)

with تبويب_صرف:
    st.subheader("صرف كمية من صنف")
    if st.session_state.مخزون:
        with st.form("نموذج_صرف", clear_on_submit=True):
            اسم_للصرف = st.selectbox("اختر الصنف", list(st.session_state.مخزون.keys()))
            كمية_للصرف = st.number_input("الكمية المطلوب صرفها", min_value=0.0, step=0.5)
            زر_صرف = st.form_submit_button("صرف")
            if زر_صرف:
                صرف_صنف(اسم_للصرف, كمية_للصرف)
    else:
        st.info("المخزون فاضي، أضف أصناف الأول من تبويب الإضافة.")

with تبويب_عرض:
    st.subheader("الأصناف الموجودة")

    الحد_الادنى = st.slider("حد التنبيه (أقل من كام تعتبر ناقصة)", 0.0, 20.0, 3.0, step=0.5)

    if st.session_state.مخزون:
        for اسم, بيانات in st.session_state.مخزون.items():
            عمود1, عمود2, عمود3 = st.columns([3, 2, 1])
            with عمود1:
                st.write(f"**{اسم}**")
            with عمود2:
                لون = "🔴" if بيانات["كمية"] <= الحد_الادنى else "🟢"
                st.write(f"{لون} {بيانات['كمية']} {بيانات['وحدة']}")
            with عمود3:
                if st.button("حذف", key=f"حذف_{اسم}"):
                    حذف_صنف(اسم)
                    st.rerun()

        st.divider()
        نواقص = {اسم: بيانات for اسم, بيانات in st.session_state.مخزون.items() if بيانات["كمية"] <= الحد_الادنى}
        if نواقص:
            st.warning("⚠️ أصناف قربت تخلص: " + "، ".join(نواقص.keys()))
        else:
            st.success("كل الأصناف كمياتها كويسة ✅")
    else:
        st.info("المخزون فاضي.")
