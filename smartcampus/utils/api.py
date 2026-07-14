import os
import requests
from config import OPENAI_API_KEY

def get_campus_weather():
    """Simulates real-time campus weather data to make the UI feel active and premium."""
    return {
        "temp": "72°F / 22°C",
        "condition": "Sunny",
        "humidity": "45%",
        "wind": "8 mph",
        "emoji": "☀️"
    }

def get_campus_insights(students_count, faculty_count, attendance_pct):
    """Generates dynamic administrative insights. Uses OpenAI if key is present, otherwise falls back to a rule-based engine."""
    if OPENAI_API_KEY and OPENAI_API_KEY != "YOUR_API_KEY_HERE" and len(OPENAI_API_KEY.strip()) > 10:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            prompt = (
                f"You are the Smart Campus AI Assistant. Based on current stats: "
                f"Total Students = {students_count}, Total Faculty = {faculty_count}, "
                f"Average Attendance = {attendance_pct}%. "
                f"Provide 3 short, actionable, bulleted recommendations (max 20 words each) for campus admin."
            )
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150,
                "temperature": 0.7
            }
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return content
        except Exception:
            pass # Fall back to rule-based insights if request fails
            
    # Rule-based fallback insights
    insights = []
    
    # 1. Attendance Check
    if attendance_pct < 75:
        insights.append("- 🔴 **Attendance Decline**: Attendance is below critical threshold. Setup check-ins for students with >3 consecutive absences.")
    elif attendance_pct < 88:
        insights.append("- 🟡 **Attendance Action**: Attendance is moderate. Remind faculty to log daily attendance before 4 PM.")
    else:
        insights.append("- 🟢 **Attendance Healthy**: Current attendance is excellent. Consider recognizing departments with 100% weekly check-in.")
        
    # 2. Ratio Check
    ratio = students_count / max(faculty_count, 1)
    if ratio > 30:
        insights.append(f"- ⚠️ **High Load**: Student-to-Faculty ratio is high ({ratio:.1f}:1). Open applications for adjunct professors in STEM departments.")
    else:
        insights.append(f"- ✅ **Balanced Classes**: Student-to-Faculty ratio is optimal ({ratio:.1f}:1) for personalized guidance.")
        
    # 3. Seasonal Library Insights
    insights.append("- 📚 **Resource Allocation**: High reservation rates for 'Database Systems' books. Release electronic licenses for student access.")
    
    return "\n\n".join(insights)
