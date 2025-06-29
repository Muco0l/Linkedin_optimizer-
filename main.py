import streamlit as st
import os
import pandas as pd
import scrape_agent, supabase_db
import ast
# Import project modules
import auth
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage

# --- Page Config ---
st.set_page_config(page_title="AI Recruitment Assistant", layout="wide",initial_sidebar_state="collapsed")

# --- App Pages ---

def login_page():
    """Displays the login and signup page."""
    st.title("🤖 Welcome to the Linkedin Profile Optimizer")
    st.markdown("Log in or create an account to manage your recruitment pipeline.")

    col1, col2 = st.columns(2)

    with col1:
        with st.form("login_form"):
            st.subheader("Login")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    success, error_message = auth.sign_in(email, password)
                    if success:
                        st.rerun()
                    else:
                        st.error(f"Login failed: {error_message}")

    with col2:
        with st.form("signup_form"):
            st.subheader("Create a New Account")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            signup_button = st.form_submit_button("Sign Up")

            if signup_button:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    user, error_message = auth.sign_up(email, password)
                    if user:
                        st.success("Signup successful! Please check your email for a verification link.")
                        st.info("Once your email is verified, you can log in.")
                    else:
                        st.error(f"Signup failed: {error_message}")



def main_dashboard():
    st.warning("You are successfully logged! Please add Job Title In Sidebar For job specific enhancements" )
    user_id = st.session_state['user'].id
    user_email = st.session_state['user'].email
    st.title("🤖 Welcome to the Linkedin Profile Optimizer")
    st.sidebar.markdown("---")

    # LinkedIn Input Section
    with st.sidebar.expander("Add LinkedIn", expanded=True):
        Linkedin_Url = st.text_input("LinkedIn URL")

        if st.button("Fetch Profile Data",use_container_width = True):
                if Linkedin_Url:
                    with st.spinner("Fetching profile data..."):
                        Profile = scrape_agent.get_profile(Linkedin_Url)
                        if "Error:" not in Profile:
                            jd_id = supabase_db.add_profile(Linkedin_Url, Profile, user_id)
                            if jd_id:
                                st.success(f"LinkedIn '{Linkedin_Url}' added successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to save profile to the database.")
                        else:
                            st.error(f"Failed to fetch profile: {Profile}")
                else:
                    st.warning("Please provide a LinkedIn URL.")
        Job_Title = st.text_input("Job Title", placeholder="e.g. Software Engineer")
        if st.button("Save Job Title", use_container_width=True):
            if Job_Title:
                st.session_state.job_title = Job_Title
                st.success(f"Job Title '{Job_Title}' saved successfully!")
            else:
                st.warning("Please provide a job title.")

    # Display Stored Profiles from DB
          
        user = st.session_state["user"]
        profiles = supabase_db.get_all_profiles(user.id)
        if profiles:
                    for profile in profiles:
                        st.sidebar.markdown(f"**Timestamp:** {profile['timestamp']}")
                        data = profile['profile']
                        decoded_text = json.loads(data)
                        st.write("### Stored Profiles")
                        st.markdown(f"```\n{decoded_text}\n```")
                        st.sidebar.markdown("---")
                    


                    st.sidebar.markdown("---")
                    

                
        else:
                        st.sidebar.markdown("_No profiles stored yet._")
    profiles = supabase_db.get_all_profiles(user.id)
    if profiles:
        message = st.chat_message("assistant")
        message.write("Hi,Got your amazing Profile")
        decoded_text = json.loads(data)
        message.write(f"```\n{decoded_text}\n```")
        st.divider()
        def init_llm():
            try:
                return ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash", 
                    temperature=0.7, 
                    google_api_key=st.secrets["GOOGLE_API_KEY"]
                )
            except Exception as e:
                st.error(f"Error initializing AI model: {e}")
                st.stop()

        llm = init_llm()

        # ------------------ Session State ------------------
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "profile" not in st.session_state:
            st.session_state.profile = (f"```\n{decoded_text}\n```")
        if "job_title" not in st.session_state:
            st.session_state.job_title = ""

        # ------------------ Helper Functions ------------------
        def get_ai_response(user_message):
            """Get response from AI based on user message and context"""
            
            # Prepare context
            profile_text = st.session_state.profile if st.session_state.profile.strip() else "Not provided"
            job_title_text = st.session_state.job_title if st.session_state.job_title.strip() else "Not provided"
            
            # Create messages directly without template
            messages = [
                HumanMessage(content=f"""You are a LinkedIn Profile Optimization expert and career coach. 

        Your capabilities:
        1. Profile Analysis: Analyze LinkedIn profiles for strengths and weaknesses
        2. Job Matching: Compare profiles against job requirements and give match scores
        3. Improvement Suggestions: Provide specific, actionable recommendations
        4. Career Advice: General LinkedIn and career guidance

        Context available:
        - User's LinkedIn Profile: {profile_text}
        - Target Job Title: {job_title_text}

        Instructions:
        - Be helpful, encouraging, and specific
        - Provide actionable advice with examples
        - If profile/job info is missing for specific tasks, politely ask for it
        - Keep responses well-structured and easy to read
        - Use bullet points and sections when helpful
        - Avoid Lengthy responses; be concise
        - take step by step approach while helping out in modification of profile
        - Use markdown formatting for clarity
        - If you need more information, ask the user directly
        - if user asks modification in certain task then help with that section only
        - if asked for job match then give the match score based on industry standard jd for{job_title_text}, if score asked then give score out of 100
        

        User's question: {user_message}""")
            ]
            
            try:
                response = llm.invoke(messages)
                return response.content
            except Exception as e:
                return f"Sorry, I encountered an error: {str(e)}"

        def display_chat_history():
            """Display the chat history"""
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # ------------------ Main Chat Interface ------------------

        # Display welcome message if no chat history
        if not st.session_state.chat_history:
            with st.chat_message("assistant"):
                st.markdown("""
                👋 **Welcome to your LinkedIn Profile Optimizer!**
                
                I can help you:
                - **Analyze** your LinkedIn profile for strengths and weaknesses
                - **Match** your profile against specific job requirements  
                - **Suggest** improvements to make your profile stand out
                - **Provide** general LinkedIn and career advice
                
                **Get started:**
                1. Add your LinkedIn profile text in the sidebar
                2. Optionally add a target job title
                3. Use the quick action buttons or just ask me anything!
                
                What would you like to work on today?
                """)

        # Display chat history
        display_chat_history()

        # Chat input
        if prompt := st.chat_input("Ask me anything about your LinkedIn profile..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get and display AI response
            with st.chat_message("assistant"):
                with st.spinner("Let me think..."):
                    ai_response = get_ai_response(prompt)
                    st.markdown(ai_response)
            
            # Add AI response to history
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

        # ------------------ Footer ------------------
            
        col1, col2 = st.columns(2)
            
        with col1:
                if st.button("📊 Analyze Profile", use_container_width=True):
                    if st.session_state.profile.strip():
                        user_msg = "Please analyze my LinkedIn profile in detail."
                        st.session_state.chat_history.append({"role": "user", "content": user_msg})
                        
                        with st.spinner("Analyzing..."):
                            ai_response = get_ai_response(user_msg)
                            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                        st.rerun()
                    else:
                        st.warning("Please add your profile first!")
            
        with col2:
                if st.button("🎯 Match Job", use_container_width=True):
                    if st.session_state.profile.strip() and st.session_state.job_title.strip():
                        user_msg = f"Please compare my profile with the {st.session_state.job_title} role and give me a match score."
                        st.session_state.chat_history.append({"role": "user", "content": user_msg})
                        
                        with st.spinner("Matching..."):
                            ai_response = get_ai_response(user_msg)
                            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                        st.rerun()
                    else:
                        st.warning("Please add both profile and job title!")
            
        if st.button("💡 Get Suggestions", use_container_width=True):
                if st.session_state.profile.strip():
                    job_context = f" for the {st.session_state.job_title} role" if st.session_state.job_title.strip() else ""
                    user_msg = f"Please give me specific suggestions to improve my LinkedIn profile{job_context}."
                    st.session_state.chat_history.append({"role": "user", "content": user_msg})
                    
                    with st.spinner("Generating suggestions..."):
                        ai_response = get_ai_response(user_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()
                else:
                    st.warning("Please add your profile first!")
            
            # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666; font-size: 0.8em;'>
            💼 LinkedIn Profile Optimizer | Built with Streamlit & Google Gemini
            </div>
            """, 
            unsafe_allow_html=True
        )
                
    else:
            st.warning("Please add a LinkedIn profile in the sidebar to get started.")
# Check if user is logged in    

if 'user' not in st.session_state:
    login_page()
else:
    main_dashboard()