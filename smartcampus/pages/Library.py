import streamlit as st
import datetime
import pandas as pd
from utils.database import get_all_books, get_all_students, add_book, update_book, delete_book
from utils.helpers import load_custom_css, render_card, render_metric_card

# Load styling
load_custom_css()

st.markdown("<h1>📚 Library Management</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B;'>Manage catalog inventory, check-out books to students, and track active return timelines.</p>", unsafe_allow_html=True)

# User Role Authorization
user_role = st.session_state.user.get("role") if st.session_state.user else "Student"
is_privileged = user_role in ["Admin", "Faculty"]

# Define Tabs
if is_privileged:
    tab_list = ["📖 Book Catalog", "🔄 Issue / Return Books", "➕ Manage Inventory"]
else:
    tab_list = ["📖 Book Catalog", "🔄 My Checked Out Books"]

tabs = st.tabs(tab_list)

books = get_all_books()
students = get_all_students()

# ----------------------------------------------------
# TAB 1: BOOK CATALOG
# ----------------------------------------------------
with tabs[0]:
    st.markdown("### Campus Book Catalog")
    
    if not books:
        st.info("No books in the library catalog yet.")
    else:
        # Search catalog
        search_query = st.text_input("Search Book Catalog", placeholder="Type Title, Author, or ISBN...")
        
        filtered_books = books
        if search_query.strip():
            q = search_query.lower().strip()
            filtered_books = [
                b for b in filtered_books
                if q in b.get("title").lower() or q in b.get("author").lower() or q in b.get("isbn").lower()
            ]
            
        if not filtered_books:
            st.warning("No books matched your query.")
        else:
            # Display catalog
            df_books = pd.DataFrame(filtered_books)
            df_display = df_books[["id", "title", "author", "isbn", "quantity", "available"]].copy()
            df_display.columns = ["Book ID", "Title", "Author", "ISBN", "Total Copies", "Available Copies"]
            st.dataframe(df_display, hide_index=True, use_container_width=True)
            
            # Detailed visual cards
            st.markdown("#### Detail Book View & Availability")
            selected_book_id = st.selectbox("Select a book to inspect details:", [b.get("id") for b in filtered_books])
            
            b_info = next(b for b in filtered_books if b.get("id") == selected_book_id)
            if b_info:
                col_c1, col_c2 = st.columns([2, 1])
                with col_c1:
                    status_badge = "<span style='color:#10B981; font-weight:600;'>In Stock</span>" if b_info.get("available") > 0 else "<span style='color:#EF4444; font-weight:600;'>Out of Stock</span>"
                    details_html = f"""
                    <table style="width: 100%; font-size: 0.95rem;">
                        <tr><td style="font-weight: 600; width: 30%; color: #64748B;">Book ID:</td><td style="color:#1E293B; font-weight:700;">{b_info.get('id')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Title:</td><td style="color:#1E293B; font-weight:600;">{b_info.get('title')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Author:</td><td style="color:#1E293B;">{b_info.get('author')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">ISBN:</td><td style="color:#1E293B;">{b_info.get('isbn')}</td></tr>
                        <tr><td style="font-weight: 600; color: #64748B;">Status:</td><td>{status_badge}</td></tr>
                    </table>
                    """
                    render_card(f"{b_info.get('title')}", details_html)
                with col_c2:
                    st.markdown(
                        f"""
                        <div style="text-align: center; background-color:#FFFFFF; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; height: 100%;">
                            <span style="font-size: 0.8rem; color:#64748B; font-weight:600; text-transform:uppercase;">Availability</span>
                            <h2 style="font-size: 3.5rem; margin: 10px 0; color:#2563EB; font-weight:700;">{b_info.get('available')}<span style='font-size:1.5rem; color:#94A3B8;'>/{b_info.get('quantity')}</span></h2>
                            <p style="font-size:0.85rem; color:#64748B; margin:0;">Copies currently available for issue.</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Active issues lists
                st.markdown("##### Current Borrowers")
                active_issues = b_info.get("issued_to", [])
                if not active_issues:
                    st.markdown("<p style='color:#64748B; font-style:italic;'>No active issues for this book.</p>", unsafe_allow_html=True)
                else:
                    df_issues = pd.DataFrame(active_issues)
                    df_iss_disp = df_issues[["student_id", "student_name", "issue_date", "due_date"]].copy()
                    df_iss_disp.columns = ["Borrower ID", "Borrower Name", "Issue Date", "Due Date"]
                    st.dataframe(df_iss_disp, hide_index=True, use_container_width=True)

# ----------------------------------------------------
# TAB 2 (PRIVILEGED): ISSUE / RETURN BOOKS
# ----------------------------------------------------
if is_privileged:
    with tabs[1]:
        st.markdown("### Issue and Return Operations")
        
        op_type = st.radio("Choose Action:", ["Issue Book", "Return Book"], horizontal=True)
        
        if op_type == "Issue Book":
            st.markdown("#### Issue Book to Student")
            
            # Filter books with available copies > 0
            available_books = [b for b in books if b.get("available", 0) > 0]
            
            if not available_books:
                st.warning("No books in catalog are currently available for checkout.")
            elif not students:
                st.warning("No students registered in database. Enroll students first.")
            else:
                with st.form("issue_book_form"):
                    selected_iss_book = st.selectbox(
                        "Select Book to Issue:", 
                        [f"{b.get('id')} - {b.get('title')} (ISBN: {b.get('isbn')})" for b in available_books]
                    )
                    selected_iss_std = st.selectbox(
                        "Select Student:", 
                        [f"{s.get('id')} - {s.get('name')}" for s in students]
                    )
                    
                    col_idate, col_ddate = st.columns(2)
                    with col_idate:
                        issue_date = st.date_input("Issue Date", value=datetime.date.today())
                    with col_ddate:
                        due_date = st.date_input("Due Date", value=datetime.date.today() + datetime.timedelta(days=14))
                        
                    submit_issue = st.form_submit_button("Complete Checkout")
                    
                    if submit_issue:
                        book_id = selected_iss_book.split(" - ")[0]
                        std_id = selected_iss_std.split(" - ")[0]
                        std_name = selected_iss_std.split(" - ")[1]
                        
                        target_book = next(b for b in books if b.get("id") == book_id)
                        
                        # Verify student doesn't already have this book checked out
                        if any(issue.get("student_id") == std_id for issue in target_book.get("issued_to", [])):
                            st.error(f"Student already has an active issue of this book title.")
                        else:
                            # Modify stock & add borrower
                            target_book["available"] = target_book.get("available") - 1
                            if "issued_to" not in target_book:
                                target_book["issued_to"] = []
                            target_book["issued_to"].append({
                                "student_id": std_id,
                                "student_name": std_name,
                                "issue_date": issue_date.strftime("%Y-%m-%d"),
                                "due_date": due_date.strftime("%Y-%m-%d")
                            })
                            
                            if update_book(book_id, target_book):
                                st.success(f"Successfully checked out '{target_book.get('title')}' to {std_name}.")
                                st.rerun()
                            else:
                                st.error("Database write error.")
                                
        else:
            st.markdown("#### Log Book Return")
            # Filter books with active borrow logs
            issued_books = [b for b in books if len(b.get("issued_to", [])) > 0]
            
            if not issued_books:
                st.info("There are no active checkouts in the library system currently.")
            else:
                selected_ret_book = st.selectbox(
                    "Select Book Title to Return:",
                    [f"{b.get('id')} - {b.get('title')}" for b in issued_books]
                )
                
                b_id = selected_ret_book.split(" - ")[0]
                target_book = next(b for b in books if b.get("id") == b_id)
                
                # Select student that borrowed
                borrowers = target_book.get("issued_to", [])
                selected_borrower = st.selectbox(
                    "Select Student Returning Book:",
                    [f"{i.get('student_id')} - {i.get('student_name')}" for i in borrowers]
                )
                
                ret_student_id = selected_borrower.split(" - ")[0]
                
                submit_return = st.button("Confirm Return")
                
                if submit_return:
                    # Remove borrower and increment available stock
                    target_book["available"] = target_book.get("available") + 1
                    target_book["issued_to"] = [i for i in borrowers if i.get("student_id") != ret_student_id]
                    
                    if update_book(b_id, target_book):
                        st.success("Book returned successfully. Stock updated.")
                        st.rerun()
                    else:
                        st.error("Error writing database.")

# ----------------------------------------------------
# TAB 3 (PRIVILEGED): MANAGE INVENTORY
# ----------------------------------------------------
if is_privileged:
    with tabs[2]:
        st.markdown("### Manage Library Inventory Catalog")
        
        # Sub actions
        inv_action = st.radio("Inventory Action:", ["Add New Title", "Edit Stock / Details", "Remove Title"], horizontal=True)
        
        if inv_action == "Add New Title":
            st.markdown("#### Add Book to Catalog")
            
            # ID generation
            if books:
                ids = [int(b.get("id")[1:]) for b in books if b.get("id").startswith("B") and b.get("id")[1:].isdigit()]
                next_id = f"B{max(ids) + 1}" if ids else "B1001"
            else:
                next_id = "B1001"
                
            with st.form("add_book_form"):
                col_bid, col_btit = st.columns([1, 3])
                with col_bid:
                    st.text_input("Book ID", value=next_id, disabled=True)
                with col_btit:
                    title = st.text_input("Book Title", placeholder="The Pragmatic Programmer")
                    
                author = st.text_input("Author(s)", placeholder="Andrew Hunt, David Thomas")
                isbn = st.text_input("ISBN Code (13 or 10-digit)", placeholder="9780135957059")
                quantity = st.number_input("Total Stock Copies", min_value=1, max_value=100, value=3)
                
                submit_add_book = st.form_submit_button("Catalog Book")
                
                if submit_add_book:
                    if not title.strip() or not author.strip() or not isbn.strip():
                        st.error("Please fill in Title, Author, and ISBN.")
                    elif any(b.get("isbn") == isbn.strip() for b in books):
                        st.error("A book with this ISBN code already exists in catalog.")
                    else:
                        new_book = {
                            "id": next_id,
                            "title": title.strip(),
                            "author": author.strip(),
                            "isbn": isbn.strip(),
                            "quantity": int(quantity),
                            "available": int(quantity),
                            "issued_to": []
                        }
                        if add_book(new_book):
                            st.success(f"Book '{title}' added to database successfully.")
                            st.rerun()
                        else:
                            st.error("Database write error.")
                            
        elif inv_action == "Edit Stock / Details":
            st.markdown("#### Edit Book Stock Count")
            
            if not books:
                st.info("Catalog empty.")
            else:
                selected_edit_book = st.selectbox(
                    "Select Book Title to Edit:",
                    [f"{b.get('id')} - {b.get('title')}" for b in books]
                )
                
                b_id = selected_edit_book.split(" - ")[0]
                target_book = next(b for b in books if b.get("id") == b_id)
                
                if target_book:
                    with st.form("edit_book_form"):
                        e_title = st.text_input("Title", value=target_book.get("title"))
                        e_author = st.text_input("Author", value=target_book.get("author"))
                        e_isbn = st.text_input("ISBN", value=target_book.get("isbn"))
                        
                        # Ensure quantity cannot be smaller than copies currently checked out
                        currently_borrowed = target_book.get("quantity") - target_book.get("available")
                        e_quantity = st.number_input(
                            "Total Inventory Quantity", 
                            min_value=currently_borrowed, 
                            max_value=100, 
                            value=target_book.get("quantity")
                        )
                        
                        submit_edit_book = st.form_submit_button("Update Catalog Record")
                        
                        if submit_edit_book:
                            if not e_title.strip() or not e_author.strip() or not e_isbn.strip():
                                st.error("Please fill in all inputs.")
                            elif any(b.get("isbn") == e_isbn.strip() and b.get("id") != b_id for b in books):
                                st.error("ISBN conflicts with another catalog record.")
                            else:
                                updated_fields = {
                                    "title": e_title.strip(),
                                    "author": e_author.strip(),
                                    "isbn": e_isbn.strip(),
                                    "quantity": int(e_quantity),
                                    "available": int(e_quantity) - currently_borrowed
                                }
                                if update_book(b_id, updated_fields):
                                    st.success("Book catalog entry updated successfully.")
                                    st.rerun()
                                else:
                                    st.error("Error writing changes.")
                                    
        else:
            st.markdown("#### Delete Title from Catalog")
            
            if not books:
                st.info("Catalog empty.")
            else:
                selected_del_book = st.selectbox(
                    "Select Book Title to Delete:",
                    [f"{b.get('id')} - {b.get('title')}" for b in books]
                )
                
                b_id = selected_del_book.split(" - ")[0]
                target_book = next(b for b in books if b.get("id") == b_id)
                
                if target_book:
                    currently_borrowed = target_book.get("quantity") - target_book.get("available")
                    if currently_borrowed > 0:
                        st.error(f"Cannot delete catalog record. {currently_borrowed} copies of this book are currently checked out to students.")
                    else:
                        confirm_del = st.checkbox("Confirm that you want to delete this title permanently.")
                        delete_btn = st.button("Permanently Remove Title")
                        
                        if delete_btn:
                            if confirm_del:
                                if delete_book(b_id):
                                    st.success("Book deleted from database.")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete.")
                            else:
                                st.error("Please confirm deletion checklist.")

# ----------------------------------------------------
# STUDENT TAB: MY CHECKED OUT BOOKS
# ----------------------------------------------------
else:
    with tabs[1]:
        st.markdown("### My Active Borrow Logs")
        
        # Check student profile
        student = next((s for s in students if s.get("email").lower() == user_email.lower()), None)
        if not student:
            st.error("Profile match failure. Contact system admin.")
        else:
            student_id = student.get("id")
            
            # Find books borrowed by this student
            my_borrowed = []
            for b in books:
                for issue in b.get("issued_to", []):
                    if issue.get("student_id") == student_id:
                        my_borrowed.append({
                            "book_id": b.get("id"),
                            "title": b.get("title"),
                            "author": b.get("author"),
                            "isbn": b.get("isbn"),
                            "issue_date": issue.get("issue_date"),
                            "due_date": issue.get("due_date")
                        })
                        
            if not my_borrowed:
                st.info("You do not have any books checked out from the library currently.")
            else:
                df_my = pd.DataFrame(my_borrowed)
                df_my.columns = ["Book ID", "Title", "Author", "ISBN", "Check-out Date", "Due Date"]
                st.dataframe(df, hide_index=True, use_container_width=True)
                
                # Warn if overdue
                overdue_count = 0
                today = datetime.date.today()
                
                for b in my_borrowed:
                    due = datetime.datetime.strptime(b.get("due_date"), "%Y-%m-%d").date()
                    if due < today:
                        st.error(f"🚨 **Overdue Alert**: '{b.get('title')}' was due on {b.get('due_date')}. Please return it to the library desk.")
                        overdue_count += 1
                        
                if overdue_count == 0:
                    st.success("✅ All checked out books are within their active loan periods.")
