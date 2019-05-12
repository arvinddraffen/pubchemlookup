# Tkinter imports
import tkinter
from tkinter import Button, Entry, filedialog, Label, messagebox, Tk, ttk

# Python Imaging Library (PIL, now pillow) for displaying .png retrieved from PubChem
from PIL import ImageTk, Image          # pip3 install pillow (for Python 3)

# Imports used for PUG REST HTTP request and JSON data parsing
import requests                         # pip3 install requests
import json

# For displaying error in popup
import traceback

# Used in removing temporary image file
import os

class PubChemGUI:
    def __init__(self, master):
        self.master = master
        master.title("PubChem Lookup")
        self.status_codes = {200:["(none)", "Success"],
                            202:["(none)", "Accepted (asynchronous operation pending)"],
                            400:["PUGREST.BadRequest", "Request is improperly formed (syntax error in the URL, POST body, etc."],
                            404:["PUGREST.NotFound", "The input record was not found (e.g. invalid CID"],
                            405:["PUGREST.NotAllowed", "Request not allowed (such as invalid MIME type in the HTTP Accept header"],
                            504:["PUGREST.Timeout", "The request timed out, from server overload or too broad a request"],
                            503:["PUGREST.ServerBusy", "Too many requests or server is busy, retry later"],
                            501:["PUGREST.Unimplemented", "The requested operation has not (yet) been implemented by the server"],
                            500:["PUGREST.ServerError or PUGREST.Unknown", "Some problem on the server side (such as a database server down, etc. or an unknown error occurred"]}
        self.compoundFound = False    
        self.init_gui()

    def init_gui(self):
        """Prepares Elements for GUI Using tkinter Grid"""
        self.frame = tkinter.Frame(root)
        self.frame.grid(column = 0, row = 0, padx = (5,10), pady = (2,2))
        self.compoundLabel = Label(self.frame, text = "Enter compound to search:")
        self.compoundLabel.pack(side = tkinter.LEFT, padx = (5,5))
        self.searchTypes = ["Name", "CID"]
        self.searchTypeCombobox = ttk.Combobox(self.frame, state = "readonly",values=self.searchTypes)
        self.searchTypeCombobox.current(0)
        self.searchTypeCombobox.pack(side = tkinter.LEFT, padx = (5,5), pady = (0,0))
        self.text = Entry(root, width = 20)
        self.text.grid(column = 1, row = 0, columnspan = 2, padx = (10,5), pady = (0,0))
        self.text.focus()
        def submitBtnAction():

            self.searchType = self.searchTypeCombobox.get()
            if self.searchType == self.searchTypes[0]:
                self.name = self.text.get()
                self.get_compound_from_text(self.name)
            elif self.searchType == self.searchTypes[1]:
                cid = self.text.get()
                try:
                    cid = int(cid)
                    self.retrieve_compound_info(cid)
                except ValueError:
                    messagebox.showerror("Error", traceback.format_exc())
        self.submitBtn = Button(root, text = "Search PubChem Database", command = submitBtnAction)
        self.submitBtn.grid(column = 3, row = 0, padx = (10,5))

        root.update()
        root.minsize(root.winfo_width() + 10, root.winfo_height() + 10)

        self.structureLabel = Label(root)
        self.structureLabel.grid(column = 0, row = 1, rowspan = 6)
        self.structureLabel.grid_remove()
        self.structureLabelLabel = Label(root, font = "Verdana 13 bold")
        self.structureLabelLabel.grid(column = 0, row = 7)
        self.structureLabelLabel.grid_remove()

        self.molecularFormulaLabelLabel = Label(root, text = "Molecular Formula:", font = "Verdana 10 bold")
        self.molecularFormulaLabelLabel.grid(column = 1, row = 1)
        self.molecularFormulaLabelLabel.grid_remove()
        self.molecularFormulaLabel = Label(root)
        self.molecularFormulaLabel.grid(column = 1, row = 2)
        self.molecularFormulaLabel.grid_remove()

        self.molecularWeightLabelLabel = Label(root, text = "Molecular Weight: ", font = "Verdana 10 bold")
        self.molecularWeightLabelLabel.grid(column = 1, row = 3)
        self.molecularWeightLabelLabel.grid_remove()
        self.molecularWeightLabel = Label(root)
        self.molecularWeightLabel.grid(column = 1, row = 4)
        self.molecularWeightLabel.grid_remove()

        self.IUPACNameLabelLabel = Label(root, text = "IUPAC Name: ", font = "Verdana 10 bold")
        self.IUPACNameLabelLabel.grid(column = 1, row = 5)
        self.IUPACNameLabelLabel.grid_remove()
        self.IUPACNameLabel = Label(root)
        self.IUPACNameLabel.grid(column = 1, row = 6)
        self.IUPACNameLabel.grid_remove()

        self.infoLabel = Label(root, text = "Information", font = "Verdana 13 bold")
        self.infoLabel.grid(column = 1, row = 7)
        self.infoLabel.grid_remove()

        self.exportTxtBtn = Button(root, text = "Export to TXT", command = self.exportTxtBtnAction)
        self.exportImgBtn = Button(root, text = "Save Image", command = self.saveImgBtnAction)
        self.exportTxtBtn.grid(column = 3, row = 1, padx = (10,5), pady = (5,5))
        self.exportImgBtn.grid(column = 3, row = 2, padx = (10,5))
        self.exportTxtBtn.grid_remove()
        self.exportImgBtn.grid_remove()

    def exportTxtBtnAction(self):
        """Prompts for directory to save txt file output when corresponding button (self.exportTxtBtn) is pressed"""
        try:
            if self.compoundFound:
                saveDirectory = filedialog.asksaveasfilename(filetypes=[("Text Files (*.txt)", "*.txt")], defaultextension=".txt", initialfile = self.name)
                with open(saveDirectory, 'w+') as file:
                    file.write(json.dumps(data))
        except:
            FileNotFoundError           # user exited filedialog popup
            self.compoundFound = False
    def saveImgBtnAction(self):
        """Prompts for directory to save structure image output when corresponding button (self.exportImgBtn) is pressed"""
        try:
            if self.compoundFound:
                saveDirectory = filedialog.asksaveasfilename(filetypes=[("PNG (*.png)", "*.png")], defaultextension=".png", initialfile = self.name)
                with open(saveDirectory, 'wb') as file:
                    file.write(self.imagerequest.content)
        except:
            FileNotFoundError
            self.compoundFound = False

    def get_compound_from_text(self, name):
        """Queries PubChem database for text entered to determine if the input is valid"""
        try:
            r = requests.get("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/" + name + "/cids/JSON")
            data = r.json()
            if 'Fault' in data:
                messagebox.showerror("Error", str(data['Fault']['Code']) + "\n" + str(data['Fault']['Details'][0]))
            elif len(data['IdentifierList']['CID']) > 1:
                ret = messagebox.askyesno("Warning", "Multiple values returned with CIDs " + str(data['IdentifierList']['CID']) + "\nWill use first CID of " + str(data['IdentifierList']['CID'][0]) + "\nProceed?")
                if ret:
                    self.retrieve_compound_info(data['IdentifierList']['CID'][0])
                    self.compoundFound = True
            else:
                self.retrieve_compound_info(data['IdentifierList']['CID'][0])
                self.compoundFound = True
        except:
            requests.exceptions.ConnectionError
            messagebox.showerror("Error", traceback.format_exc())

    def retrieve_compound_info(self, cid):
        """Queries PubChem database based on CID entered, or returned based on text input, for molecular structure, molecular formula, molecular weight, and IUPAC name"""
        #Retrieve molecular structure
        self.imagerequest = requests.get("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/" + str(cid) + "/PNG")
        if self.imagerequest.status_code != 200 and self.imagerequest.status_code != 202:
            self.compoundFound = False
            print(self.imagerequest.status_code)
            messagebox.showerror("Error", self.status_codes[self.imagerequest.status_code][0] + "\n" + self.status_codes[self.imagerequest.status_code][1])
        else:
            open('structure.png', 'wb').write(self.imagerequest.content)
            
            # Place molecular structure on window
            self.img = ImageTk.PhotoImage(Image.open('structure.png'))
            os.remove('structure.png')

            # Retrieve information about molecule/compound (specifically molecular formula, molecular weight, IUPAC name)
            r = requests.get("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/" + str(cid) + "/property/MolecularFormula,MolecularWeight,IUPACName/JSON")
            data = r.json()

            if self.searchType == self.searchTypes[1]:
                request = requests.get("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/" + str(cid) + "/synonyms/JSON")
                names = request.json() 
                print(names)
                if 'Fault' in names:
                    messagebox.showerror("Error", str(names['Fault']['Code']) + "\n" + str(names['Fault']['Message']))
                    self.name = ""
                else:
                    self.name = names['InformationList']['Information'][0]['Synonym'][0] # Error-check for no name returned (example: 498)

            # Assign Retrieved Data
            if 'MolecularFormula' not in str(data['PropertyTable']['Properties'][0]):
                self.molecularFormula = "Nothing returned"
                messagebox.showwarning("Warning", message = "No molecular formula returned")
            else:
                self.molecularFormula = str(data['PropertyTable']['Properties'][0]['MolecularFormula'])

            if 'MolecularWeight' not in str(data['PropertyTable']['Properties'][0]):
                self.molecularWeight = "Nothing returned"
                messagebox.showwarning("Warning", message = "No molecular weight returned")
            else:
                self.molecularWeight = str(data['PropertyTable']['Properties'][0]['MolecularWeight'])

            if 'IUPACName' not in str(data['PropertyTable']['Properties'][0]):
                self.IUPACName = "N/A"
                messagebox.showwarning("Warning", message = "No IUPAC name returned")
            else:
                self.IUPACName = str(data['PropertyTable']['Properties'][0]['IUPACName'])

            self.compoundFound = True
            self.update_gui(cid)

    def update_gui(self, cid):
        """Displays GUI elements setup in init_gui() based on information retrieved from PubChem database"""
        self.structureLabel.config(image = self.img)
        self.structureLabel.grid()
        self.structureLabelLabel.config(text = str(self.name).title() + " (CID: " + str(cid) + ")")
        self.structureLabelLabel.grid()

        self.molecularFormulaLabel.config(text = self.molecularFormula)
        self.molecularFormulaLabelLabel.grid()
        self.molecularFormulaLabel.grid()

        self.molecularWeightLabel.config(text = self.molecularWeight)
        self.molecularWeightLabelLabel.grid()
        self.molecularWeightLabel.grid()

        self.IUPACNameLabel.config(text = self.IUPACName)
        self.IUPACNameLabelLabel.grid()
        self.IUPACNameLabel.grid()

        self.infoLabel.grid()

        if self.compoundFound:
            self.exportTxtBtn.grid()
            self.exportImgBtn.grid()
        else:
            self.exportTxtBtn.grid_remove()
            self.exportImgBtn.grid_remove()

        root.update()
        root.minsize(root.winfo_width(), root.winfo_height()) 


if __name__ == '__main__':
    root = Tk()
    gui = PubChemGUI(root)
    root.mainloop()
