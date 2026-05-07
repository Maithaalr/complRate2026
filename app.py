# HR Data Completion Dashboard — Streamlit Project

## app.py

```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="HR Dashboard", layout="wide")

# =========================
# REQUIRED FIELDS
# =========================

GENERAL_FIELDS = [
    'اسم الجهة التابعة',
    'الدائرة',
    'اسم الدائرة بالانجليزية',
    'الوحدة التنظيمية',
    'الوحدة التنظيمية بالانجليزية',
    'المسمى الوظيفي',
    'المسمى الوظيفي بالانجليزية',
    'الوظيفة',
    'الدرجة الوظيفية',
    'الدرجة الوظيفية بالانجليزية',
    'نوع الوظيفة',
    'الفئة الوظيفية',
    'المجموعة الوظيفية الرئيسية',
    'المجموعة الوظيفية الفرعية',
    'الرقم الوظيفي',
    'تاريخ التعيين',
    'مدة الخدمة',
    'نوع العقد',
    'اسم الموظف',
    'الاسم بالانجليزي',
    'تاريخ الميلاد',
    'العمر',
    'مكان الميلاد',
    'الجنسية',
    'الجنس',
    'الديانة',
    'الحالة الاجتماعية',
    'عدد الأبناء',
    'البريد الالكتروني',
    'رقم الهاتف',
    'العنوان المنطقة',
    'العنوان امارة',
    'اسم المشرف',
    'رقم المشرف',
    'بريد المشرف',
    'المستوى التعليمي',
    'التخصص',
    'المؤسسة التعليمية',
    'تاريخ انتهاء الدراسة',
    'درجة المؤهل',
    'هل المؤهل متوافق للوظيفة',
    'تاريخ التصديق',
    'رقم التصديق',
    'عدد سنوات الخبرة السابقة',
    'رقم الهوية',
    'تاريخ انتهاء الهوية',
    'رقم الجواز',
    'تاريخ اصدار الجواز',
    'تاريخ انتهاء الجواز',
    'مكان اصدار الجواز',
    'الرقم الموحد',
    'فئة التأمين الصحي',
    'إعاقة',
    'رقم المستند',
    'رقم التحقق'
]

EXPAT_FIELDS = [
    'رقم الإقامة',
    'تاريخ اصدار الإقامة',
    'تاريخ انتهاء الإقامة',
    'الكفيل'
]

EMIRATI_FIELDS = [
    'رقم خلاصة القيد',
    'رقم البلدة',
    'رقم الأسرة'
]

GCC_COUNTRIES = [
    'إماراتية',
    'السعودية',
    'الكويتية',
    'القطرية',
    'البحرينية',
    'العمانية'
]


# =========================
# FUNCTIONS
# =========================

def is_filled(value):
    if pd.isna(value):
        return False

    value = str(value).strip()

    invalid_values = ['', 'nan', 'none', 'null', '-', 'n/a']

    return value.lower() not in invalid_values



def get_required_fields(row):
    required_fields = GENERAL_FIELDS.copy()

    nationality = str(row['الجنسية']).strip()

    # Emirati fields
    if nationality == 'إماراتية':
        required_fields.extend(EMIRATI_FIELDS)

    # Expat fields
    elif nationality not in GCC_COUNTRIES:
        required_fields.extend(EXPAT_FIELDS)

    return required_fields



def calculate_completion(row):
    required_fields = get_required_fields(row)

    total_required = len(required_fields)

    completed = 0

    for field in required_fields:
        if field in row.index:
            if is_filled(row[field]):
                completed += 1

    percentage = (completed / total_required) * 100

    return round(percentage, 2)



def calculate_field_completion(df, field_name, condition=None):

    temp_df = df.copy()

    if condition is not None:
        temp_df = temp_df[condition]

    total = len(temp_df)

    if total == 0:
        return 0

    completed = temp_df[field_name].apply(is_filled).sum()

    return round((completed / total) * 100, 2)


# =========================
# UI
# =========================

st.title("📊 HR Data Quality Dashboard")

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=['xlsx', 'xls']
)

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    # =========================
    # CLEAN COLUMN NAMES
    # =========================

    df.columns = df.columns.str.strip()

    # =========================
    # CALCULATE COMPLETION
    # =========================

    df['نسبة الاستكمال'] = df.apply(calculate_completion, axis=1)

    # =========================
    # TABS
    # =========================

    tab1, tab2, tab3 = st.tabs([
        '📈 Dashboard',
        '✅ Data Completion',
        '🏢 Department Filter'
    ])

    # =========================================================
    # TAB 1
    # =========================================================

    with tab1:

        st.header("Dashboard")

        total_employees = len(df)

        male_count = len(df[df['الجنس'] == 'ذكر'])
        female_count = len(df[df['الجنس'] == 'أنثى'])

        avg_completion = round(df['نسبة الاستكمال'].mean(), 2)

        top_department = df['الدائرة'].value_counts().idxmax()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("إجمالي الموظفين", total_employees)
        col2.metric("متوسط الاستكمال", f"{avg_completion}%")
        col3.metric("الذكور", male_count)
        col4.metric("الإناث", female_count)

        st.markdown('---')

        st.subheader("أكثر دائرة فيها موظفين")

        st.info(top_department)

        # Gender Chart
        gender_df = df['الجنس'].value_counts().reset_index()
        gender_df.columns = ['الجنس', 'العدد']

        fig_gender = px.pie(
            gender_df,
            names='الجنس',
            values='العدد',
            title='توزيع الجنس'
        )

        st.plotly_chart(fig_gender, use_container_width=True)

        # Department Chart
        dep_df = df['الدائرة'].value_counts().reset_index()
        dep_df.columns = ['الدائرة', 'العدد']

        fig_dep = px.bar(
            dep_df,
            x='الدائرة',
            y='العدد',
            title='عدد الموظفين حسب الدائرة'
        )

        st.plotly_chart(fig_dep, use_container_width=True)

        # Nationality Chart
        nat_df = df['الجنسية'].value_counts().reset_index()
        nat_df.columns = ['الجنسية', 'العدد']

        fig_nat = px.bar(
            nat_df,
            x='الجنسية',
            y='العدد',
            title='توزيع الجنسيات'
        )

        st.plotly_chart(fig_nat, use_container_width=True)

    # =========================================================
    # TAB 2
    # =========================================================

    with tab2:

        st.header("Data Completion")

        overall_completion = round(df['نسبة الاستكمال'].mean(), 2)

        st.metric(
            'نسبة الاستكمال العامة',
            f'{overall_completion}%'
        )

        st.markdown('---')

        field_results = []

        # GENERAL FIELDS
        for field in GENERAL_FIELDS:

            if field in df.columns:

                completion = calculate_field_completion(df, field)

                field_results.append({
                    'الحقل': field,
                    'نسبة الاستكمال': completion
                })

        # EXPAT FIELDS
        expat_condition = ~df['الجنسية'].isin(GCC_COUNTRIES)

        for field in EXPAT_FIELDS:

            if field in df.columns:

                completion = calculate_field_completion(
                    df,
                    field,
                    expat_condition
                )

                field_results.append({
                    'الحقل': field,
                    'نسبة الاستكمال': completion
                })

        # EMIRATI FIELDS
        emirati_condition = df['الجنسية'] == 'الإمارات'

        for field in EMIRATI_FIELDS:

            if field in df.columns:

                completion = calculate_field_completion(
                    df,
                    field,
                    emirati_condition
                )

                field_results.append({
                    'الحقل': field,
                    'نسبة الاستكمال': completion
                })

        completion_df = pd.DataFrame(field_results)

        st.dataframe(
            completion_df,
            use_container_width=True
        )

        st.markdown('---')

        st.subheader('أقل الحقول استكمالاً')

        lowest_fields = completion_df.sort_values(
            by='نسبة الاستكمال'
        ).head(10)

        fig_low = px.bar(
            lowest_fields,
            x='الحقل',
            y='نسبة الاستكمال',
            title='الحقول الأقل استكمالاً'
        )

        st.plotly_chart(fig_low, use_container_width=True)

    # =========================================================
    # TAB 3
    # =========================================================

    with tab3:

        st.header('Department Filter')

        departments = sorted(df['الدائرة'].dropna().unique())

        selected_department = st.selectbox(
            'اختر الدائرة',
            departments
        )

        filtered_df = df[
            df['الدائرة'] == selected_department
        ]

        st.success(f'عدد الموظفين: {len(filtered_df)}')

        department_completion = round(
            filtered_df['نسبة الاستكمال'].mean(),
            2
        )

        st.metric(
            'نسبة الاستكمال للدائرة',
            f'{department_completion}%'
        )

        st.markdown('---')

        st.dataframe(filtered_df)

        dep_field_results = []

        # GENERAL FIELDS
        for field in GENERAL_FIELDS:

            if field in filtered_df.columns:

                completion = calculate_field_completion(
                    filtered_df,
                    field
                )

                dep_field_results.append({
                    'الحقل': field,
                    'نسبة الاستكمال': completion
                })

        dep_completion_df = pd.DataFrame(dep_field_results)

        st.subheader('نسبة استكمال الحقول')

        st.dataframe(dep_completion_df)

        fig_dep_completion = px.bar(
            dep_completion_df.sort_values(
                by='نسبة الاستكمال'
            ).head(10),
            x='الحقل',
            y='نسبة الاستكمال',
            title='أقل الحقول استكمالاً في الدائرة'
        )

        st.plotly_chart(
            fig_dep_completion,
            use_container_width=True
        )

else:

    st.info('Please upload Excel file')
