import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import urllib.parse
from datetime import datetime
import os

# ✅ NEW (for JPEG support)
from PIL import Image, ImageTk

# ---------------- SAFE SYMPTOMS DATABASE ----------------

SYMPTOM_DB = {
    "Cold / Runny Nose": ["Steam inhalation (5–10 minutes)", "Warm fluids and rest"],
    "Cough": ["Honey in warm water (not for infants)", "Warm fluids"],
    "Sore Throat": ["Warm salt water gargle", "Warm fluids"],
    "Headache": ["Adequate rest", "Drink water"],
    "Indigestion / Acidity": ["Warm water after meals", "Light food"],
    "Constipation": ["Warm water in morning", "Fiber-rich food"],
    "Mild Fever": ["Rest", "Hydration"],
    "Fatigue / Weakness": ["Adequate sleep", "Nutritious food"],
    "Stress / Anxiety": ["Deep breathing", "Short walks"],
    "Poor Sleep": ["Relaxation before bed", "Avoid screens at night"],
    "Mild Body Pain": ["Warm compress", "Rest"],
    "Other (Not listed)": []
}

WHO_LINK = "https://www.who.int/health-topics/traditional-complementary-and-integrative-medicine"

# ---------------- START SCREEN ----------------

class StartScreen:
    def __init__(self, root):
        self.root = root
        root.title("HealSync Start")

        root.state('zoomed')   # FULL SCREEN

        # LOAD JPEG IMAGE
        img = Image.open("start.jpeg")

        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()

        img = img.resize((width, height))
        self.img = ImageTk.PhotoImage(img)

        label = tk.Label(root, image=self.img)
        label.pack(fill="both", expand=True)

        # Click anywhere to continue
        label.bind("<Button-1>", self.open_main)

    def open_main(self, event):
        self.root.destroy()
        main_root = tk.Tk()
        HealSyncApp(main_root)
        main_root.mainloop()

# ---------------- APP ----------------

class HealSyncApp:
    def __init__(self, root):
        self.root = root
        root.title("HealSync – Ayurvedic Support")
        root.geometry("780x720")

        root.configure(bg="#d0f0ff")

        tk.Label(root, text="HEALSYNC – AYURVEDIC MODULE",
                 font=("Arial", 16, "bold"), bg="#d0f0ff").pack(pady=8)

        frame = tk.Frame(root, bg="#d0f0ff")
        frame.pack(padx=15, pady=5)

        tk.Label(frame, text="Name", bg="#d0f0ff").grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.name_var, width=40).grid(row=0, column=1)

        tk.Label(frame, text="Age", bg="#d0f0ff").grid(row=1, column=0, sticky="w")
        self.age = ttk.Combobox(frame, values=[str(i) for i in range(1,101)], width=38)
        self.age.set("25")
        self.age.grid(row=1, column=1)

        tk.Label(frame, text="Gender", bg="#d0f0ff").grid(row=2, column=0, sticky="w")
        self.gender = ttk.Combobox(frame, values=["Female","Male","Other"], width=38)
        self.gender.set("Female")
        self.gender.grid(row=2, column=1)

        tk.Label(frame, text="Weight (kg)", bg="#d0f0ff").grid(row=3, column=0, sticky="w")
        self.weight = ttk.Combobox(frame, values=[str(i) for i in range(20,181)], width=38)
        self.weight.set("55")
        self.weight.grid(row=3, column=1)

        tk.Label(frame, text="Symptoms", bg="#d0f0ff").grid(row=4, column=0, sticky="w")
        self.symptom_text = tk.StringVar(value="None selected")
        tk.Entry(frame, textvariable=self.symptom_text, state="readonly", width=40).grid(row=4, column=1)
        tk.Button(frame, text="Select", command=self.select_symptoms).grid(row=4, column=2)

        tk.Label(frame, text="If Other, type symptom", bg="#d0f0ff").grid(row=5, column=0, sticky="w")
        self.other_symptom = tk.StringVar()
        tk.Entry(frame, textvariable=self.other_symptom, width=40).grid(row=5, column=1)

        tk.Button(root, text="SUBMIT", font=("Arial",13,"bold"),
                  bg="black", fg="white", command=self.submit).pack(pady=8)

        tk.Button(root, text="View History", command=self.view_history).pack()

        tk.Label(root, text=
            "Precautions:\n"
            "• Pregnant women should avoid strong herbs\n"
            "• If symptoms last >48 hrs consult doctor\n"
            "• Avoid remedies if allergic",
            fg="gray", bg="#d0f0ff").pack(pady=6)

        self.symptom_vars = {k: tk.IntVar() for k in SYMPTOM_DB}

    # (ALL YOUR REMAINING CODE SAME — NO CHANGE)

    def select_symptoms(self):
        win = tk.Toplevel(self.root)
        win.title("Select Symptoms")
        for s in SYMPTOM_DB:
            tk.Checkbutton(win, text=s, variable=self.symptom_vars[s]).pack(anchor="w")
        tk.Button(win, text="Done", command=lambda:[
            self.symptom_text.set(", ".join([k for k,v in self.symptom_vars.items() if v.get()])),
            win.destroy()
        ]).pack(pady=5)

    def submit(self):
        name = self.name_var.get().strip()
        selected = [k for k,v in self.symptom_vars.items() if v.get()]

        if not name or not selected:
            messagebox.showerror("Error","Enter name and select symptoms")
            return

        dt = datetime.now().strftime("%d-%m-%Y %H:%M")
        rows = []

        for s in selected:
            if s == "Other (Not listed)":
                other = self.other_symptom.get().strip()
                remedy = "Refer Google / WHO"
                rows.append((dt, name, self.age.get(), self.gender.get(),
                             self.weight.get(), other, remedy))
            else:
                remedy = ", ".join(SYMPTOM_DB[s])
                rows.append((dt, name, self.age.get(), self.gender.get(),
                             self.weight.get(), s, remedy))

        self.show_output(rows)

    def show_output(self, rows):
        win = tk.Toplevel(self.root)
        win.title("Output")
        win.geometry("900x400")
        win.configure(bg="#ccffcc")

        cols = ("DateTime","Name","Age","Gender","Weight","Symptom","Remedies")
        tree = ttk.Treeview(win, columns=cols, show="headings")

        for c in cols:
            tree.heading(c, text=c, anchor="center")
            tree.column(c, width=120, anchor="center")

        first = True
        for r in rows:
            if first:
                tree.insert("", "end", values=r)
                first = False
            else:
                tree.insert("", "end", values=("", "", "", "", "", r[5], r[6]))

        tree.pack(fill="both", expand=True)

        if any(r[5] == self.other_symptom.get().strip() for r in rows):
            keyword = self.other_symptom.get().strip()
            if keyword:
                tk.Button(win, text="Search Google",
                    command=lambda:webbrowser.open(
                        "https://www.google.com/search?q="+
                        urllib.parse.quote("ayurvedic remedies for "+keyword)
                    )).pack(pady=4)

            tk.Button(win, text="WHO Traditional Medicine",
                command=lambda:webbrowser.open(WHO_LINK)).pack(pady=4)

        tk.Button(win, text="Save", command=lambda:self.save(rows)).pack(pady=4)
        tk.Button(win, text="Close", command=win.destroy).pack(pady=4)

    def save(self, rows):
        name = self.name_var.get().strip()
        file = f"history_{name}.txt"
        with open(file,"a",encoding="utf-8") as f:
            if not os.path.exists(file):
                f.write("DateTime\tName\tAge\tGender\tWeight\tSymptom\tRemedies\n")
            for r in rows:
                f.write("\t".join(r)+"\n")
            f.write("\n")
        messagebox.showinfo("Saved","History saved successfully")

    def view_history(self):
        name = self.name_var.get().strip()
        file = f"history_{name}.txt"
        if not os.path.exists(file):
            messagebox.showinfo("No History","No saved history")
            return

        win = tk.Toplevel(self.root)
        win.title("History")
        box = tk.Text(win, wrap="none")
        with open(file,"r",encoding="utf-8") as f:
            box.insert("1.0",f.read())
        box.config(state="disabled")
        box.pack(fill="both", expand=True)

# ---------------- MAIN ----------------

if __name__ == "__main__":
    root = tk.Tk()
    StartScreen(root)
    root.mainloop()