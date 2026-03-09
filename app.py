import streamlit as st
import pandas as pd

st.set_page_config(page_title="Team Task Tracker", layout="wide")

st.title("📋 Team Task Tracker")

# storage
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# sidebar
role = st.sidebar.selectbox(
"Role",
["Team Lead","Employee"]
)

user = st.sidebar.text_input("Enter Your Name")

# TEAM LEAD PANEL
if role == "Team Lead":

    st.header("Assign Task")

    emp = st.text_input("Assign To (Employee Name)")

    task = st.text_input("Task Description")

    priority = st.selectbox(
    "Priority",
    ["Red","Yellow","Green"]
    )

    status = st.selectbox(
    "Status",
    ["Assigned","WIP","DONE","EXPECTED"]
    )

    if st.button("Assign Task"):

        if emp and task:

            st.session_state.tasks.append(
            {
            "employee":emp,
            "task":task,
            "priority":priority,
            "status":status
            })

            st.success("Task Assigned")

# EMPLOYEE TASK VIEW
st.header("My Tasks")

if user:

    for i,t in enumerate(st.session_state.tasks):

        if t["employee"].lower() == user.lower():

            col1,col2,col3,col4 = st.columns([4,1,1,1])

            with col1:
                st.write(t["task"])

            with col2:
                st.write(t["priority"])

            with col3:

                new_status = st.selectbox(
                "Status",
                ["Assigned","WIP","DONE","EXPECTED"],
                index=["Assigned","WIP","DONE","EXPECTED"].index(t["status"]),
                key=i
                )

                st.session_state.tasks[i]["status"] = new_status

            with col4:

                if st.button("Delete", key=f"d{i}"):

                    st.session_state.tasks.pop(i)
                    st.rerun()

# COPY UPDATE
st.header("Task Update (Copy to Teams / Email)")

output = ""

count = 1

for t in st.session_state.tasks:

    if user and t["employee"].lower() == user.lower():

        output += f"{count}) {t['task']} - {t['status']}\n"
        count += 1

st.text_area("", output, height=200)

# CLEAR TASKS
if role == "Team Lead":

    if st.button("Clear All Tasks"):

        st.session_state.tasks = []
        st.success("All tasks cleared")