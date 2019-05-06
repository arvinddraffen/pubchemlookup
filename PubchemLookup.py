# Tkinter imports
import tkinter
from tkinter import Button, Entry, filedialog, Label, messagebox, Tk

# Python Imaging Library (PIL, now pillow) for displaying .png retrieved from PubChem
from PIL import ImageTk, Image          # pip3 install pillow (for Python 3)

# Imports used for PUG REST HTTP request and JSON data parsing
import requests                         # pip3 install requests
import json

# For displaying error in popup
import traceback

class PubChemGUI:
    def __init__(self, master):
        self.master = master
        master.title("PubChem Lookup")
        self.init_gui()

    def init_gui(self):
        self.compountLabel = Label(root, text = "Enter compound to search:")
        self.compountLabel.grid(column = 0, row = 0, padx = (5,10), pady = (5,5))
        self.text = Entry(root, width = 20)
        self.text.grid(column = 1, row = 0, columnspan = 2, padx = (10,5), pady = (5,5))
        self.text.focus()
        def submitBtnAction():
            self.name = self.text.get()
            self.get_compound(self.name)
        self.submitBtn = Button(root, text = "Search PubChem Database", command = submitBtnAction)
        self.submitBtn.grid(column = 3, row = 0, padx = (10,5), pady = (5,5))

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

    def get_compound(self, name):
        try:
            r = requests.get("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/" + name + "/cids/JSON")
            data = r.json()
            if 'Fault' in data:
                messagebox.showerror("Error", str(data['Fault']['Code']) + "\n" + str(data['Fault']['Details'][0]))
            elif len(data['IdentifierList']['CID']) > 1:
                ret = messagebox.askyesno("Warning", "Multiple values returned with CIDs " + str(data['IdentifierList']['CID']) + "\nWill use first CID of " + str(data['IdentifierList']['CID'][0]) + "\nProceed?")
                if ret:
                    self.retrieve_compound_info(data['IdentifierList']['CID'][0])
            else:
                self.retrieve_compound_info(data['IdentifierList']['CID'][0])
        except:
            requests.exceptions.ConnectionError
            messagebox.showerror("Error", traceback.format_exc())

        def saveBtnAction():
            try:
                saveDirectory = filedialog.asksaveasfilename(filetypes=[("Text Files", "*.txt")], defaultextension=".txt", initialfile = self.name)
                with open(saveDirectory, 'w+') as file:
                    file.write(json.dumps(data))
            except:
                FileNotFoundError           # user exited filedialog popup

        self.exportBtn = Button(root, text = "Export to TXT", command = saveBtnAction)
        self.exportBtn.grid(column = 3, row = 1, padx = (10,5), pady = (5,5))

    def retrieve_compound_info(self, cid):
        #Retrieve molecular structure
        r = requests.get("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/" + str(cid) + "/PNG")
        open('structure.png', 'wb').write(r.content)
        
        # Place molecular structure on window
        self.img = ImageTk.PhotoImage(Image.open('structure.png'))

        # Retrieve information about molecule/compound (specifically molecular formula, molecular weight, IUPAC name)
        r = requests.get("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/" + str(cid) + "/property/MolecularFormula,MolecularWeight,IUPACName/JSON")
        data = r.json()

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

        self.update_gui(cid)

    def update_gui(self, cid):
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

        root.update()
        root.minsize(root.winfo_width(), root.winfo_height()) 


if __name__ == '__main__':
    root = Tk()
    gui = PubChemGUI(root)
    root.mainloop()
