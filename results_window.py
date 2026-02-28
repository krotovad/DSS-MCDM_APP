"""
Results Window module
Contains the ResultsWindow class for displaying MCDA analysis results with enhanced visualization
"""

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from visualization import (
    PlotCanvas, 
    create_ranking_chart, 
    create_comparison_chart, 
    create_weights_visualization, 
    create_performance_spider_chart,
    create_scatter_plot_2d,
    create_heatmap,
    create_parallel_coordinates
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ResultsWindow(QMainWindow):
    """Window to display analysis results with enhanced visualization, designed as a proper window with menu bar and status bar"""
    
    def __init__(self, data, methods, inputs, results, parent=None):
        super(ResultsWindow, self).__init__(parent)
        
        self.data = data
        self.methods = methods
        self.inputs = inputs
        self.results = results
        
        self.initUI()
        
    def initUI(self):
        """Initialize the results window UI"""
        self.setWindowTitle("Analysis Results with Visualization")
        self.setGeometry(150, 150, 1400, 900)
        
        # Apply the same styling as the main window
        from ui_components import STYLE_SHEET
        self.setStyleSheet(STYLE_SHEET)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        save_action = QAction('Save Report', self)
        save_action.triggered.connect(self.save_report)
        file_menu.addAction(save_action)
        
        close_action = QAction('Close', self)
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Status bar
        self.statusBar().showMessage('Analysis Results Loaded')
        
        # Left side: Navigation panel
        nav_layout = QVBoxLayout()
        
        # Create navigation buttons for different views
        self.nav_buttons = {}
        
        nav_group = QGroupBox("Navigation")
        nav_group_layout = QVBoxLayout(nav_group)
        
        views = [
            ("Data", "Original Data"),
            ("Results", "Method Results"),
            ("Charts", "Visualizations"),
            ("Comparison", "Method Comparison")
        ]
        
        for key, label in views:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, k=key: self.switch_view(k))
            self.nav_buttons[key] = btn
            nav_group_layout.addWidget(btn)
        
        # Initially check the first button
        self.nav_buttons["Data"].setChecked(True)
        nav_layout.addWidget(nav_group)
        
        # Add stretch to fill remaining space
        nav_layout.addStretch()
        
        # Right side: Content area
        right_layout = QVBoxLayout()
        
        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Create each view
        self.data_view = self.create_data_view()
        self.results_view = self.create_results_view()
        self.charts_view = self.create_charts_view()
        self.comparison_view = self.create_comparison_view()
        
        self.stacked_widget.addWidget(self.data_view)  # Index 0
        self.stacked_widget.addWidget(self.results_view)  # Index 1
        self.stacked_widget.addWidget(self.charts_view)  # Index 2
        self.stacked_widget.addWidget(self.comparison_view)  # Index 3
        
        right_layout.addWidget(self.stacked_widget)
        
        # Buttons - moved to separate group
        button_group = QGroupBox("Actions")
        button_layout = QHBoxLayout(button_group)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        save_btn = QPushButton("Save Report")
        save_btn.clicked.connect(self.save_report)
        button_layout.addWidget(save_btn)
        
        right_layout.addWidget(button_group)
        
        # Combine layouts
        main_layout.addLayout(nav_layout, 1)
        main_layout.addLayout(right_layout, 4)
        
        self.setLayout(main_layout)
        
        # Initialize with data view
        self.current_view = "Data"
        
    def switch_view(self, view_name):
        """Switch between different views"""
        # Uncheck all buttons
        for key, btn in self.nav_buttons.items():
            btn.setChecked(False)
        
        # Check the selected button
        self.nav_buttons[view_name].setChecked(True)
        
        # Switch to the corresponding widget
        if view_name == "Data":
            self.stacked_widget.setCurrentIndex(0)
        elif view_name == "Results":
            self.stacked_widget.setCurrentIndex(1)
        elif view_name == "Charts":
            self.stacked_widget.setCurrentIndex(2)
        elif view_name == "Comparison":
            self.stacked_widget.setCurrentIndex(3)
            
        self.current_view = view_name
    
    def create_data_view(self):
        """Create the data view"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        data_group = QGroupBox("Original Data")
        data_layout = QVBoxLayout(data_group)
        
        self.data_table = QTableWidget()
        self.data_table.setRowCount(len(self.data))
        self.data_table.setColumnCount(len(self.data[0]) if self.data else 0)
        self.data_table.setHorizontalHeaderLabels([f"Criterion {i+1}" for i in range(len(self.data[0]) if self.data else 0)])
        
        for i, row in enumerate(self.data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                self.data_table.setItem(i, j, item)
        
        data_layout.addWidget(self.data_table)
        layout.addWidget(data_group)
        
        # Add weights information
        weights_group = QGroupBox("Weights Information")
        weights_layout = QVBoxLayout(weights_group)
        
        weights_text = QTextEdit()
        weights_text.setPlainText(f"Weights: {self.inputs}")
        weights_text.setMaximumHeight(60)
        weights_text.setReadOnly(True)
        weights_layout.addWidget(weights_text)
        
        layout.addWidget(weights_group)
        
        # Add 3D visualization
        viz_group = QGroupBox("3D Visualization")
        viz_layout = QVBoxLayout(viz_group)
        
        self.plot_canvas = PlotCanvas()
        self.plot_canvas.plot(self.data)
        viz_layout.addWidget(self.plot_canvas)
        
        layout.addWidget(viz_group)
        
        return widget
    
    def create_results_view(self):
        """Create the results view"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create a tab widget for each method's results
        tabs = QTabWidget()
        
        for method in self.methods:
            if method in self.results:
                tab = QWidget()
                tab_layout = QVBoxLayout(tab)
                
                results_table = QTableWidget()
                
                # Set up the table based on results
                if isinstance(self.results[method], list) and self.results[method]:
                    if isinstance(self.results[method][0], (list, tuple)):
                        # Results are in table format
                        rows = len(self.results[method])
                        cols = len(self.results[method][0])
                        results_table.setRowCount(rows)
                        results_table.setColumnCount(cols)
                        
                        for i, row in enumerate(self.results[method]):
                            for j, val in enumerate(row):
                                item = QTableWidgetItem(str(val))
                                results_table.setItem(i, j, item)
                    else:
                        # Results are in single column format (rankings)
                        results_table.setRowCount(len(self.results[method]))
                        results_table.setColumnCount(2)
                        results_table.setHorizontalHeaderLabels(["Alternative", "Rank"])
                        
                        for i, val in enumerate(self.results[method]):
                            alt_item = QTableWidgetItem(f"A{i+1}")
                            rank_item = QTableWidgetItem(str(val + 1))  # Convert to 1-indexed rank
                            results_table.setItem(i, 0, alt_item)
                            results_table.setItem(i, 1, rank_item)
                
                tab_layout.addWidget(results_table)
                tabs.addTab(tab, method)
        
        layout.addWidget(tabs)
        return widget
    
    def create_charts_view(self):
        """Create the charts view"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create tabs for different chart types
        tabs = QTabWidget()
        
        # Add ranking charts for each method
        for method in self.methods:
            if method in self.results and isinstance(self.results[method], list) and self.results[method]:
                # Create a tab with scroll area for the chart
                tab = QWidget()
                tab_layout = QVBoxLayout(tab)
                
                # Create the ranking chart
                fig = create_ranking_chart(self.results[method], method)
                canvas = FigureCanvas(fig)
                
                # Add to scroll area
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll_content = QWidget()
                scroll_layout = QVBoxLayout(scroll_content)
                scroll_layout.addWidget(canvas)
                scroll.setWidget(scroll_content)
                
                tab_layout.addWidget(scroll)
                tabs.addTab(tab, method)
        
        # Add comparison chart
        if len(self.results) > 1:
            comparison_tab = QWidget()
            comparison_layout = QVBoxLayout(comparison_tab)
            
            fig = create_comparison_chart(self.results)
            canvas = FigureCanvas(fig)
            
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.addWidget(canvas)
            scroll.setWidget(scroll_content)
            
            comparison_layout.addWidget(scroll)
            tabs.addTab(comparison_tab, "Method Comparison")
        
        # Add advanced visualization charts
        # 2D Scatter Plot Tab
        scatter_tab = QWidget()
        scatter_layout = QVBoxLayout(scatter_tab)
        
        fig = create_scatter_plot_2d(self.data, 0, 1, "2D Scatter Plot: Criterion 1 vs Criterion 2")
        canvas = FigureCanvas(fig)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout_2d = QVBoxLayout(scroll_content)
        scroll_layout_2d.addWidget(canvas)
        scroll.setWidget(scroll_content)
        
        scatter_layout.addWidget(scroll)
        tabs.addTab(scatter_tab, "2D Scatter Plot")
        
        # Heatmap Tab
        heatmap_tab = QWidget()
        heatmap_layout = QVBoxLayout(heatmap_tab)
        
        fig = create_heatmap(self.data, "Heatmap of Criteria Values")
        canvas = FigureCanvas(fig)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout_hm = QVBoxLayout(scroll_content)
        scroll_layout_hm.addWidget(canvas)
        scroll.setWidget(scroll_content)
        
        heatmap_layout.addWidget(scroll)
        tabs.addTab(heatmap_tab, "Heatmap")
        
        # Parallel Coordinates Tab
        par_coord_tab = QWidget()
        par_coord_layout = QVBoxLayout(par_coord_tab)
        
        fig = create_parallel_coordinates(self.data, "All Methods", [f"C{i+1}" for i in range(len(self.data[0]) if self.data else 0)])
        canvas = FigureCanvas(fig)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout_pc = QVBoxLayout(scroll_content)
        scroll_layout_pc.addWidget(canvas)
        scroll.setWidget(scroll_content)
        
        par_coord_layout.addWidget(scroll)
        tabs.addTab(par_coord_tab, "Parallel Coordinates")
        
        # Spider Chart Tab (using first method for example)
        if self.methods:
            spider_tab = QWidget()
            spider_layout = QVBoxLayout(spider_tab)
            
            # Using the original data for spider chart visualization
            # This would normally use the results of a specific method
            fig = create_performance_spider_chart(self.data, self.methods[0], [f"C{i+1}" for i in range(len(self.data[0]) if self.data else 0)])
            canvas = FigureCanvas(fig)
            
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll_content = QWidget()
            scroll_layout_sp = QVBoxLayout(scroll_content)
            scroll_layout_sp.addWidget(canvas)
            scroll.setWidget(scroll_content)
            
            spider_layout.addWidget(scroll)
            tabs.addTab(spider_tab, "Spider Chart")
        
        layout.addWidget(tabs)
        return widget
    
    def create_comparison_view(self):
        """Create the comparison view"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        comparison_group = QGroupBox("Methods Comparison")
        comparison_layout = QVBoxLayout(comparison_group)
        
        # Create a table comparing results from different methods
        comparison_table = QTableWidget()
        
        if self.results:
            methods_list = list(self.results.keys())
            n_alternatives = len(self.results[methods_list[0]]) if methods_list else 0
            
            comparison_table.setColumnCount(len(methods_list) + 1)  # +1 for alternative labels
            comparison_table.setRowCount(n_alternatives)
            
            # Set headers
            headers = ["Alternative"] + methods_list
            comparison_table.setHorizontalHeaderLabels(headers)
            
            # Fill the table
            for i in range(n_alternatives):
                # Set alternative label
                alt_item = QTableWidgetItem(f"A{i+1}")
                comparison_table.setItem(i, 0, alt_item)
                
                # Set results for each method
                for j, method in enumerate(methods_list):
                    if i < len(self.results[method]):
                        rank = self.results[method][i] + 1  # Convert to 1-indexed
                        item = QTableWidgetItem(str(rank))
                        comparison_table.setItem(i, j + 1, item)
        
        comparison_layout.addWidget(comparison_table)
        layout.addWidget(comparison_group)
        
        # Add visualization comparing all methods
        viz_group = QGroupBox("Comparison Visualization")
        viz_layout = QVBoxLayout(viz_group)
        
        fig = create_comparison_chart(self.results)
        canvas = FigureCanvas(fig)
        viz_layout.addWidget(canvas)
        
        layout.addWidget(viz_group)
        
        return widget
    
    def save_report(self):
        """Save a report of the analysis"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Analysis Report", "", 
            "PDF Files (*.pdf);;HTML Files (*.html);;All Files (*)", 
            options=options
        )
        
        if file_path:
            # In a real implementation, this would generate a comprehensive report
            # For now, just show a message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Report generation functionality would be implemented here.")
            msg.setInformativeText(f"Report would be saved to: {file_path}")
            msg.setWindowTitle("Report Generation")
            msg.exec_()


    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", "MCDA Analysis Tool - Results Window\nVersion 1.0")


if __name__ == "__main__":
    # Example usage
    app = QApplication(sys.argv)
    
    # Sample data for testing
    sample_data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    sample_methods = ['TOPSIS', 'WSR']
    sample_inputs = [0.3, 0.5, 0.2]
    sample_results = {
        'TOPSIS': [2, 0, 1],
        'WSR': [2, 0, 1]
    }
    
    window = ResultsWindow(sample_data, sample_methods, sample_inputs, sample_results)
    window.show()
    
    sys.exit(app.exec_())