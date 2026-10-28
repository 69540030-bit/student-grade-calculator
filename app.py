import streamlit as st
import pandas as pd
from io import StringIO

# เกณฑ์เกรดมาตรฐานตัวอย่าง สามารถปรับให้ตรงกับเกณฑ์ของรายวิชาได้
GRADE_RULES = [
    (80, "A", 4.0),
    (75, "B+", 3.5),
    (70, "B", 3.0),
    (65, "C+", 2.5),
    (60, "C", 2.0),
    (55, "D+", 1.5),
    (50, "D", 1.0),
    (0, "F", 0.0),
]

def get_grade(score):
    """คืนค่าเกรดตัวอักษรและคะแนนเกรดจากคะแนน 0–100"""
    for minimum, letter, point in GRADE_RULES:
        if score >= minimum:
            return letter, point
    return "F", 0.0

def calculate_results(courses):
    """คำนวณเกรดรายวิชาและ GPA แบบถ่วงน้ำหนักตามหน่วยกิต"""
    results = []
    total_credits = 0
    total_weighted_points = 0

    for course in courses:
        name = course["name"].strip() or "ไม่ระบุชื่อวิชา"
        credits = int(course["credits"])
        score = float(course["score"])

        if not 0 <= score <= 100:
            raise ValueError(f"คะแนนของวิชา {name} ต้องอยู่ระหว่าง 0 ถึง 100")
        if credits <= 0:
            raise ValueError(f"หน่วยกิตของวิชา {name} ต้องมากกว่า 0")

        letter, point = get_grade(score)
        weighted = point * credits
        results.append({
            "รายวิชา": name,
            "หน่วยกิต": credits,
            "คะแนน": score,
            "เกรด": letter,
            "คะแนนเกรด": point,
            "คะแนนเกรด x หน่วยกิต": weighted,
        })
        total_credits += credits
        total_weighted_points += weighted

    gpa = total_weighted_points / total_credits if total_credits > 0 else 0.0
    return results, total_credits, gpa

st.set_page_config(page_title="โปรแกรมคำนวณเกรดนักศึกษา", page_icon="🎓", layout="wide")
st.title("🎓 โปรแกรมคำนวณเกรดนักศึกษา")
st.write("กรอกคะแนนรายวิชาและหน่วยกิต เพื่อดูเกรดรายวิชาและ GPA โดยประมาณ")
st.info("เกณฑ์ตัวอย่าง: A ≥ 80, B+ ≥ 75, B ≥ 70, C+ ≥ 65, C ≥ 60, D+ ≥ 55, D ≥ 50, F < 50 คะแนน ควรตรวจสอบเกณฑ์จริงของมหาวิทยาลัยก่อนใช้งาน")

course_count = st.number_input("จำนวนรายวิชา", min_value=1, max_value=12, value=3, step=1)
courses = []

with st.form("grade_form"):
    st.subheader("ข้อมูลรายวิชา")
    for i in range(int(course_count)):
        st.markdown(f"**วิชาที่ {i + 1}**")
        col1, col2, col3 = st.columns([3, 1, 2])
        with col1:
            name = st.text_input("ชื่อรายวิชา", value=f"รายวิชา {i + 1}", key=f"name_{i}")
        with col2:
            credits = st.number_input("หน่วยกิต", min_value=1, max_value=6, value=3, step=1, key=f"credits_{i}")
        with col3:
            score = st.number_input("คะแนน (0–100)", min_value=0.0, max_value=100.0, value=75.0, step=0.5, key=f"score_{i}")
        courses.append({"name": name, "credits": credits, "score": score})
    submitted = st.form_submit_button("คำนวณเกรด")

if submitted:
    try:
        results, total_credits, gpa = calculate_results(courses)
        df = pd.DataFrame(results)
        st.subheader("ผลการคำนวณ")
        left, middle, right = st.columns(3)
        left.metric("จำนวนวิชา", len(results))
        middle.metric("หน่วยกิตรวม", total_credits)
        right.metric("GPA", f"{gpa:.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # สร้างไฟล์ CSV เพื่อให้ผู้ใช้บันทึกผลลัพธ์ได้
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="ดาวน์โหลดผลการคำนวณ (CSV)",
            data=csv_data,
            file_name="grade_results.csv",
            mime="text/csv",
        )
        st.caption("หมายเหตุ: GPA นี้คำนวณจากคะแนนเกรดคูณหน่วยกิต และหารด้วยหน่วยกิตรวม")
    except ValueError as error:
        st.error(str(error))
else:
    st.caption("กรอกข้อมูลให้ครบ แล้วกด “คำนวณเกรด” เพื่อแสดงผล")
