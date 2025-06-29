# 🤖 LinkedIn Profile Optimizer

An AI-powered web application that helps users optimize their LinkedIn profiles for specific job roles using advanced profile analysis, job matching, and personalized recommendations.

## ✨ Features

- **🔐 User Authentication**: Secure sign-up and login with Supabase Auth
- **🔍 Profile Scraping**: Automated LinkedIn profile data extraction using Apify
- **🤖 AI-Powered Analysis**: Intelligent profile analysis using Google Gemini 2.0 Flash
- **🎯 Job Matching**: Compare profiles against specific job titles with match scores
- **💡 Smart Recommendations**: Get actionable suggestions to improve your profile
- **💬 Conversational AI**: Chat interface with conversation memory
- **📊 Profile Storage**: Secure profile data storage with Supabase
- **⚡ Real-time Updates**: Instant profile updates and analysis

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **AI Model**: Google Gemini 2.0 Flash (via Langchain)
- **Web Scraping**: Apify Client
- **Data Processing**: Pandas, JSON

## 📋 Prerequisites

Before running this application, ensure you have:

- Python 3.8 or higher
- A Supabase account and project
- An Apify account with API access
- A Google AI Studio API key
- Git (for cloning the repository)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd linkedin-profile-optimizer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your Supabase database**
   - Create a new table called `linkedinurls` with the following schema:
   ```sql
   CREATE TABLE linkedinurls (
     id SERIAL PRIMARY KEY,
     url TEXT NOT NULL,
     profile JSONB NOT NULL,
     user_id UUID NOT NULL REFERENCES auth.users(id),
     timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```

5. **Configure Streamlit secrets**
   Create a `.streamlit/secrets.toml` file in your project root:
   ```toml
   [default]
   SUPABASE_URL = "your-supabase-project-url"
   SUPABASE_KEY = "your-supabase-anon-key"
   APIFY_API_KEY = "your-apify-api-key"
   GOOGLE_API_KEY = "your-google-ai-studio-api-key"
   ```

## 🏃‍♂️ Running the Application

1. **Start the Streamlit application**
   ```bash
   streamlit run main.py
   ```

2. **Access the application**
   Open your browser and navigate to `http://localhost:8501`

## 📖 Usage Guide

### Getting Started

1. **Sign Up/Login**
   - Create a new account or login with existing credentials
   - Email verification is required for new accounts

2. **Add LinkedIn Profile**
   - Enter your LinkedIn profile URL in the sidebar
   - Click "Fetch new Profile Data or Update" to scrape your profile
   - Your profile will be stored securely in the database

3. **Set Job Title (Optional)**
   - Add a target job title for job-specific optimizations
   - This helps the AI provide more targeted recommendations

### AI Features

#### 📊 Profile Analysis
- Get detailed analysis of your profile's strengths and weaknesses
- Receive professional feedback on your profile effectiveness

#### 🎯 Job Matching
- Compare your profile against specific job requirements
- Get match scores out of 100 with detailed explanations
- Identify alignment areas and skill gaps

#### 💡 Smart Suggestions
- Receive actionable recommendations to improve your profile
- Get specific examples and prioritized improvements
- Tailored advice based on your target job role

#### 💬 Conversational AI
- Chat naturally with the AI about your profile
- Ask follow-up questions and get contextual responses
- The AI remembers your conversation history

## 🏗️ Project Structure

```
linkedin-profile-optimizer/
├── main.py              # Main Streamlit application
├── auth.py              # Authentication module
├── scrape_agent.py      # LinkedIn profile scraping
├── supabase_db.py       # Database operations
├── requirements.txt     # Python dependencies
├── .streamlit/
│   └── secrets.toml    # Configuration secrets
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

The application requires the following secrets in `.streamlit/secrets.toml`:

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Your Supabase project URL | ✅ |
| `SUPABASE_KEY` | Your Supabase anon/public key | ✅ |
| `APIFY_API_KEY` | Your Apify API key for web scraping | ✅ |
| `GOOGLE_API_KEY` | Your Google AI Studio API key | ✅ |

## 🔐 Security Features

- **Secure Authentication**: Supabase Auth with email verification
- **Data Encryption**: All data encrypted at rest and in transit
- **User Isolation**: Profile data is isolated per user
- **Session Management**: Secure session handling with automatic cleanup

## 🚨 Troubleshooting

### Common Issues

1. **Profile scraping fails**
   - Verify your Apify API key is correct
   - Ensure the LinkedIn URL is publicly accessible
   - Check your Apify account credits

2. **Authentication errors**
   - Verify Supabase URL and key are correct
   - Check if email verification is complete
   - Ensure Supabase Auth is properly configured

3. **AI responses not working**
   - Verify your Google API key is valid
   - Check your Google AI Studio quota
   - Ensure you have access to Gemini 2.0 Flash model

