"""
BASICS

Analyzes the MIDAS README and draws conclusions.
Deals with finding the OS and the languages used
"""

import os, shutil


# Finds the corresponding image to the OS
OS_chart = {'Ubuntu_16.04':'carlosred/ubuntu-midas:16.04'}
# Python refers to python3 by default, python2 is not supported
# No need for installation
# Avoids language names inside other language names
Allowed_languages = sorted(['python', 'r', 'c', 'c++', 'haskell', 'fortran', 'bash'], key=len, reverse=True)
language_instructions = {
        'python':{'Ubuntu_16.04':'echo python is installed by default'},
        'fortran':{'Ubuntu_16.04':'apt-get install gfortran -y'},
        'bash':{'Ubuntu_16.04':'echo bash is installed by default'},
        'r':{'Ubuntu_16.04':'apt-get install r-base -y'}}
libraries_instructions = {'python':'pip3 install LIBRARY'}
# Does necessarily follow the convention, mostly as a 
language_compiled = {'python':False, 'c++':True, 'fortran':True, 'bash':False, 'r':True}
# C++ is going to require a lot of special instructions
command_instructions = {
        'python':'python3 FILE',
        'fortran':'gfortran FILE -o a.out',
        'bash':'bash FILE',
        'r':'Rscript FILE'
}


# Verifies that a file has all 5 required inputs
# README_path (str): Must be the full path to the README
def valid_README(README_path):
	
    qualifier = [['OS)', 'LANGUAGE)', 'COMMAND)', 'OUTPUT)'], [0, 0, 0, 0]]

    for nvnv in range(0, len(qualifier[0])):
        with open(README_path, 'r') as README:
            for line in README:
                if '#' == line.replace(" ", '')[0]:
                    continue
                if qualifier[0][nvnv] in line:
                    qualifier[1][nvnv] = 1
                    break

    if 0 in qualifier[1]:
        return False
    return True


# Reads the README and writes if to a file of the same name (ignoring comments)
# Writes a new README in the same folder
def parser(README_path):

    with open(README_path, "r") as README:
        with open("READREAD.txt", 'w') as R2:
            for line in README:
                if line.replace(" ", '')[0] == '#':
                    continue
                R2.write(line)
    os.remove("README.txt")
    shutil.move("READREAD.txt", "README.txt")


# Finds the OS
def valid_OS(README_path):

    with open(README_path, "r") as README:
        for line in README:
            # Only one OS is needed
            for onos in OS_chart.keys():
                if onos in line:
                    return onos
        
    # OS must be specified
    return False


# Finds the language(s)
def valid_language(README_path):

    lang_used = []
    with open(README_path, 'r') as README:
        for line in README:
            if 'LANGUAGE)' not in line:
                continue
            LLL = line.replace('\n', '').lower()
            for lang in Allowed_languages:
                if lang in LLL:
                    lang_used.append(lang)
                    break

    if len(lang_used) == 0:
        return False

    return list(set(lang_used))


# Finds all the input files
# FILES_PATH (str): Path to all the files, inclusing the readme
def present_input_files(FILES_PATH):
    files_needed = os.listdir(FILES_PATH)
    files_present = []

    with open(FILES_PATH+"/README.txt", 'r') as README:
        for line in README:
            if "COMMAND)" not in line:
                continue

            LLL = line.replace("COMMAND)", '').replace('\n', '').replace(' ', '')
            files_present.append(LLL.split(':'))

            if files_present[-1][1] not in files_needed:
                return False

    return files_present


# Installation instructions for each OS
def install_OS(README_path):
    actual_OS = valid_OS(README_path)
    return 'FROM '+OS_chart[actual_OS]


# Installation instructions for each language
# LANGUAGE (str): Language name
# USED_OS (str)
def install_language(LANGUAGE, USED_OS):
    return language_instructions[LANGUAGE][USED_OS]


# Finds the setup files and executes the command bash on each of them
def user_guided_setup(README_path):

    SETUP_INSTRUCTIONS = []
    with open(README_path, 'r') as README:
        for line in README:
            if "USER_SETUP)" not in line:
                continue
            SETUP_INSTRUCTIONS.append("bash "+line.replace("USER_SETUP)", '').replace('\n', '').replace(' ', ''))

    return SETUP_INSTRUCTIONS


# Recognizes a programming language is a sentence in a sentence
# SENTEN (str): Sentence to analyze
def recognize_language(SENTEN):

    for LANG in Allowed_languages:
        if LANG in SENTEN:
            return LANG

    return False


# Finds the necessary libraries and returns instructions about how to install them
def install_libraries(README_path):

    LIBS_INSTRUCTIONS = []
    with open(README_path, 'r') as README:
        for line in README:
            if 'LIBRARY)' not in line:
                continue
            LLL = line.lower().replace(' ', '').replace('\n', '').split(':')
            curlang = recognize_language(LLL[0])
            if curlang not in libraries_instructions.keys():
                return False

            LIBS_INSTRUCTIONS.append(libraries_instructions[curlang].replace('LIBRARY', LLL[1]))

    return LIBS_INSTRUCTIONS


# Returns the copy instructions for all the files present
def copy_files_to_image(FILES_PATH):

    ins = []
    for file in os.listdir(FILES_PATH):
        ins.append("COPY "+file+" /work/"+file)

    return ins


# Returns a valid command
# COMMAND (arr) (str): LANGUAGE, FILE
# cpp_libs (arr) (str: C++ libraries, only useful for C++ 
def execute_command(COMMAND, cpp_libs=[]):

    # Finds the language
    LANG = recognize_language(COMMAND[0].lower())

    if not language_compiled[LANG]:
        return command_instructions[LANG].replace('FILE', COMMAND[1])

    # Compiled instructions go line by line
    if LANG == 'fortran':
        # Cannot accept libraries
        com1 = command_instructions[LANG].replace('FILE', COMMAND[1])
        return com1+" && ./a.out"

    if LANG == 'r':

        com1 = command_instructions[LANG].replace('FILE', COMMAND[1])
        if len(COMMAND) == 3:
            return com1+" > "+str(COMMAND[2])
        
