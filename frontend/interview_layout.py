import uuid, time, json
from langgraph.types import Command
from langchain_core.messages import HumanMessage
import streamlit as st
from backend.interview_server import interviewbot
from backend.utilities import load_interview_rules
from utilities import set_multi_states, set_state, _render_tool_message, read_message_text_aloud, record_audio_messages, stop_audio_recording

# Container for Q&A
q_n_a_container = st.empty()

@st.fragment(run_every=1)
def render_timer(end_time, total_time, question):
    remaining = end_time - time.time()
    if remaining > 0:
        progress = min(remaining / total_time, 1.0)
        st.progress(progress, text=f"Time Remaining: {int(remaining)}s")
        st.caption("Note: Please press Ctrl+Enter to save your draft answer before time runs out.")
    else:
        submit_answer(st.session_state["q&a_config"], question, True)

def start_new_interview():
    st.query_params.clear()
    st.session_state["interview_status"] = "format-selection"
    del st.session_state["candidate_info"]
    del st.session_state["bot_response"]
    if "clock_ends_at" in st.session_state: del st.session_state["clock_ends_at"]
    del st.session_state["q&a_config"]
    del st.session_state["format"]

def interview_report():
    with st.spinner(":hourglass: :blue[Loading Data] - :grey[Building PDF Report...] *Please wait patiently* :gear:"):
        report_response = interviewbot.invoke(
            {"messages": [HumanMessage("Generate a PDF report of the conversion and evaluation of the interview. Keep the evaluation intact and don't try to summarise it")], "phase": "reporting"},
            st.session_state["q&a_config"]
        )
        _render_tool_message(json.loads(report_response["messages"][-2].content.replace("'", '"')), 1)
    st.success(":white_check_mark: :green[PDF Report Generated Successfully]")

def render_rules(rules: dict) -> None:
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Interview format: {rules['format']}")
            st.write(f"Time frame: {rules['time_frame'] * rules['no_of_questions']} minutes")
        with col2:
            st.write(f"Number of questions: {rules['no_of_questions']}")
            st.write(f"Question duration: {rules['time_frame']} minutes")

def render_verdict(data: dict, level: int = 0) -> None:
    for key, value in data.items():
        formatted_key = key.replace("_", " ").title()
        
        if isinstance(value, str):
            st.write(f"**{formatted_key}:** {value}")
                
        elif isinstance(value, list):
            st.write(f"**{formatted_key}:**")
            for index, item in enumerate(value, 1):
                if isinstance(item, dict):
                    render_verdict(item, level + 1)
                else:
                    st.write(f"{index}. {item}")
        elif isinstance(value, dict):
            st.write(f"**{formatted_key}:**")
            render_verdict(value, level + 1)

def start_interview(candidate_name: str, candidate_desired_role: str, candidate_preferred_companies: str) -> None:
    if not candidate_name or not candidate_desired_role:
        st.error("Candidate name and desired role are required")
        return

    set_multi_states({
        "candidate_info": {
            "name": candidate_name,
            "desired_role": candidate_desired_role,
            "preferred_companies": candidate_preferred_companies
        },
        "interview_status": "q&a"
    })

def submit_answer(
    config: dict, question: str, rerun: bool = False
) -> None:
    with st.spinner("Submitting Answer..."):
        stop_audio_recording()
        answer = st.session_state.get(question, "")
        bot_response = interviewbot.invoke(Command(resume=answer), config)
    st.session_state["bot_response"] = bot_response
    if "clock_ends_at" in st.session_state:
        del st.session_state["clock_ends_at"]
    if rerun: st.rerun()

def render_format_selection():
    interview_rules = load_interview_rules()
    interview_formats = interview_rules.keys()

    q_n_a_container.empty()
    with q_n_a_container.container():
        st.title("Interview AI")
        st.subheader("Select Interview Format")

        for format in interview_formats:
            if format == "comments": continue

            no_of_questions = interview_rules[format]["no_of_questions"]
            time_frame = interview_rules[format]["time_frame"]
            st.button(
                f"{format.title()} Format Interview",
                help=f"{no_of_questions} questions interview with {time_frame} minute/minutes each question",
                on_click=set_multi_states,
                args=[{
                    "format": format,
                    "interview_status": "information-collection"
                }]
            )

def render_candidate_info():
    q_n_a_container.empty()
    with q_n_a_container.container():
        st.title("Interview AI")
        st.subheader("Candidate Information")
        candidate_name = st.text_input(
            "Full Name :blue[(required)]"
        )
        candidate_desired_role =  st.text_input(
            "Desired Job Role :blue[(required)]"
        )
        candidate_preferred_companies = st.text_input(
            "Preferred Companies :blue[(optional - comma separated names)]"
        )
        st.button("Start Interview", on_click=start_interview, args=(
            candidate_name, candidate_desired_role, candidate_preferred_companies
        ))

def render_q_n_a():
    q_n_a_container.empty()
    
    # Initialize Interview if needed
    if "q&a_config" not in st.session_state:
        with st.spinner("Loading Question..."):
            interview_thread_id = str(uuid.uuid4())
            st.session_state["q&a_config"] = {"configurable": {"thread_id": interview_thread_id}}
            st.query_params["thread_id"] = interview_thread_id
            st.session_state["bot_response"] = interviewbot.invoke({
                "messages": [{"role": "user", "content": "Start Interview"}],
                "phase": "q&a",
                "rules": {"format": st.session_state["format"]}
            }, st.session_state["q&a_config"])

    # Process Interrupts
    if st.session_state.get("bot_response") and "__interrupt__" in st.session_state["bot_response"]:
        config = st.session_state["q&a_config"]
        bot_response = st.session_state["bot_response"]
        interrupt_message = bot_response['__interrupt__'][0].value

        if isinstance(interrupt_message, str):
            # Auto-fill info logic
            if "full name" in interrupt_message.lower():
                with st.spinner("Loading Question..."):
                    bot_response = interviewbot.invoke(
                        Command(resume=st.session_state["candidate_info"]["name"]), config
                    )
            elif "job role" in interrupt_message.lower():
                with st.spinner("Loading Question..."):
                    bot_response = interviewbot.invoke(
                        Command(resume=st.session_state["candidate_info"]["desired_role"]), config
                    )
            elif "names of companies" in interrupt_message.lower():
                with st.spinner("Loading Question..."):
                    bot_response = interviewbot.invoke(
                        Command(resume=st.session_state["candidate_info"]["preferred_companies"]), config
                    )
            
            st.session_state["bot_response"] = bot_response
            st.rerun()
        else:
            # Question Phase
            with q_n_a_container.container():
                st.title("Interview AI")
                render_rules(bot_response["rules"])
                
                st.write(f"**Question:** {interrupt_message.question}")
                st.caption(f"Asked by: {interrupt_message.companies} | Type: {interrupt_message.type}")
                
                if interrupt_message.type.lower() == "practical":
                    answer = st.text_area("Answer:", key=interrupt_message.question, placeholder="Write your answer here...")
                else: answer = ""

                if "clock_ends_at" not in st.session_state:
                    read_message_text_aloud(interrupt_message.question)
                    time_limit = bot_response.get("rules", {}).get("time_frame", 1) * 60
                    st.session_state["clock_ends_at"] = time.time() + time_limit
                
                st.button("Submit Answer", key=f"btn_{interrupt_message.question}", on_click=submit_answer, args=(config, interrupt_message.question))
                st.caption("Note: Please do not refresh the page while answering question as it will auto-submit your current answer with empty text value.")
                record_audio_messages(interrupt_message.question)
                total_time = bot_response["rules"]["time_frame"] * 60
                render_timer(
                    st.session_state["clock_ends_at"],
                    total_time,
                    interrupt_message.question
                )
    else:
        # No interrupt means interview is done
        set_state("interview_status", "evaluation")
        st.rerun()

def render_evaluation():
    q_n_a_container.empty()
    if "bot_response" in st.session_state and st.session_state["bot_response"]["messages"]:
        last_msg = st.session_state["bot_response"]["messages"][-1]
        if hasattr(last_msg, "content"):
            try:
                evaluation = json.loads(last_msg.content)
                with q_n_a_container.container():
                    st.title("Interview AI")
                    st.subheader("Evaluation")
                    render_verdict(evaluation)
            except json.JSONDecodeError:
                st.error("Failed to parse evaluation data.")
