import streamlit as st
from supabase import create_client, Client

import os
# Load environment variables    
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def sign_up(email, password):
    """Signs up a new user using Supabase Auth."""
    try:
        result = supabase.auth.sign_up({"email": email, "password": password})
        return result, None
    except Exception as e:
        return None, str(e)

def sign_in(email, password):
    """Signs in an existing user and stores session info in Streamlit state."""
    try:
        session = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state['user'] = session.user
        st.session_state['session'] = session
        return True, None
    except Exception as e:
        return False, str(e)

def sign_out():
    """Logs out the user and clears session data."""
    st.session_state.pop('user', None)
    st.session_state.pop('session', None)
    st.rerun()