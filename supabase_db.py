#----IMPORTS----
from supabase import create_client, Client
import json
import streamlit as st
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]  

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_profile(linkedin_url, profile, user_id):
    try:
        response = supabase.table("linkedinurls").insert({
            "url": linkedin_url,
            "profile": json.dumps(profile),
            "user_id": user_id
        }).execute()

        if response.data:
            return response.data[0]["id"]
        else:
            print("Failed to insert record.")
            return None
    except Exception as e:
        print(f"Supabase SDK error (add_profile): {e}")
        return None

def get_all_profiles(user_id):
    try:
        response = supabase.table("linkedinurls").select("*").eq("user_id", user_id).order("timestamp", desc=True).limit(1) .execute()
        return response.data
    except Exception as e:
        print(f"Supabase SDK error (get_all_profiles): {e}")
        return []

def setup_database():
    print("Table should already be created via Supabase dashboard. Skipping setup.")