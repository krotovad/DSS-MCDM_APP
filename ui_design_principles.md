# UI Design Principles for MCDA Application

## Overview
This document outlines the UI design principles implemented in the main window and how they should be applied consistently across all other windows in the MCDA application.

## Core Design Elements

### 1. Styling System
The application uses a consistent CSS-style stylesheet (`STYLE_SHEET`) that defines:
- **Font**: Segoe UI, Tahoma, sans-serif at 10pt
- **Colors**: Blue (#3498db) as primary color with complementary grays
- **Component styling**: Consistent borders, padding, and hover effects
- **Group boxes**: With rounded corners and subtle borders

### 2. Layout Structure
- **Main layout**: QVBoxLayout for vertical arrangement of components
- **Spacing**: 15px between elements for visual breathing room
- **Margins**: 15px around the entire window for padding
- **Grouping**: QGroupBox to logically organize related controls

### 3. Component Design
- **Input fields**: QLineEdit with rounded borders and focus highlighting
- **Buttons**: Rounded corners with hover and press state changes
- **Tables**: Clean borders with alternating row colors
- **Checkboxes**: Custom-styled with checkmarks

## Main Window Architecture

### Structure
```python
MainWindow (QMainWindow)
├── Menu Bar (File, Help menus)
├── Central Widget (QWidget)
│   └── Main Layout (QVBoxLayout)
│       ├── Input Group Box
│       ├── Methods Group Box
│       ├── Data Table Group Box
│       └── Button Layout (QHBoxLayout)
```

### Key Features
- Title: "MCDA Analysis Tool"
- Size: 1200x800 pixels
- Menu system with standard File and Help options
- Three main sections: Input Parameters, MCDA Methods, Data Table
- Action buttons arranged horizontally at the bottom

## Results Window Architecture

### Structure
```python
ResultsWindow (QWidget)
├── Main Layout (QHBoxLayout)
│   ├── Left Panel: Original Data (QVBoxLayout)
│   │   └── Data Table in Group Box
│   └── Right Panel: Results Tabs (QVBoxLayout)
│       ├── Tab Widget with method-specific results
│       └── Close Button
```

### Key Features
- Title: "Analysis Results"
- Size: 1200x800 pixels
- Split layout: Original data on left, results on right
- Tabbed interface for different method results
- Consistent styling with main window

## Design Principles for All Windows

### 1. Consistent Styling
- All windows must apply the global `STYLE_SHEET`
- Use the same color palette and font specifications
- Maintain consistent component appearance (buttons, inputs, etc.)

### 2. Standardized Layout
- Use QVBoxLayout for primary layout structure
- Maintain 15px spacing and margins throughout
- Group related elements using QGroupBox with proper titles
- Use horizontal layouts only for button groups

### 3. Window Properties
- Set appropriate window title reflecting purpose
- Use reasonable default size (typically 1200x800 for main interfaces)
- Apply consistent window geometry

### 4. Menu Integration
- Standard File menu with Load/Save options
- Help menu with About dialog
- Consistent action naming and placement

### 5. Component Consistency
- Input fields with appropriate labels and placeholders
- Group similar functionality in dedicated sections
- Use tabbed interfaces for organizing multiple related views
- Maintain consistent button placement and labeling

## Implementation Guidelines

### For New Windows
When creating new windows or dialogs:
1. Import the `STYLE_SHEET` from ui_components
2. Follow the standard layout pattern (QVBoxLayout with proper spacing)
3. Use group boxes to organize functionality
4. Apply the same styling approach as existing windows
5. Maintain consistent component sizing and spacing

### Example Template
```python
class NewWindow(QWidget):  # Or QMainWindow as appropriate
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Descriptive Title")
        self.setGeometry(x, y, 1200, 800)  # Adjust position as needed
        
        # Apply consistent styling
        self.setStyleSheet(STYLE_SHEET)
        
        # Use standard layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Add content organized in group boxes
        # ...
        
        self.setLayout(main_layout)
```

## Existing Windows Compliance Status

### ✓ Compliant Windows
- MainWindow: Fully compliant with design principles
- ResultsWindow: Mostly compliant (uses same stylesheet and layout concepts)

### Need Review/Update
- Any custom dialog windows or specialized interfaces

Following these principles ensures a cohesive user experience across the entire application with consistent look, feel, and interaction patterns.