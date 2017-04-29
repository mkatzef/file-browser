""" A tool intended to provide the basic functions of a file browser across
    multiple platforms. (Specifically, this tool is intended to prevent the need
    to restart my computer whenever Finder stops responding and won't force
    close in El Capitan on unofficial hardware)
    Author: Marc Katzef
    Date: 6/12/2015
"""

import os
import sys
import shutil
import subprocess
from tkinter import *
from tkinter.ttk import *
from distutils.dir_util import copy_tree

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
SELECTION_KEY = 'Button-3'

class Maingui:
    def __init__(self, window):
        #title_label = Label(window, text='File Browser', font=('Arial', 18), anchor=CENTER)
        #title_label.grid(row=0, column=0, columnspan=2, sticky=W+E)      
    
        self.frame_a = Frame(window)
        self.frame_a.grid(row=1, column=0, rowspan=4)
        
        self.frame_b = Frame(window)
    
        self.frame_c = Frame(window)
    
        self.frame_d = Frame(window)
        
        frame_e = Frame(window)
        frame_e.grid(row=4, column=1, sticky=S)
        self.the_buttons(frame_e)
        
        a = Filebrowser(self.frame_a)
        Replacegui(self.frame_b, a)
        Emptier(self.frame_c, a)
        Movestuff(self.frame_d, a)
        
        self.active_frame = self.frame_c
        self.change_view('gen')


    def the_buttons(self, window):
        general_button = Button(window, text='General', command=lambda x='gen': self.change_view(x), width=10)
        general_button.grid(row=0, column=0, pady=10, padx=(5,0))
        
        name_button = Button(window, text='Filenames', command=lambda x='nam': self.change_view(x), width=10)
        name_button.grid(row=0, column=1)
        
        empty_button = Button(window, text='Subfolders', command=lambda x='emp': self.change_view(x), width=10)
        empty_button.grid(row=0, column=2, padx=(0,15))

        
    def change_view(self, which, *others):
        if which == 'gen':
            new_active_frame = self.frame_d
        elif which == 'nam':
            new_active_frame = self.frame_b
        elif which == 'emp':
            new_active_frame = self.frame_c

        self.active_frame.grid_forget()
        self.active_frame = new_active_frame
        self.active_frame.grid(row=1, column=1, rowspan=4, sticky=N+E+W+S)

        
        
class Filebrowser:
    """The window that lets you navigate the files on your device"""
    def __init__(self, window):
        """Identifies OS, Initialises variables, places a current directory
        label, a back button, and the listbox which displays the files and
        folders of the current directory. Then calls the function which updates
        the options within the listbox.
        """
        self.test_os()
        
        self.cur_dir_full = StringVar()
        self.cur_dir_last = StringVar()
        self.cur_dir_full.set(self.start_dir)
        self.cur_dir_last.set('')
        self.status_var = StringVar()
        self.hidden_status = IntVar()
        self.cur_range = []
        self.hover_selection = StringVar()
        self.hover_selection.set('')

        dir_label = Label(window, textvariable=self.cur_dir_full)
        dir_label.grid(row=0, column=0, sticky=W, padx=(15,0))
        
        back_button = Button(window, text='Back', command=self.go_back, width=8)
        back_button.grid(row=0, column=1, sticky=E, padx=(0,2))
        
        self.dir_window = Listbox(window, width=50, height=30)
        self.dir_window.grid(row=1, column=0, columnspan=2, padx=(15,2))
        self.dir_window.bind('<Double-Button-1>', self.intermediate)
        self.dir_window.bind('<{}>'.format(SELECTION_KEY), self.hover_option)
        
        status_label = Label(window, textvariable=self.status_var)
        status_label.grid(row=3, column=0, columnspan=2, pady=(0, 5))
        
        hidden_tickbox = Checkbutton(window, text='Show Hidden Files', var=self.hidden_status, command=self.update_options)
        hidden_tickbox.grid(row=2, column=0, columnspan=2)
        
        self.update_options()


    def hover_option(self, *others):
        if len(self.dir_window.curselection()) > 0:
            select_index = self.dir_window.curselection()[0]
            if self.options[select_index].endswith(':/'):
                self.hover_selection.set(self.options[select_index])
            elif self.cur_dir_full.get().endswith('/'):
                self.hover_selection.set(self.cur_dir_full.get() + self.options[select_index])
            else:
                self.hover_selection.set(self.cur_dir_full.get() + '/' + self.options[select_index])


    def test_os(self):
        """Identifies the device's operating system, sets an appropriate
        starting directory, and the method of opening files"""
        cur_platform = sys.platform
        
        if cur_platform == 'darwin':
            self.start_dir = '/'
            self.file_open = lambda x: subprocess.call(['open', x])
        elif cur_platform == 'win32':
            drives = [letter + ':/' for letter in ALPHABET if os.path.exists(letter + ':/')]
            self.start_dir = drives[0]
            self.file_open = lambda x: os.startfile(x)
        else:
            self.start_dir = '/'
            self.file_open = lambda x: subprocess.call(['xdg-open', x])


    def intermediate(self, *others):
        """Patches the transformation from Combobox to Listbox"""
        self.status_var.set('Everything is OK (at the moment)')
        select_index = self.dir_window.curselection()[0]
        self.cur_dir_last.set(self.options[select_index])
        if self.cur_dir_last.get().endswith(':/'):
            self.start_dir = self.cur_dir_last.get()
        self.new_path()
    
    
    def new_path(self, *others):
        """Adds the last selected folder to the current directory"""
        if self.cur_dir_full.get() == '':
            new_path = self.cur_dir_last.get()
            self.cur_dir_full.set(new_path)
            
        else:
            new_path = self.cur_dir_full.get() + self.cur_dir_last.get() + '/'
            if new_path.startswith(self.start_dir + '/'):
                new_path = self.start_dir + new_path[len(self.start_dir) + 1:]
            self.cur_dir_full.set(new_path)
            
        self.update_options()
    
    
    def update_options(self, *others):
        """Produces the new set of options for the listbox to display, or opens
        the file that was selected. Where the device is known to be Windows, and
        the user tries to go higher than root of one drive, some shifty business
        takes place to show the available drives.
        """
        if self.start_dir == self.cur_dir_full.get() and ':/' in self.start_dir and self.cur_dir_last.get() == '':
            self.cur_dir_full.set('')
            drives = [letter + ':/' for letter in ALPHABET if os.path.exists(letter + ':/')]
            self.options = drives
            self.update_range()
            self.status_var.set('Drive selection')
        
        elif os.path.isfile(self.cur_dir_full.get()[:-1]):
            file_path = self.cur_dir_full.get()
            self.go_back()
            self.file_open(file_path)
            self.status_var.set('File opened')
            
        else:
            try:
                contents = next(os.walk(self.cur_dir_full.get()))
                folders = sorted(contents[1])
                files = sorted(contents[2])
                
                all_options = folders + files
                if self.hidden_status.get() == 0:
                    all_options = self.clean_options(all_options)
                    
                self.options = all_options
                self.update_range()
                
            except:
                self.status_var.set('Something went wrong')
                self.go_back()

    
    def clean_options(self, all_options):
        """Checks if hidden files must be shown, and processes the current 
        options accordingly, then chucks them back at the option updater"""
        clean_options = []
        for option in all_options:
            if not(option[0] in ['.', '$', '~'] \
                     or option.lower()[-3:] in ['sys', 'ini', 'bak', 'xml', 'log', '.db']
                     or option.lower().startswith('ntuser') \
                     or option.lower()[-4:-1] == 'log'):
                clean_options.append(option)
                
        return clean_options

    
    def update_range(self, *others):
        """Updates the available values in the listbox"""
        self.dir_window.delete(0, END)
        for option in self.options:
            self.dir_window.insert(END, option)


    def go_back(self, *others):
        """Goes up a directory, or strips the opened filename from its path"""
        current_directory = self.cur_dir_full.get()
        
        if current_directory.endswith(':/'):
            self.cur_dir_full.set(self.start_dir)
            self.cur_dir_last.set('')
            self.update_options()
        elif current_directory == self.start_dir or current_directory == '':
            return 'huh?'
        
        parts = current_directory.split('/')[:-1]
        new_path = ''
        for index in range(len(parts) - 1):
            new_path += parts[index] + '/'
                
        self.cur_dir_full.set(new_path)  
        self.update_options()
        

class Replacegui:
    """Replaces a specified (non-empty) substring (old_chunk) with a specified
    new substring (new_chunk) in any file or folder name that includes the old
    substring.
    """
    def __init__(self, window, file_browser):
        """Sets up the two entry boxes and their super informative names,
        a fancy title label, a button and a status label"""
        self.file_browser = file_browser        

        self.old_chunk = StringVar()
        self.new_chunk = StringVar()
        self.summary = StringVar()

        title_label = Label(window, text='Name Editor', font=('Arial', 14), width=20, anchor=CENTER)
        title_label.grid(row=0, column=0, columnspan=2, sticky=N)

        old_entry_label = Label(window, text='Current:')
        old_entry_label.grid(row=1, column=0, sticky=E, padx=10, pady=(50,0))
        old_entry = Entry(window, textvariable=self.old_chunk)
        old_entry.grid(row=1, column=1, sticky=S+W)

        new_entry_label = Label(window, text='New:')
        new_entry_label.grid(row=2, column=0, sticky=E, padx=10, pady=5)
        new_entry = Entry(window, textvariable=self.new_chunk)
        new_entry.grid(row=2, column=1, sticky=W)

        process_button = Button(window, text='Replace', command=self.verify)
        process_button.grid(row=3, column=0, columnspan=2, sticky=N)
        
        summary_label = Label(window, textvariable=self.summary)
        summary_label.grid(row=4, column=0, columnspan=2, pady=(5,80), sticky=N)
        self.summary.set('Ready')

        explanation = """This module allows the user to replace
every instance of a user-defined
substring in the names of all of the
files and folders contained in the
same directory at the same time.

Steps:
1. Navigate to the directory (using the
   file browser) in which file or folder
   names must be edited.
2. Enter a string that must be searched
   for and replaced in the 'Current' entry
   box.
3. (Optional, enter a string in the 'New'
   entry box) click 'Replace' to swap every
   instance of the 'Current' substring with
   the empty string or the user-defined
   'New' substring"""
        description_label = Label(window, text=explanation)
        description_label.place(relx=0.03, rely=0.37)

    def verify(self, *others):
        """Ensures a valid substring (to be replaced in the present files and 
        folders) has been entered"""
        if self.old_chunk.get() == '':
            self.summary.set('Current substring required')
        else:
            self.process()
    
    def process(self):
        """Performs the actual replacement of old_chunk to new_chunk"""
        self.given_path = self.file_browser.cur_dir_full
        filenames = next(os.walk(self.given_path.get()))[1] + next(os.walk(self.given_path.get()))[2]
        counter = 0
        
        for filename in filenames:
            if self.old_chunk.get() in filename:
                name_pieces = filename.split(self.old_chunk.get())
                
                new_name = ''
                for index in range(len(name_pieces) - 1):
                    new_name += name_pieces[index] + self.new_chunk.get()
                new_name += name_pieces[-1]
                
                old_path = self.given_path.get() + '/' + filename
                new_path = self.given_path.get() + '/' + new_name
                shutil.move(old_path, new_path)
                counter += 1
                
        if counter == 1:
            plural = ''
        else:
            plural = 's'
            
        summary_message = 'Process successful, {} file{} renamed.'.format(counter, plural)
        self.summary.set(summary_message)
        self.file_browser.update_options()


class Emptier:
    """Moves all of the files on any directory descending from the 
    user-specified path to the user-specified path, and removes the folders.
    """
    def __init__(self, window, file_browser):
        """Sets up a title, a tickbox (as a safety measure), a button that could
        ruin your OS, and a status label"""
        self.file_browser = file_browser
        self.tick_var = IntVar()
        self.status_var = StringVar()

        title_label = Label(window, text='Subfolder Emptier', font=('Arial', 14), width=20, anchor=CENTER)
        title_label.grid(row=0, column=0, sticky=N)
        
        empty_button = Button(window, text='Empty Subfolders', command=self.attempt_to_empty)
        empty_button.grid(row=1, column=0, pady=(50,0))
        
        tick_box = Checkbutton(window, text='Confirm', var=self.tick_var, command=self.status)
        tick_box.grid(row=2, column=0, pady=5)
        
        status_label = Label(window, textvariable=self.status_var)
        status_label.grid(row=3, column=0, padx=5)

        explanation = """This module allows the user to bring
all of the files found in all subfolders
of the current directory up to the
current directory, and delete all of the
empty folders - in just two clicks.
   
Steps:
1. Navigate to the directory in the
   filebrowser from which subfolders
   must be emptied.
2. Click on the tickbox to confirm your
   intent to empty subfolders.
3. Click the 'Empty Subfolders' button.
   (Warning: cannot be undone)"""
        description_label = Label(window, text=explanation)
        description_label.place(relx=0.03, rely=0.37)
        self.status()
        
        
    def status(self, *others):
        """Comments on the status of the tickbox"""
        tick_status = self.tick_var.get()
        if tick_status == 0:
            self.status_var.set('Not primed')
        elif tick_status == 1:
            self.status_var.set('Primed')
        
            
    def attempt_to_empty(self, *others):
        """Consults the value of the tickbox. If the tickbox has been primed,
        the folder emptying process is carried out with the current path from
        the filebrowser, and the tickbox is reset to not primed"""
        tick_status = self.tick_var.get()
        if tick_status == 0:
            self.status_var.set('Must be primed to Continue')
        elif tick_status == 1:
            self.tick_var.set(0) # Immediately un-prime again
            given_path = self.file_browser.cur_dir_full.get()
            try:
                self.empty_subfolders(given_path)
                self.file_browser.update_options()
                self.status_var.set('The folders were successfully emptied') 
            except:
                self.status_var.set('Something went wrong')
                

    def empty_subfolders(self, given_path):
        """Empties the present subfolders (probably not in the most efficient way,
        sue me)"""
        child_folder_list = self.all_subfolders(given_path)
        nevermind = False
        
        for folder in child_folder_list:
            folder_files = self.scour_files(folder)
    
            for file in folder_files:
                cur_dir = folder + '/' + file
                new_dir = given_path + '/' + file
    
                if os.path.exists(new_dir) and '(' in new_dir and ')' in new_dir \
                   and new_dir.index('(') < new_dir.index(')'):
                    before_end = new_dir.split(')')[-2]
                    middle_bit = before_end.split('(')[-1]
                    if middle_bit.isdigit():

                        fallback_counter = int(middle_bit)
                        while os.path.exists(new_dir):
                            name_pieces = file.split('(')
                            new_name = ''
                            for index in range(len(name_pieces) - 1):
                                new_name += name_pieces[index] + '('
                            new_name = new_name + str(fallback_counter) + ')' + file.split(')')[-1]
                            new_dir = given_path + '/' + new_name
                            fallback_counter += 1
                            nevermind = True

                if not(nevermind):
                    fallback_counter = 1
                    while os.path.exists(new_dir):
                        fallback_counter += 1
                        name_pieces = file.split('.')
                        new_name = ''
                        for index in range(len(name_pieces) - 1):
                            new_name += name_pieces[index] + '.'
                        new_name = new_name[:-1] + ' (' + str(fallback_counter) + ').' + name_pieces[-1]
                        new_dir = given_path + '/' + new_name
                    
                shutil.move(cur_dir, new_dir)
    
        child_folder_list.reverse()
        for folder in child_folder_list:
            os.rmdir(folder)

        

    def all_subfolders(self, given_path):
        """Finds all child folders, returns them as a sorted list"""
        current_path = given_path
        child_folders = self.scour_folders(current_path)
    
        master_set = set()
        for folder in child_folders:
            if not(folder.endswith('app')):
                master_set.add(given_path + '/' + folder)
    
        testpoint1 = 0
        testpoint2 = len(master_set)
    
        while testpoint1 != testpoint2:
            testpoint1 = testpoint2
    
            master_additions = []
            terminal_paths = set()
            
            for path in master_set:
                if path in terminal_paths:
                    continue
                    
                path_child_folders = self.scour_folders(path)
                
                if len(path_child_folders) ==0:
                    terminal_paths.add(path)
                    
                for folder_name in path_child_folders:
                    master_additions.append(path + '/' + folder_name)
    
            for new_term in master_additions:
                master_set.add(new_term)
                
            testpoint2 = len(master_set)
            
        return sorted(list(master_set))


    def scour_files(self, given_path):
        """Returns a list of filenames for the files in the given_path"""
        return next(os.walk(given_path))[2]


    def scour_folders(self, given_path):
        """Returns a list of folder names for the folders in the given_path"""
        return next(os.walk(given_path))[1]


class Movestuff:
    def __init__(self, window, file_browser):
        self.file_browser = file_browser
        self.file_browser.hover_selection.trace('w', self.add_to_selection)
        full_width = 3
        self.button_width = 15
        self.selection_list = []
        self.hover_selection = ''
        self.status_var = StringVar()
        self.status_var.set('Ready')
        
        title_label = Label(window, text='General', font=('Arial', 14), width=20, anchor=CENTER)
        title_label.grid(row=0, column=0, columnspan=full_width, sticky=N)

        self.selection_listbox = Listbox(window, width=35, height=6)
        self.selection_listbox.grid(row=2, column=0, columnspan=3, sticky=N)
        self.selection_listbox.bind('<{}>'.format(SELECTION_KEY), self.hover_option)

        deselect_button = Button(window, text='Copy', command=self.copy_selection, width=self.button_width)
        deselect_button.grid(row=3, column=0, sticky=N)

        select_button = Button(window, text='Move', command=self.move_selection, width=self.button_width)
        select_button.grid(row=3, column=2, sticky=N)

        delete_button = Button(window, text='Delete', command=self.delete_the_things, width=self.button_width)
        delete_button.grid(row=4, column=0, sticky=N)
        
        new_folder_button = Button(window, text='New Folder', command=self.new_folder, width=self.button_width)
        new_folder_button.grid(row=4, column=2, sticky=N)
        
        status_label = Label(window, textvariable=self.status_var)
        status_label.grid(row=5, column=0, columnspan=3, pady=(0,5))
        
        explanation = """This module allows the user to perform
four basic tasks that one expects from
a file browser; copy, move, and delete
files and folders, and creating new
folders.

Steps:
1. Add files and folders to the above
   selection by clicking on the item in
   the file browser and then pressing
   {0}. (Optional, remove items
   from the selection by clicking on
   the item in the selection and then
   pressing {0}).
2. Navigate to the end directory and
   click 'Copy' or 'Move' to bring the
   items to the new directory.
   OR
   Click 'Delete' to delete every selected
   item. (Warning: this cannot be undone)""".format(SELECTION_KEY.upper())
        
        description_label = Label(window, text=explanation)
        description_label.place(relx=0.03, rely=0.37)

    def add_to_selection(self, *others):
        new_option = self.file_browser.hover_selection.get()
        if not(new_option == ''):
            valid = True
            for option in self.selection_list:
                if (os.path.isdir(new_option) or os.path.isdir(option)) and \
                   (new_option.startswith(option + '/') or option.startswith(new_option + '/')):
                    valid = False
                    self.status_var.set('Cannot modify child with parent')
            
            if new_option in self.selection_list:
                valid = False
                self.status_var.set('Item already selected')                

            if valid:
                if os.path.isfile(new_option):
                    self.status_var.set('File added to selection')
                else:
                    self.status_var.set('Folder added to selection') 
                self.selection_list.append(new_option)


            self.update_list()


    def remove_from_selection(self):
        if self.hover_selection in self.selection_list:
            self.selection_list.remove(self.hover_selection)

        self.update_list()


    def move_selection(self, *others):
        end_path = self.file_browser.cur_dir_full.get() + '/'
        selection_list_copy = self.selection_list[:]
        counter = 0
        for item in self.selection_list:
            item_name = item.split('/')[-1]
            resulting_path = end_path + item_name
            if not(os.path.exists(resulting_path)):
                counter += 1
                shutil.move(item, resulting_path)
                selection_list_copy.remove(item)

        if counter == 1:
            plural = ''
        else:
            plural = 's'
            
        template = 'Process successful, {} item{} moved'
        self.status_var.set(template.format(counter, plural))
        self.selection_list = selection_list_copy
        self.update_list()
        self.file_browser.update_options()
        

    def copy_selection(self, *others):
        end_path = self.file_browser.cur_dir_full.get() + '/'
        selection_list_copy = self.selection_list[:]
        counter = 0
        for item in self.selection_list:
            item_name = item.split('/')[-1]
            resulting_path = end_path + item_name
            if not(os.path.exists(resulting_path)):
                counter += 1
                if os.path.isdir(item):
                    copy_tree(item, resulting_path)
                else:
                    shutil.copy(item, resulting_path)
                selection_list_copy.remove(item)

        if counter == 1:
            plural = ''
        else:
            plural = 's'
            
        template = 'Process successful, {} item{} copied'
        self.status_var.set(template.format(counter, plural))

        self.selection_list = selection_list_copy
        self.update_list()
        self.file_browser.update_options()


    def new_folder(self, *others):
        current_path = self.file_browser.cur_dir_full.get() + '/'
        template = 'New Folder{}'
        end_path = current_path + template.format('')
        counter = 1
        while os.path.isdir(end_path):
            counter += 1
            end_path = current_path + template.format(' (' + str(counter) + ')')
        
        os.makedirs(end_path)
        self.status_var.set('New folder added')
        self.file_browser.update_options()


    def delete_the_things(self, *others):
        selection_list_copy = self.selection_list[:]
        counter = 0
        for item in self.selection_list:
            counter += 1
            if os.path.isfile(item):
                os.remove(item)
                    
            else:
                shutil.rmtree(item)

            selection_list_copy.remove(item)

        if counter == 1:
            plural = ''
        else:
            plural = 's'
            
        template = 'Process successful, {} item{} deleted'
        self.status_var.set(template.format(counter, plural))

        self.selection_list = selection_list_copy
        self.update_list()
        self.file_browser.update_options()


    def hover_option(self, *others):
        select_index = self.selection_listbox.curselection()[0]
        self.hover_selection = self.selection_list[select_index]
        self.remove_from_selection()

        
    def update_list(self):
        self.selection_listbox.delete(0, END)
        for option in self.selection_list:
            self.selection_listbox.insert(END, option)


def main():
    """Constructs the main window, and the appropriate frames for the
    individual tools"""
    window = Tk()
    window.title('File Browser')
    window.resizable(width=False, height=False)
    Maingui(window)
    window.mainloop()


main()
