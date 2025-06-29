import streamlit as st
import os
import pandas as pd
import scrape_agent, supabase_db
import ast
# Import project modules
import auth
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# --- Page Config ---
st.set_page_config(page_title="AI Recruitment Assistant", layout="wide",initial_sidebar_state="auto")

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
    st.warning("You are successfully logged in! Please add Job Title In Sidebar For job specific enhancements" )
    user_id = st.session_state['user'].id
    user_email = st.session_state['user'].email
    st.title("🤖 Welcome to the Linkedin Profile Optimizer")

    # LinkedIn Input Section
    st.sidebar.header("LinkedIn Profile Management")
    with st.sidebar.expander("Add LinkedIn", expanded=True):
        Linkedin_Url = st.text_input("LinkedIn URL")

        if st.button("Fetch new Profile Data or Update",use_container_width = True):
                if Linkedin_Url:
                    with st.spinner("Fetching profile data..."):
                        Profile = scrape_agent.get_profile(Linkedin_Url)
                        if "Error:" not in Profile:
                            jd_id = supabase_db.add_profile(Linkedin_Url, Profile, user_id)
                            if jd_id:
                                st.success(f"LinkedIn '{Linkedin_Url}' added successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to save profile to the database in sidebar.")
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
        message.write("If it is outdated, please update it in the sidebar.")
        st.divider()
        def init_llm():
            try:
                return ChatGoogleGenerativeAI(
                    model="gemini-2,0-flash", 
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
        if "llm_messages" not in st.session_state:
            st.session_state.llm_messages = []
        if "profile" not in st.session_state:
            st.session_state.profile = (f"```\n{decoded_text}\n```")
        if "job_title" not in st.session_state:
            st.session_state.job_title = ""

        # ------------------ Helper Functions ------------------
        def initialize_system_message():
            """Initialize the system message with context"""
            profile_text = st.session_state.profile if st.session_state.profile.strip() else "Not provided"
            job_title_text = st.session_state.job_title if st.session_state.job_title.strip() else "Not provided"
            
            system_message = f"""You are a LinkedIn Profile Optimization expert and career coach with access to conversation history.

Your capabilities:
1. Profile Analysis: Analyze LinkedIn profiles for strengths and weaknesses
2. Job Matching: Compare profiles against job requirements and give match scores
3. Improvement Suggestions: Provide specific, actionable recommendations
4. Career Advice: General LinkedIn and career guidance
5. Conversation Memory: Remember previous discussions and build upon them

Current Context:
- User's LinkedIn Profile: {profile_text}
- Target Job Title: {job_title_text}

Instructions:
- Be helpful, encouraging, and specific
- Provide actionable advice with examples
- Remember our conversation history and reference previous discussions when relevant
- If profile/job info is missing for specific tasks, politely ask for it
- Keep responses well-structured and easy to read
- Use bullet points and sections when helpful
- Be concise but comprehensive - provide exactly what's asked
- Take a step-by-step approach while helping with profile modifications
- Use markdown formatting for clarity
- If asked for modifications in certain sections, focus only on that section
- For job match requests, give match scores out of 100 based on industry standards
- Build upon previous suggestions and conversations
- If the user references something from earlier in our conversation, acknowledge it

Communication Style:
- Professional yet friendly
- Specific and actionable
- Concise but thorough
- Reference previous context when relevant"""

            return SystemMessage(content=system_message)

        def get_ai_response(user_message):
            """Get response from AI based on user message and full conversation context"""
            
            try:
                # If this is the first message or system message needs updating, reinitialize
                if not st.session_state.llm_messages or len(st.session_state.llm_messages) == 0:
                    st.session_state.llm_messages = [initialize_system_message()]
                
                # Add the new user message
                st.session_state.llm_messages.append(HumanMessage(content=user_message))
                
                # Get response from LLM with full conversation history
                response = llm.invoke(st.session_state.llm_messages)
                
                # Add AI response to LLM messages for memory
                st.session_state.llm_messages.append(AIMessage(content=response.content))
                
                return response.content
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                # Still add the error to maintain conversation flow
                st.session_state.llm_messages.append(AIMessage(content=error_msg))
                return error_msg

        def update_system_context():
            """Update system message when profile or job title changes"""
            if st.session_state.llm_messages:
                # Replace the first message (system message) with updated context
                st.session_state.llm_messages[0] = initialize_system_message()

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
                - **Remember** our conversation and build upon previous discussions
                
                **Get started:**
                1. Your LinkedIn profile is already loaded
                2. Optionally add a target job title in the sidebar
                3. Use the quick action buttons or just ask me anything!
                
                I'll remember our entire conversation, so feel free to ask follow-up questions or refer back to previous suggestions!
                
                What would you like to work on today?
                """)

        # Display chat history
        display_chat_history()

        # Chat input
        if prompt := st.chat_input("Ask me anything about your LinkedIn profile..."):
            # Add user message to display history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get and display AI response
            with st.chat_message("assistant"):
                with st.spinner("Let me think..."):
                    ai_response = get_ai_response(prompt)
                    st.markdown(ai_response)
            
            # Add AI response to display history
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

        # ------------------ Quick Action Buttons ------------------
            
        col1, col2 = st.columns(2)
            
        with col1:
                if st.button("📊 Analyze Profile", use_container_width=True):
                    if st.session_state.profile.strip():
                        user_msg = "Please analyze my LinkedIn profile in detail, focusing on strengths, weaknesses, and overall effectiveness."
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
                        user_msg = f"Please compare my profile with the {st.session_state.job_title} role and give me a detailed match score out of 100 with specific areas of alignment and gaps."
                        st.session_state.chat_history.append({"role": "user", "content": user_msg})
                        
                        with st.spinner("Matching..."):
                            ai_response = get_ai_response(user_msg)
                            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                        st.rerun()
                    else:
                        st.warning("Please add both profile and job title!")
            
        if st.button("💡 Get Suggestions", use_container_width=True):
                if st.session_state.profile.strip():
                    job_context = f" specifically for the {st.session_state.job_title} role" if st.session_state.job_title.strip() else ""
                    user_msg = f"Please give me specific, actionable suggestions to improve my LinkedIn profile{job_context}. Include examples and prioritize the most impactful changes."
                    st.session_state.chat_history.append({"role": "user", "content": user_msg})
                    
                    with st.spinner("Generating suggestions..."):
                        ai_response = get_ai_response(user_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()
                else:
                    st.warning("Please add your profile first!")
            
        # Additional utility buttons
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("🔄 Update Context", use_container_width=True):
                update_system_context()
                st.success("Context updated with latest profile and job title!")
                
        with col4:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.llm_messages = []
                st.success("Chat cleared! Starting fresh conversation.")
                st.rerun()

        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666; font-size: 0.8em;'>
            💼 LinkedIn Profile Optimizer | Built with Streamlit & Google Gemini | Now with Conversation Memory
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