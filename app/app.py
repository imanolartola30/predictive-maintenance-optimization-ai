import os
import sys
import importlib
import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(os.path.expanduser("~/.env"), override=True)
load_dotenv(ENV_PATH, override=True)

sys.path.append(os.path.join(PROJECT_ROOT, "src"))

import rag_copilot
importlib.reload(rag_copilot)
from rag_copilot import MaintenanceRAGCopilot

st.set_page_config(page_title="Predictive Maintenance · MILP & AI Copilot", layout="wide")

st.title("⚙️ Industrial Predictive Maintenance · 8h Shift Optimizer & AI Copilot")
st.caption("End-to-End System: LightGBM Failure Prediction (24h) + Pyomo/HiGHS Shift Scheduling + Technical RAG Copilot")

copilot = MaintenanceRAGCopilot(PROJECT_ROOT)
df_sched = copilot.df_schedule

tab1, tab2 = st.tabs([
    "🤖 1. AI Maintenance Copilot (RAG)",
    "📅 2. 8-Hour Shift Schedule (MILP)"
])

with tab1:
    left_col, right_col = st.columns([1.0, 1.2])

    with left_col:
        st.subheader("Select Scheduled Machine")
        machine_ids = df_sched["machineID"].tolist()
        selected_m = st.selectbox(
            "Choose a machine from this week's schedule:",
            options=machine_ids,
            format_func=lambda m: (
                f"Machine #{m} ({df_sched.loc[df_sched['machineID']==m, 'model'].values[0]}) — "
                f"{df_sched.loc[df_sched['machineID']==m, 'shift'].values[0]} — "
                f"Risk in {df_sched.loc[df_sched['machineID']==m, 'pred_comp'].values[0]}"
            )
        )
        s_row = df_sched[df_sched["machineID"] == selected_m].iloc[0]

        st.markdown(f"""
        * **Machine ID & Model:** `Machine #{s_row['machineID']}` (`{s_row['model']}`)
        * **Predicted Component at Risk:** `{s_row['pred_comp']}`
        * **Real Audit Outcome:** **{s_row['outcome']}** (Real failure: `{s_row['real_failure']}`)
        * **Assigned 8-Hour Shift (MILP):** `{s_row['shift']}` (Duration: `{s_row['repair_hours']} hours`)
        * **Preventive Cost:** `{s_row['prev_cost']:.0f} EUR` · **Real Net Savings:** `{s_row['real_net_savings']:+.0f} EUR`
        """)

    with right_col:
        st.subheader("💬 Shop-Floor Technical Copilot (Official Manual RAG)")

        try:
            if "GEMINI_API_KEY" in st.secrets and not os.environ.get("GEMINI_API_KEY"):
                os.environ["GEMINI_API_KEY"] = str(st.secrets["GEMINI_API_KEY"]).strip()
        except Exception:
            pass
        if "gemini_key" in st.session_state and st.session_state["gemini_key"]:
            os.environ["GEMINI_API_KEY"] = st.session_state["gemini_key"]

        current_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if len(current_key) > 15:
            st.success("✅ Connected to **Gemini AI** (`GEMINI_API_KEY` active)")
        else:
            st.info("ℹ️ **Offline RAG Mode active** (or paste a `GEMINI_API_KEY` below to enable live Gemini AI generation):")
            new_key = st.text_input("Optional — Paste your GEMINI_API_KEY here:", type="password", placeholder="AIzaSy...")
            if st.button("Activate Gemini API Key"):
                if len(new_key.strip()) > 15:
                    st.session_state["gemini_key"] = new_key.strip()
                    os.environ["GEMINI_API_KEY"] = new_key.strip()
                    try:
                        with open(ENV_PATH, "w", encoding="utf-8") as f:
                            f.write(f"GEMINI_API_KEY={new_key.strip()}\n")
                    except Exception:
                        pass
                    st.rerun()
                else:
                    st.error("Please paste a valid Gemini API key (starts with AIza...).")

        lang_choice = st.radio(
            "Language / Idioma / Hizkuntza:",
            options=["en", "es", "eu"],
            horizontal=True,
            format_func=lambda x: {"en": "English", "es": "Castellano", "eu": "Euskara"}[x]
        )
        placeholders = {
            "en": f"e.g., How much does it cost to repair {s_row['pred_comp']}? / What is the tightening torque?",
            "es": f"Ej: ¿A cuántos Nm aprieto {s_row['pred_comp']}? / ¿Cuánto cuesta repararla? / ¿Cuándo le toca turno?",
            "eu": f"Adib: Zenbat Nm-ra estutu behar dut {s_row['pred_comp']}? / Zein txandatan konponduko da?"
        }
        input_labels = {
            "en": "Ask any question about this machine or the maintenance manual:",
            "es": "Escribe tu pregunta sobre esta máquina o el manual de taller:",
            "eu": "Idatzi zure galdera makina honi edo eskuliburuari buruz:"
        }
        btn_labels = {
            "en": "Ask AI Copilot (RAG)",
            "es": "Preguntar al Copiloto IA (RAG)",
            "eu": "Galdetu IA Kopilotuari (RAG)"
        }
        user_q = st.text_input(input_labels[lang_choice], value="", placeholder=placeholders[lang_choice])
        if st.button(btn_labels[lang_choice], type="primary"):
            query_to_send = user_q.strip() if user_q.strip() else placeholders[lang_choice]
            res = copilot.ask_copilot(query_to_send, machine_id=int(selected_m), lang=lang_choice)
            st.markdown(res["answer"])
            with st.expander("View retrieved sections from docs/technical_manual.md (TF-IDF Cosine Similarity)"):
                for c in res["retrieved_chunks"]:
                    st.markdown(f"**{c['title']} ({c['page']}) — Cosine Similarity: `{c['similarity_score']}`**")
                    st.code(c["content"], language="markdown")

with tab2:
    st.subheader("Weekly 8-Hour Shift Schedule (Pyomo + HiGHS)")
    st.dataframe(df_sched, use_container_width=True)
    sched_img = os.path.join(PROJECT_ROOT, "img", "milp_schedule.png")
    if os.path.exists(sched_img):
        st.image(sched_img, caption="Figure: Technician 8-Hour Shift Schedule & Model Protection")
