import tkinter as tk
from app.gui.main_gui import APUEngineGUI

def main():
    root = tk.Tk()
    app = APUEngineGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
