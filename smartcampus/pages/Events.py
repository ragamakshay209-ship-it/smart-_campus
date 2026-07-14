import streamlit as st
import datetime
import pandas as pd
from utils.database import get_all_events, add_event, update_event, delete_event
from utils.helpers import load_custom_css, render_card

# Load styling
load_custom_css()

st.markdown("<h1>🎉 Campus Events Calendar</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B;'>Stay updated on academic panels, workshops, athletic meets, and cultural festivals.</p>", unsafe_allow_html=True)

# User Role Authorization
user_role = st.session_state.user.get("role") if st.session_state.user else "Student"
is_privileged = user_role in ["Admin", "Faculty"]

# Prepare Tabs
if is_privileged:
    tab_list = ["📅 Campus Calendar", "➕ Create Event", "✏️ Edit / Delete Events"]
else:
    tab_list = ["📅 Campus Calendar"]

tabs = st.tabs(tab_list)
events = get_all_events()

# ----------------------------------------------------
# TAB 1: CAMPUS CALENDAR
# ----------------------------------------------------
with tabs[0]:
    st.markdown("### Upcoming & Archive Events")
    
    if not events:
        st.info("No events scheduled on the campus roll.")
    else:
        # Filter controls
        col_cat, col_timeline = st.columns(2)
        with col_cat:
            cats = ["All Categories", "Academic", "Cultural", "Sports", "Workshop"]
            selected_cat = st.selectbox("Filter Category", cats)
        with col_timeline:
            timeline = st.selectbox("Time Horizon", ["All Events", "Upcoming", "Past Events"])
            
        filtered_events = events
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        
        # Category filter
        if selected_cat != "All Categories":
            filtered_events = [e for e in filtered_events if e.get("category") == selected_cat]
            
        # Timeline filter
        if timeline == "Upcoming":
            filtered_events = [e for e in filtered_events if e.get("date") >= today_str]
        elif timeline == "Past Events":
            filtered_events = [e for e in filtered_events if e.get("date") < today_str]
            
        if not filtered_events:
            st.warning("No events found matching current criteria.")
        else:
            # Sort events by date
            sorted_events = sorted(filtered_events, key=lambda x: x.get("date"))
            
            # Display list of events
            for ev in sorted_events:
                is_upcoming = ev.get("date") >= today_str
                badge_color = "#10B981" if is_upcoming else "#64748B"
                badge_text = "UPCOMING" if is_upcoming else "PAST"
                
                # Category badges
                cat_colors = {"Academic": "#2563EB", "Cultural": "#EC4899", "Sports": "#F59E0B", "Workshop": "#8B5CF6"}
                cat_color = cat_colors.get(ev.get("category"), "#64748B")
                
                date_parsed = datetime.datetime.strptime(ev.get("date"), "%Y-%m-%d").strftime("%B %d, %Y")
                
                # Card HTML structure
                card_html = f"""
                <div style="margin-bottom: 8px; display: flex; flex-wrap: wrap; gap: 8px;">
                    <span style="font-size:0.75rem; font-weight:700; color:{cat_color}; background:{cat_color}15; padding: 3px 8px; border-radius:4px;">{ev.get('category').upper()}</span>
                    <span style="font-size:0.75rem; font-weight:700; color:{badge_color}; background:{badge_color}15; padding: 3px 8px; border-radius:4px;">{badge_text}</span>
                </div>
                <p style="margin: 4px 0; font-size:0.95rem; color:#475569;">
                    📅 <b>{date_parsed}</b> &nbsp;&bull;&nbsp; ⏰ <b>{ev.get('time')}</b> &nbsp;&bull;&nbsp; 📍 <b>{ev.get('location')}</b>
                </p>
                <p style="margin-top: 12px; margin-bottom: 0; line-height: 1.5; color:#1E293B;">{ev.get('description')}</p>
                """
                render_card(f"🎉 {ev.get('title')}", card_html, color=cat_color)

# ----------------------------------------------------
# TAB 2: CREATE EVENT (PRIVILEGED ONLY)
# ----------------------------------------------------
if is_privileged:
    with tabs[1]:
        st.markdown("### Create New Campus Event")
        
        # Calculate Next ID
        if events:
            ids = [int(e.get("id")[2:]) for e in events if e.get("id").startswith("EV") and e.get("id")[2:].isdigit()]
            next_id = f"EV{max(ids) + 1:03d}" if ids else "EV001"
        else:
            next_id = "EV001"
            
        with st.form("create_event_form"):
            col_evid, col_evtitle = st.columns([1, 3])
            with col_evid:
                st.text_input("Event ID", value=next_id, disabled=True)
            with col_evtitle:
                title = st.text_input("Event Title", placeholder="Smart Campus Hackathon")
                
            description = st.text_area("Event Description", placeholder="Write event details, schedules, and guest speakers...")
            
            col_evdate, col_evtime = st.columns(2)
            with col_evdate:
                date = st.date_input("Event Date", value=datetime.date.today())
            with col_evtime:
                time = st.time_input("Event Time", value=datetime.time(9, 0))
                
            col_evloc, col_evcat = st.columns(2)
            with col_evloc:
                location = st.text_input("Location / Venue", placeholder="Seminar Hall A, Auditorium")
            with col_evcat:
                category = st.selectbox("Category", ["Academic", "Cultural", "Sports", "Workshop"])
                
            submit_create_ev = st.form_submit_button("Publish Event")
            
            if submit_create_ev:
                if not title.strip() or not description.strip() or not location.strip():
                    st.error("Please fill in Title, Description, and Location fields.")
                else:
                    new_ev = {
                        "id": next_id,
                        "title": title.strip(),
                        "description": description.strip(),
                        "date": date.strftime("%Y-%m-%d"),
                        "time": time.strftime("%H:%M"),
                        "location": location.strip(),
                        "category": category
                    }
                    if add_event(new_ev):
                        st.success(f"Event published successfully with ID: {next_id}.")
                        st.rerun()
                    else:
                        st.error("Error writing changes. Try again.")

# ----------------------------------------------------
# TAB 3: EDIT / DELETE EVENTS (PRIVILEGED ONLY)
# ----------------------------------------------------
if is_privileged:
    with tabs[2]:
        st.markdown("### Update / Cancel Published Events")
        
        if not events:
            st.info("No events registered.")
        else:
            selected_edit_ev = st.selectbox("Select Event to Modify:", [f"{e.get('id')} - {e.get('title')}" for e in events])
            
            target_id = selected_edit_ev.split(" - ")[0]
            event_to_edit = next(e for e in events if e.get("id") == target_id)
            
            if event_to_edit:
                with st.form("edit_event_form"):
                    e_title = st.text_input("Event Title", value=event_to_edit.get("title"))
                    e_description = st.text_area("Event Description", value=event_to_edit.get("description"))
                    
                    col_edate, col_etime = st.columns(2)
                    with col_edate:
                        ev_d = datetime.datetime.strptime(event_to_edit.get("date"), "%Y-%m-%d").date()
                        e_date = st.date_input("Event Date", value=ev_d)
                    with col_etime:
                        ev_t = datetime.datetime.strptime(event_to_edit.get("time"), "%H:%M").time()
                        e_time = st.time_input("Event Time", value=ev_t)
                        
                    col_eloc, col_ecat = st.columns(2)
                    with col_eloc:
                        e_location = st.text_input("Location / Venue", value=event_to_edit.get("location"))
                    with col_ecat:
                        cat_list = ["Academic", "Cultural", "Sports", "Workshop"]
                        cat_idx = cat_list.index(event_to_edit.get("category")) if event_to_edit.get("category") in cat_list else 0
                        e_category = st.selectbox("Category", cat_list, index=cat_idx)
                        
                    submit_edit_ev = st.form_submit_button("Update Event Details")
                    
                    if submit_edit_ev:
                        if not e_title.strip() or not e_description.strip() or not e_location.strip():
                            st.error("Please fill in Title, Description, and Location.")
                        else:
                            updated_fields = {
                                "title": e_title.strip(),
                                "description": e_description.strip(),
                                "date": e_date.strftime("%Y-%m-%d"),
                                "time": e_time.strftime("%H:%M"),
                                "location": e_location.strip(),
                                "category": e_category
                            }
                            if update_event(target_id, updated_fields):
                                st.success("Event details updated successfully.")
                                st.rerun()
                            else:
                                st.error("Database update error.")
                                
                st.markdown("---")
                st.markdown("#### ⚠️ Danger Zone")
                confirm_del = st.checkbox(f"Confirm that you want to delete event **{event_to_edit.get('title')}**.")
                delete_btn = st.button("🔴 Cancel / Delete Event")
                
                if delete_btn:
                    if confirm_del:
                        if delete_event(target_id):
                            st.success(f"Event {event_to_edit.get('title')} has been removed.")
                            st.rerun()
                        else:
                            st.error("Failed to delete.")
                    else:
                        st.error("Please confirm check-box before deletion.")
