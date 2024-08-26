from tkinter import *
from PIL import Image, ImageTk
import pathlib
import tkinter.messagebox
import sqlite3
import re
import hashlib
import random
import asyncio
import os


# --- Global Settings ---
# Set main program directory
main_directory = os.path.join(os.getcwd(), r'OneDrive\Documents\TWGSB\Year 12\Computer Science\Computer Science NEA\NEA Program Files')
db_path = os.path.join(main_directory, 'Users.db')

# --- Shared Functions ---

# Sample Data for Autofill
sample_names = ['Alice', 'Bob', 'Charlie', 'Honey_Badger562']

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to validate the email format
def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$", email) is not None

# Validation Function
def validate_inputs(name1, email1, username1, password1):
    if not all([name1, email1, username1, password1]):
        return "All fields are required."
    if not is_valid_email(email1):
        return "Invalid email address."
    if len(password1) < 8 or not re.search(r"\d", password1) or ' ' in password1:
        return "Password must be at least 8 characters, contain a number and not contain spaces."
    if ' ' in username1:
        return "Username cannot contain spaces."
    return None

# Function to store user data in the database
async def store_user_async(name1, email1, username1, password1):
    await asyncio.sleep(1)  # Simulate a delay
    # Construct the path to the database file
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create the 'users' table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            name TEXT,
            email TEXT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    try:
        cursor.execute(
            "INSERT INTO users (name, email, username, password) VALUES (?, ?, ?, ?)",
            (name1, email1, username1, password1))
        conn.commit()  # Commit the changes to the database
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False
    except Exception as e:
        conn.close()
        return False

# Function to clear input fields
def clear_fields():
    name.set('')
    email.set('')
    username.set('')
    password.set('')

# Function to handle form submission
def submit_data():
    name1, email1, username1, password1 = name.get(), email.get(
    ), username.get(), password.get()
    error_message = validate_inputs(name1, email1, username1, password1)
    if error_message:
        tkinter.messagebox.showerror("Error", error_message)
        return
    try:
        success = asyncio.run(
            store_user_async(name1, (email1).lower(), (username1).lower(),
                             hash_password(password1)))
        if success:
            tkinter.messagebox.showinfo('Success!', 'Signup successful!')
            clear_fields()
        else:
            tkinter.messagebox.showerror("Error",
                                         "This username is already taken.")
    except Exception as e:
        tkinter.messagebox.showerror("Error", f"Unexpected error: {e}")

# Helper function to create labels and entries
def create_label(root, text, y_pos):
    label = Label(root, text=text, font=('Arial', 12), bg='#ffffff')
    label.place(x=80, y=y_pos)
    return label

def create_entry(root, var, y_pos, is_password=False):
    entry = Entry(root, textvariable=var, width=30)
    if is_password:
        entry.config(show='*')
    entry.place(x=250, y=y_pos)
    return entry

# Function to autofill sample data
def autofill_sample_data():
    name.set(random.choice(sample_names))
    email.set(f"{name.get().lower()}@example.com")
    username.set(f"{name.get().lower()}123")
    password.set('password123')

# Function to show password strength
def on_password_entry(event):
    strength_label['text'] = "Strength: " + ("Strong" if len(password.get()) >= 8 else "Weak")

# --- Signup Page ---
def open_signup_window(root): 
    signup_window = Toplevel(root)
    signup_window.geometry('500x450+710+250')
    signup_window.title('Signup')
    signup_window.config(bg='#aaaaaa')
    #Signup Heading
    heading = Label(signup_window,
                    text='Signup',
                    font=('Helvetica', 20, 'bold'),
                    fg='#403737',
                    bg='#ffffff')
    heading.pack(pady=20)
    
    #Full Name
    name_label = create_label(signup_window, 'Full Name:', 70)
    name_entry = create_entry(signup_window, name, 71.5)

    #Email
    email_label = create_label(signup_window, 'Email:', 120)
    email_entry = create_entry(signup_window, email, 121.5)

    #Username
    username_label = create_label(signup_window, 'Username:', 170)
    username_entry = create_entry(signup_window, username, 171.5)

    #Password
    password_label = create_label(signup_window, 'Password:', 220)
    password_entry = create_entry(signup_window, password, 221.5, is_password=True)
    password_entry.bind('<KeyRelease>', on_password_entry)

    global strength_label # Declare strength_label as global
    strength_label = Label(signup_window,
                           text='Strength: ',
                           font=('Arial', 10),
                           bg='#ffffff')
    strength_label.place(x=250, y=250)

    # Autofill Button
    autofill_button = Button(signup_window,
                             text='Autofill',
                             width=12,
                             bg='#777777',
                             fg='white',
                             command=autofill_sample_data)
    autofill_button.place(x=80, y=300)

    # Submit Button
    submit_button = Button(signup_window,
                           text='Submit',
                           width=12,
                           bg='#555555',
                           fg='white',
                           command=submit_data)
    submit_button.place(x=340, y=300)

    # Button to go to login page 
    login_button = Button(signup_window,
                          text='Login Page',
                          width=10,
                          bg='#555555',
                          fg='white',
                          command=lambda:[open_login_window(), clear_fields(), signup_window.destroy()])
    login_button.place(x=20, y=400)

    # Button to exit
    exit_button = Button(signup_window,
                          text='Exit',
                          width=10,
                          bg='#555555',
                          fg='white',
                          command=lambda: exit())
    exit_button.place(x=400, y=400) 


# --- Login Page ---

def open_login_window():
    login_window = Toplevel(root)
    login_window.geometry('500x300+710+250')
    login_window.title('Login')
    login_window.config(bg='#aaaaaa')

    # Variables for login fields
    login_username = StringVar()
    login_password = StringVar()

    async def login_submit():
        try:
            # Get values from login fields
            username1 = login_username.get()
            password1 = hash_password(login_password.get())  # Hash the password before checking

            # Simulate a delay and connect to the database
            await asyncio.sleep(1)
            # Construct the path to the database file
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if username and password exist in the database
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username1.lower(), password1))
            user = cursor.fetchone()

            if user:
                tkinter.messagebox.showinfo('Success!', 'Login successful!')
                login_window.destroy()
                open_menu_window()
                
            else:
                tkinter.messagebox.showerror('Error', 'Invalid username or password.')

            conn.close()

        except Exception as e:
            tkinter.messagebox.showerror("Error", f"An error occurred: {e}")

    # Login Heading
    login_heading = Label(login_window,
                          text='Login',
                          font=('Helvetica', 20, 'bold'),
                          fg='#403737',
                          bg='#ffffff')
    login_heading.pack(pady=20)

    username_label = create_label(login_window, 'Username:', 72.5)
    username_entry = create_entry(login_window, login_username, 74)

    password_label = create_label(login_window, 'Password:', 122.5)
    password_entry = create_entry(login_window, login_password, 124, is_password=True)

    # Login Button
    login_button = Button(login_window,
                          text='Login',
                          width=10,
                          bg='#555555',
                          fg='white',
                          command=lambda: asyncio.run(login_submit()))
    login_button.place(x=354, y=180)

    # Button to go to signup page
    signup_button = Button(login_window,
                          text='Signup Page',
                          width=10,
                          bg='#555555',
                          fg='white',
                          command=lambda:[open_signup_window(root), login_window.destroy()])
    signup_button.place(x=20, y=250) 

    # Button to exit
    exit_button = Button(login_window,
                          text='Exit',
                          width=10,
                          bg='#555555',
                          fg='white',
                          command=lambda: exit())
    exit_button.place(x=400, y=250) 

# --- Main Menu ---

def open_menu_window():
    menu_window = Toplevel(root)
    menu_window.geometry('1000x1000+460+23')
    menu_window.title('Main Menu')
    menu_window.config(bg='#aaaaaa')
    
    # Menu Heading
    menu_heading = Label(menu_window,
                          text='Main Menu',
                          font=('Helvetica', 20, 'bold'),
                          fg='#403737',
                          bg='#ffffff')
    menu_heading.pack(pady=20)

    # Icons for Main Menu
    
    # Chart Icon
    try:
        chart_icon_image = PhotoImage(file=os.path.join(main_directory, 'chart.png'))
        chart_button = Button(menu_window, image=chart_icon_image, command='', borderwidth=3)
        chart_button.pack(pady=20)
        chart_button.place(x=75,y=75)
        menu_window.chart_icon_image = chart_icon_image  # Prevent image from being garbage collected
    except Exception as e:
        tkinter.messagebox.showerror("Error", f"Failed to load chart icon: {e}")

    # Indicators Icon
    try:
        indicators_icon_image = PhotoImage(file=os.path.join(main_directory, 'indicators.png'))
        indicators_button = Button(menu_window, image=indicators_icon_image, command='', borderwidth=3)
        indicators_button.pack(pady=20)
        indicators_button.place(x=525,y=75)
        menu_window.indicators_icon_image = indicators_icon_image  # Prevent image from being garbage collected
    except Exception as e:
        tkinter.messagebox.showerror("Error", f"Failed to load indicators icon: {e}")

    # AI Chatbot Icon
    try:
        aichatbot_icon_image = PhotoImage(file=os.path.join(main_directory, 'aichatbot.png'))
        aichatbot_button = Button(menu_window, image=aichatbot_icon_image, command='', borderwidth=3)
        aichatbot_button.pack(pady=20)
        aichatbot_button.place(x=75,y=525)
        menu_window.aichatbot_icon_image = aichatbot_icon_image  # Prevent image from being garbage collected
    except Exception as e:
        tkinter.messagebox.showerror("Error", f"Failed to load aichatbot icon: {e}")

    # Settings Icon
    try:
        settings_icon_image = PhotoImage(file=os.path.join(main_directory, 'settings.png'))
        settings_button = Button(menu_window, image=settings_icon_image, command='', borderwidth=3)
        settings_button.pack(pady=20)
        settings_button.place(x=525,y=525)
        menu_window.settings_icon_image = settings_icon_image  # Prevent image from being garbage collected
    except Exception as e:
        tkinter.messagebox.showerror("Error", f"Failed to load settings icon: {e}")

    # Button to go to login
    login_button = Button(menu_window,
                          text='Back',
                          width=10,
                          bg='#555555',
                          fg='white',
                          command=lambda: [open_login_window(), menu_window.destroy()])
    login_button.place(x=900, y=950) 

# --- Main Window ---

root = Tk()
root.geometry('0x0')
root.geometry('+10000+10000')
root.title("Don't Click")

name = StringVar()
email = StringVar()
username = StringVar()
password = StringVar()

open_login_window()

root.mainloop()
