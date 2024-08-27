from tkinter import *
import customtkinter as ctk
from customtkinter import filedialog
from PIL import Image
import os
import func
import threading
import webbrowser
import db_ops
import sys
sys.path.insert(0, 'spaCy-training')
import resume_parser, advice, reformat

cv = None
jobdesc = None
settings = None
devdir = None
dev_mode_value = 0
cog = ctk.CTkImage(dark_image=Image.open(r'assets/cog.png'), size=(50, 50))

def cv_upload(): # Upload CVs, only file types accepted are text & pdf files
    global cv, cvtext
    cwd = os.getcwd()
    cv = filedialog.askopenfilename(initialdir=cwd, title='Select a File', filetypes=(('pdf files','*.pdf'),('text files','*.txt')))
    if cv:
        filename = os.path.basename(cv)
        cvtext.configure(text=f'{filename}') 

def job_upload(): # Upload job description, only file types accepted are text & pdf files
    global jobdesc, jdesctext
    cwd = os.getcwd()
    jobdesc = filedialog.askopenfilename(initialdir=cwd, title='Select a File', filetypes=(('pdf files','*.pdf'),('text files','*.txt')))
    if jobdesc:
        filename = os.path.basename(jobdesc)
        jdesctext.configure(text=f'{filename}') 

def dev_upload(): # Select developer mode folder
    global devdir
    cwd = os.getcwd()
    devdir = filedialog.askdirectory(initialdir=cwd, title='Select a Folder')
    
def change_appearance(new_appearance): # Change CustomTkinter appearance mode
    ctk.set_appearance_mode(new_appearance)

def set_theme(new_theme): # Change CustomTkinter theme
    ctk.set_default_color_theme(new_theme)  

def loadingscreen(): # Make use of threading to run functions in a separate thread, prevents the CustomTkinter GUI window from freezing while results are being calculated
    prepare_loading_screen()
    threading.Thread(target=run_func_main, daemon=True).start()

def return_to_home(): # Returns to the home screen frame, changes the values of CV and Jobdesc to None, so that the program flow is as if the window has been freshly opened.
    global devdir, cv, jobdesc
    if devdir != None:
        db_ops.database(cv, jobdesc, devdir) # If there is a folder for developer mode, data is saved as CSV files in the directory
    cv = None
    jobdesc = None
    for widget in window.winfo_children(): # Deletes all widgets in the screen
        widget.destroy()
    home_screen(window).pack(expand=True, fill='both')

def sidebar_button_event(main_frame, results, description, i):
    
    def compute_advices(): # Get advice on CV & job description
        advices_text = advice.advice(cv, description.iloc[-(i+1)])
        main_frame.after(0, update_cc_comments, advices_text)
    
    def update_cc_comments(advices_text): # Update the comment window based on Career Confidence's advice
        cc_comments.insert("0.0", advices_text)
        cc_comments.configure(state="disabled")

    for widget in main_frame.winfo_children(): # Deletes all widgets in the screen
        widget.destroy()

    job_title_label = ctk.CTkLabel(main_frame, text=f'Job Title: {results.iloc[-(i+1)]["title"]}', font=('Roboto', 35, 'bold'), anchor='w')  
    job_title_label.pack(pady=(20, 10), fill='x', padx=20)

    listed_on_label = ctk.CTkLabel(main_frame, text=f'Listed on: {results.iloc[-(i+1)]["date_posted"]}', font=('Roboto', 20), anchor='w')
    listed_on_label.pack(fill='x', padx=20)
    

    job_description_label = ctk.CTkLabel(main_frame, text='Job description: ', font=('Roboto', 20), anchor='w')
    job_description_label.pack(pady=(20, 10), fill='x', padx=20)
    desc = ctk.CTkTextbox(main_frame, width=150, height=150)
    desc.pack(fill='x', padx=20)
    desc.insert("0.0", f"{description.iloc[-(i+1)]}")
    desc.configure(state="disabled")

    cc_comments_label = ctk.CTkLabel(main_frame, text='CC Comments:', font=('Roboto', 20), anchor='w')
    cc_comments_label.pack(pady=(20, 10), fill='x', padx=20)

    cc_comments = ctk.CTkTextbox(main_frame, width=150, height=150)
    cc_comments.pack(fill='x', padx=20)
    cc_comments.insert('0.0','Loading...')
    cc_comments.configure(state="normal")

    apply_button = ctk.CTkButton(main_frame, text='Apply here', command=lambda: webbrowser.open_new_tab(f'{results.iloc[-(i+1)]["job_url"]}')) # Uses the webbrowser function to open the link using the default browser
    apply_button.pack(pady=(20, 10), padx=20)

    apply_button = ctk.CTkButton(main_frame, text='Return to Home', command=return_to_home)
    apply_button.pack(pady=(20, 10), padx=20)

    advice_thread = threading.Thread(target=compute_advices) # Executes the advice function in a separate thread to prevent the GUI window from freezing
    advice_thread.start()


def create_results_sidebar(parent, main_frame):
    for widget in main_frame.winfo_children(): # Deletes all widgets in the screen
        widget.destroy()

    sidebar_frame = ctk.CTkFrame(parent, width=140, corner_radius=0)
    sidebar_frame.grid(row=0, column=0, rowspan=10, sticky='nsew')
    sidebar_frame.grid_rowconfigure(10, weight=1)
    
    job_trends = ctk.CTkLabel(sidebar_frame, text='JOB TRENDS', font=('Roboto', 20, 'bold'))
    job_trends.grid(row=0, column=0, padx=20, pady=(20, 10))

    job_trends_amt = ctk.CTkLabel(sidebar_frame, text='5 jobs found!', font=('Roboto', 15))
    job_trends_amt.grid(row=1, column=0, padx=20, pady=(20, 10))

    for i in range(5): # Loop to create multiple side buttons, allowing the user to select a job.
        ctk.CTkButton(sidebar_frame, text=f'Job {i+1}', command=lambda mf=main_frame, res=searchresults, desc=searchdescription, idx=i: sidebar_button_event(mf, res, desc, idx)).grid(row=2+i, column=0, padx=20, pady=10)

    return sidebar_frame

def create_sidebar(parent):
    sidebar_frame = ctk.CTkFrame(parent, width=140, corner_radius=0)
    sidebar_frame.grid(row=0, column=0, sticky="ns")
    parent.grid_columnconfigure(0, minsize=140)

    results = ctk.CTkLabel(sidebar_frame, text=f"{name} - {result}%", font=ctk.CTkFont(size=20, weight='bold'))
    results.grid(row=0, column=0, padx=20, pady=(20, 10))

    score1 = ctk.CTkLabel(sidebar_frame, text=f"ANALYSIS", font=ctk.CTkFont(size=15))
    score1.grid(row=2, column=0, padx=20, pady=(20, 10))
    progress_bar_1 = ctk.CTkProgressBar(sidebar_frame, width=150, mode='determinate', determinate_speed=0)
    progress_bar_1.set(result/100)
    progress_bar_1.grid(row=3, column=0, padx=20, pady=10)

    score2 = ctk.CTkLabel(sidebar_frame, text=f"KEYWORDS", font=ctk.CTkFont(size=15))
    score2.grid(row=5, column=0, padx=20, pady=(20, 10))
    progress_bar_2 = ctk.CTkProgressBar(sidebar_frame, width=150, mode='determinate', determinate_speed=0)
    progress_bar_2.set(keywords/100)
    progress_bar_2.grid(row=6, column=0, padx=20, pady=10)

    score3 = ctk.CTkLabel(sidebar_frame, text=f"FORMATTING", font=ctk.CTkFont(size=15)) 
    score3.grid(row=8, column=0, padx=20, pady=(20, 10))
    progress_bar_3 = ctk.CTkProgressBar(sidebar_frame, width=150, mode='determinate', determinate_speed=0)
    progress_bar_3.set(similarity/100)
    progress_bar_3.grid(row=9, column=0, padx=20, pady=10)

    sidebar_frame.grid_rowconfigure(10, weight=1)


    return sidebar_frame

def create_results_frame(parent):
    results_frame = ctk.CTkFrame(parent)
    results_frame.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)
    parent.grid_columnconfigure(1, weight=1)
    parent.grid_rowconfigure(0, weight=1)

    please_select = ctk.CTkLabel(results_frame, text='PLEASE SELECT A JOB!', font=('Roboto', 20, 'bold'))
    please_select.pack(expand=True, fill='both')

    return results_frame


def prepare_loading_screen():
    global frame, progress, loading_text
    frame = ctk.CTkFrame(window, width=1400, height=720)
    frame.place(x=0, y=0)
    progress = ctk.CTkProgressBar(frame, orientation='horizontal', height=50, width=800, mode='indeterminate')
    loading_text = ctk.CTkLabel(frame, text='Calculating score...', font=('Aerial', 40))
    loading_text.place(x=550, y=200)
    progress.place(x=300, y=300)
    if window.winfo_exists():
        window.after(0,progress.start())

def advance(main_frame):
    for widget in main_frame.winfo_children():
        widget.destroy()
    mainframe2 = create_results_frame(window)
    create_results_sidebar(window, mainframe2)

def create_main_frame(parent):
    global searchresults, searchdescription, cv_advice, rkeywords, reformatted_cv, name, keywords, similarity
    main_frame = ctk.CTkFrame(parent)
    main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
    parent.grid_columnconfigure(1, weight=1)
    parent.grid_rowconfigure(0, weight=1) 
    keywords = float(keywords)
    similarity = float(similarity) 

    analysis_label = ctk.CTkLabel(main_frame, text=f"Analysis - {result}%", font=ctk.CTkFont(size=15))
    analysis_label.pack(pady=(20, 10), fill='x', padx=20, side='top', anchor='w')
    analysis_text = ctk.CTkTextbox(main_frame, width=700, height=130)
    analysis_text.pack(fill='x', padx=20)
    analysis_text.insert('0.0', f'{cv_advice}')
    analysis_text.configure(state="disabled")
    
    keywords_label = ctk.CTkLabel(main_frame, text=f"Keywords - {keywords}%", font=ctk.CTkFont(size=15))
    keywords_label.pack(pady=(20, 10), fill='x', padx=20, side='top', anchor='w')
    keywords_text = ctk.CTkTextbox(main_frame, width=700, height=130)
    keywords_text.pack(fill='x', padx=20)
    keywords_text.insert('0.0', f'{rkeywords}')
    keywords_text.configure(state="disabled")

    formatting_label = ctk.CTkLabel(main_frame, text=f"Formatting - {similarity}%", font=ctk.CTkFont(size=15))
    formatting_label.pack(pady=(20, 10), fill='x', padx=20, side='top', anchor='w')
    formatting_text = ctk.CTkTextbox(main_frame, width=700, height=130)
    formatting_text.pack(fill='x', padx=20)
    formatting_text.insert('0.0', f'{reformatted_cv}')
    formatting_text.configure(state="disabled")

    continue_button = ctk.CTkButton(main_frame,width=100,height=40,text='Continue', command=lambda: advance(parent))
    continue_button.pack(pady=(20, 10), padx=20)

    return main_frame  
    
def run_func_main():
    global searchresults, searchdescription, cv_advice, rkeywords, reformatted_cv, result, name, keywords, similarity
    city, country, role = func.job_search_params(jobdesc)
    searchresults, searchdescription = func.jobs(city, country, role)
    cv_advice = advice.advice(cv,jobdesc)
    rkeywords = resume_parser.parser(cv)["skills"]
    reformatted_cv = reformat.reformat(cv,jobdesc)
    result, name, keywords, similarity = func.main(jobdesc, cv)
    window.after(0, complete_processing)

def complete_processing():
    if window.winfo_exists():
        progress.configure(mode='determinate')
        progress.set(1)
        progress.stop()
        loading_text.configure(text='Calculations complete!')
        window.after(0, clear_screen_and_continue)

def clear_screen_and_continue():
    for widget in window.winfo_children():
        widget.destroy()
    mainframe = create_main_frame(window)
    create_sidebar(window)
    
def submit():
    global cv, jobdesc
    if cv == None or jobdesc == None:
        error_window()
    elif devdir == None and dev_mode_value == 1:
        dev_error_window()
    else:
        for widget in window.winfo_children():
            widget.destroy()
        loadingscreen()

def error_window():
    error = ctk.CTkToplevel(window)
    error.title('Error')
    error.geometry('550x150')
    error.resizable(0,0)
    error.after(200, error.lift)
    error.attributes('-topmost',True)

    error_label = ctk.CTkLabel(error, text='Error: Please upload both a CV and a job description before proceeding.', anchor='w',font=('Aerial',13))
    error_label.place(x=50, y=20)

def dev_error_window():
    dev_error = ctk.CTkToplevel(window)
    dev_error.title('Error')
    dev_error.geometry('550x150')
    dev_error.resizable(0,0)
    dev_error.after(200, dev_error.lift)
    dev_error.attributes('-topmost',True)

    dev_error_label = ctk.CTkLabel(dev_error, text='Error: Please upload a developer mode file directory before proceeding.', anchor='w',font=('Aerial',13))
    dev_error_label.place(x=50, y=20)


def settings_window():
    global settings
    global devdir
    global dev_mode_value
    settings = ctk.CTkToplevel(window)
    settings.title('Settings')
    settings.geometry('300x400')
    settings.resizable(0,0)
    settings.after(200, settings.lift)
    settings.attributes('-topmost',True)

    def dev_callback():
        if dev_mode.get() == 1:
            devmode_dir.place(x=50, y=220)
        else:
            devmode_dir.place_forget()

    appearance = ctk.CTkLabel(settings, text='Appearance Mode:', anchor='w')
    appearance_menu = ctk.CTkOptionMenu(settings, values=['Light','Dark','System'], command=change_appearance)
    theme = ctk.CTkLabel(settings, text='Color Theme:', anchor='w')
    theme_menu = ctk.CTkOptionMenu(settings, values=['blue','dark-blue','green'], command=set_theme)
    default_check = ctk.StringVar(value='off')
    dev_mode = ctk.CTkCheckBox(settings, text='Developer Mode', variable=default_check, onvalue=1, offvalue=2,command=dev_callback)
    devmode_dir = ctk.CTkButton(settings, width=40, height=20, text='File Directory', command=dev_upload)


    appearance.place(x=50, y=50)
    appearance_menu.place(x=50, y=80)
    theme.place(x=50, y=110)
    theme_menu.place(x=50, y=140)
    dev_mode.place(x=50, y=190)


def settings_callback():
    if (settings != None) and settings.winfo_exists():
        pass
    else:
        settings_window()


def home_screen(parent):
    global cvtext, jdesctext
    home_frame = ctk.CTkFrame(parent, width=1400, height=720)
    cvbutton = ctk.CTkButton(home_frame, width=180, height=42, text='Upload', command=cv_upload)
    cvbutton.place(x=300, y=175)
    jdescbutton = ctk.CTkButton(home_frame, width=180, height=42, text='Upload', command=job_upload)
    jdescbutton.place(x=920, y=175)
    settingsbutton = ctk.CTkButton(home_frame, image=cog, text='', fg_color='transparent', hover=False, command=settings_callback)
    settingsbutton.place(x=1225, y=50)
    submitb = ctk.CTkButton(home_frame, width=270, height=63, text='Submit',command=submit)
    submitb.place(x=565, y=550)
    cvtext = ctk.CTkLabel(home_frame, text='Upload your CV', width=400, justify='left', anchor='w', font=('Aerial',20))
    cvtext.place(x=320, y=120)
    jdesctext = ctk.CTkLabel(home_frame, text='Upload the job description', width=400, justify='left', anchor='w', font=('Aerial',20))
    jdesctext.place(x=895, y=120)

    return home_frame

def main_screen():
    global window
    window = ctk.CTk()
    window.title('Career Confidence')
    window.geometry('1400x720')
    window.resizable(0,0)
    window.after(201, lambda:window.iconbitmap(r'assets/logo.ico'))
    home_screen(window).pack(expand=True, fill='both')
    window.mainloop()


main_screen()