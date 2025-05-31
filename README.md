# OBSM: Oblivion Spell Maker

**OBSM** is a custom spell creation tool inspired by *The Elder Scrolls IV: Oblivion*. It allows users to design and calculate custom spells based on in-game mechanics, providing a user-friendly interface for spell crafting.

## Features

* **Spell Creation Interface**: Design custom spells with multiple effects.
* **Effect Management**: Add, edit, and remove spell effects.
* **Cost Calculation**: Automatically computes the magicka cost of spells based on selected effects and character skills.
* **Data Integration**: Utilizes an Excel file (`obsm_effs.xlsx`) containing spell effect data for accurate calculations.
* **GUI Application**: Provides a graphical user interface for ease of use.

---------------------

## Running the Spell Maker

A standalone Windows executable can be found in the releases page: https://github.com/fcgary/OBSM/releases

---------------------

## How does spell making work?
See the UESP's article on spell making: https://en.uesp.net/wiki/Oblivion:Spell_Making

---------------------
## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

## Installation (From Source)

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/fcgary/OBSM.git
   cd OBSM
   ```

2. **(Optional) Set Up a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:

   ```bash
   python tool/obsm_gui.py
   ```


### To Build the Executable:

1. **Install PyInstaller**:

   ```bash
   pip install pyinstaller
   ```

2. **Build with Icon Support**:

   ```bash
   pyinstaller --onefile --icon=path/to/icon.ico tool/obsm_gui.py
   ```

   Replace `path/to/icon.ico` with your `.ico` file path. The built `.exe` will appear in the `dist` directory.

## File Structure

```
OBSM/
│
├── tool/
│   ├── obsm_gui.py          # GUI application
│   └── obsm_calculator.py   # Spell logic
│
├── data/
│   └── obsm_effs.xlsx       # Effect data
│
├── dist/
│   └── obsm.exe             # Compiled executable (after build)
│
├── requirements.txt
└── README.md
```
