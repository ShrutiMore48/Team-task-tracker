import streamlit as st
import pandas as pd
from datetime import datetime
from plyer import notification
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Daily Task Tracker", layout="wide")

DATA_FILE="tasks.csv"

# -----------------------
# LOAD DATA
# -----------------------

def load_data():
    try:
        df=pd.read_csv(DATA_FILE)
        df["Start"]=pd.to_datetime(df["Start"],errors="coerce")
        df["Pause"]=pd.to_datetime(df["Pause"],errors="coerce")
        return df
    except:
        return pd.DataFrame(columns=[
            "Priority","Study","Task","Task Type",
            "Estimated Effort","Actual Effort",
            "Status","Start","Pause","Paused Time"
        ])

def save(df):
    df.to_csv(DATA_FILE,index=False)

df=load_data()

st_autorefresh(interval=5000,key="timer")

st.title("📋 Daily Task Tracker")

# -----------------------
# ADD TASK
# -----------------------

st.subheader("➕ Add Task")

c1,c2,c3,c4,c5=st.columns(5)

priority=c1.number_input("Priority",1,20,1)

study=c2.text_input("Study")

task=c3.text_input("Task")

task_type=c4.selectbox(
    "Task Type",
    ["Work Task","Meeting","Training","Break"]
)

est=c5.number_input(
    "Estimated Effort (hr)",
    min_value=0.0,
    max_value=50.0,
    value=0.5,
    step=0.1
)

if st.button("Add Task"):

    new=pd.DataFrame([{
        "Priority":priority,
        "Study":study,
        "Task":task,
        "Task Type":task_type,
        "Estimated Effort":est,
        "Actual Effort":"",
        "Status":"PENDING",
        "Start":"",
        "Pause":"",
        "Paused Time":0
    }])

    df=pd.concat([df,new],ignore_index=True)

    save(df)

    st.success("Task Added")

# -----------------------
# TASK MANAGEMENT
# -----------------------

st.subheader("⚙ Task Management")

col1,col2=st.columns(2)

# CLEAR ALL TASKS

with col1:

    confirm=st.checkbox("Confirm clear all tasks")

    if confirm and st.button("🗑 Clear All Tasks"):

        df=pd.DataFrame(columns=df.columns)

        save(df)

        st.success("All tasks cleared")

        st.rerun()

# DELETE SPECIFIC TASK

with col2:

    if len(df)>0:

        task_delete=st.selectbox(
            "Select task to delete",
            df.index,
            format_func=lambda x: f"{df.loc[x,'Priority']} | {df.loc[x,'Study']} | {df.loc[x,'Task']}"
        )

        if st.button("Delete Selected Task"):

            df=df.drop(task_delete)

            save(df)

            st.success("Task deleted")

            st.rerun()

# -----------------------
# TASK EXECUTION
# -----------------------

st.subheader("▶ Task Execution")

for i,row in df.iterrows():

    c1,c2,c3,c4,c5,c6=st.columns([1,2,4,2,2,2])

    p=row["Priority"]

    if p<=2:
        color="red"
    elif p<=5:
        color="orange"
    else:
        color="green"

    c1.markdown(
        f"<span style='background:{color};color:white;padding:4px 8px;border-radius:6px'>{p}</span>",
        unsafe_allow_html=True
    )

    c2.write(row["Study"])

    c3.write(row["Task"])

    status=row["Status"]

# ---------- PENDING ----------

    if status=="PENDING":

        if c4.button("Start",key=f"start{i}"):

            df.at[i,"Status"]="WIP"

            df.at[i,"Start"]=datetime.now()

            save(df)

            st.rerun()

# ---------- WIP ----------

    elif status=="WIP":

        start=row["Start"]

        if pd.notna(start):

            elapsed=(datetime.now()-start).total_seconds()/3600

            c4.write(f"⏱ {elapsed:.2f} hr")

        if c5.button("Pause",key=f"pause{i}"):

            df.at[i,"Pause"]=datetime.now()

            df.at[i,"Status"]="PAUSED"

            save(df)

            st.rerun()

        if c6.button("Complete",key=f"done{i}"):

            elapsed=(datetime.now()-start).total_seconds()/3600

            df.at[i,"Actual Effort"]=round(elapsed,2)

            df.at[i,"Status"]="DONE"

            save(df)

            notification.notify(
                title="Task Completed",
                message=row["Task"],
                timeout=4
            )

            st.rerun()

# ---------- PAUSED ----------

    elif status=="PAUSED":

        if c4.button("Resume",key=f"resume{i}"):

            pause=row["Pause"]

            paused=(datetime.now()-pause).total_seconds()/3600

            df.at[i,"Paused Time"]=row["Paused Time"]+paused

            df.at[i,"Status"]="WIP"

            save(df)

            st.rerun()

# ---------- DONE ----------

    elif status=="DONE":

        c4.success("DONE")

        if row["Task Type"]=="Work Task":

            st.write("Checklist followed")

            colA,colB,colC=st.columns(3)

            colA.checkbox("Yes",key=f"yes{i}")

            colB.checkbox("No",key=f"no{i}")

            colC.checkbox("Reminder optional",key=f"rem{i}")

# -----------------------
# KANBAN BOARD
# -----------------------

st.subheader("📌 Kanban Board")

col1,col2,col3=st.columns(3)

col1.markdown("### PENDING")

for _,r in df[df["Status"]=="PENDING"].iterrows():

    col1.info(f"{r['Study']} - {r['Task']}")

col2.markdown("### WIP")

for _,r in df[df["Status"].isin(["WIP","PAUSED"])].iterrows():

    col2.warning(f"{r['Study']} - {r['Task']}")

col3.markdown("### DONE")

for _,r in df[df["Status"]=="DONE"].iterrows():

    col3.success(f"{r['Study']} - {r['Task']}")

# -----------------------
# TEAMS UPDATE
# -----------------------

st.subheader("📊 Task Update (Copy to Teams / Email)")

update=df.sort_values("Priority")

lines=[]

i=1

for _,row in update.iterrows():

    lines.append(
        f"{i}) {row['Study']} - {row['Task']} - {row['Status']}"
    )

    i+=1

msg="\n".join(lines)

st.text_area(
"Copy below text",
msg,
height=200
)

if st.button("Generate Teams Update"):

    st.code(msg)