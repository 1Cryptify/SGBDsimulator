import logging
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTabWidget,QHBoxLayout,QComboBox,QListWidget,QLabel
from gui.widgets.input_form_widget import InputFormWidget
from gui.widgets.export_button_widget import ExportButtonWidget
from gui.widgets.status_message_widget import StatusMessageWidget
from gui.widgets.data_table_widget import DataTableWidget
from gui.widgets.confirmation_dialog import ConfirmationDialog
from gui.widgets.loading_spinner import LoadingSpinner
from gui.widgets.notification_banner import NotificationBanner
from gui.widgets.tabbed_interface import TabbedInterface
from gui.widgets.search_bar import SearchBar
from gui.widgets.pagination_control import PaginationControl
from gui.widgets.file_uploader import FileUploader
from gui.widgets.chart_display import ChartDisplay
from gui.widgets.user_profile import UserProfile
from gui.widgets.feedback_form import FeedbackForm
from gui.widgets.help_dialog import HelpDialog
from gui.widgets.notification_settings import NotificationSettings
from utils.settings_manager import SettingsManager
from utils.logging_util import LoggingUtil
from modules.crud_operator import CRUDOperator
from modules.data_viewer import DataViewer
from modules.schema_manager import SchemaManager
from modules.query_executor import QueryExecutor
from modules.database_connector import DatabaseConnector
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SGBD Simulator")
        self.setGeometry(100, 100, 1024, 768)
        
        # Initialize core components with database path
        db_path = "sgbd_simulator.db"
        self.settings_manager = SettingsManager()
        self.logging_util = LoggingUtil()
        self.crud_operator = CRUDOperator(db_path)
        self.query_executor = QueryExecutor(db_path)
        self.schema_manager = SchemaManager(db_path)
        self.data_viewer = DataViewer(db_path)
        
        # Central widget setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Status components
        self.notification_banner = NotificationBanner()
        self.status_message = StatusMessageWidget()
        self.loading_spinner = LoadingSpinner()
        layout.addWidget(self.notification_banner)
        
        # Main tabbed interface
        self.tabs = TabbedInterface()
        layout.addWidget(self.tabs)
        
        # Database Management Tab (Primary)
        db_management = QWidget()
        db_layout = QVBoxLayout(db_management)
        
        # Table List Panel
        table_list_panel = QWidget()
        table_list_layout = QVBoxLayout(table_list_panel)
        
        # Table List Widget
        self.table_list = QListWidget()
        self.table_list.itemClicked.connect(self.handle_table_selection)
        self.refresh_table_list()  # Method to populate the list
        table_list_layout.addWidget(QLabel("Available Tables:"))
        table_list_layout.addWidget(self.table_list)
        
        # CRUD Operations Panel
        crud_panel = QWidget()
        crud_layout = QHBoxLayout(crud_panel)
    
        # Create/Insert Form
        self.insert_form = InputFormWidget()
        self.insert_form.add_field("Table", "text", "Enter table name")
        self.insert_form.add_field("Data", "text", "key1:value1,key2:value2")
        self.insert_form.set_submit_handler(lambda data: self.crud_operator.create(data['Table'], dict(item.split(':') for item in data['Data'].split(','))))
    
        # Update Form
        self.update_form = InputFormWidget()
        self.update_form.add_field("Table", "text", "Enter table name")
        self.update_form.add_field("Data", "text", "key1:value1,key2:value2")
        self.update_form.add_field("Condition", "text", "WHERE clause")
        self.update_form.set_submit_handler(lambda data: self.crud_operator.update(data['Table'], 
            dict(item.split(':') for item in data['Data'].split(',')), 
            data['Condition'], ()))
    
        # Delete Form
        self.delete_form = InputFormWidget()
        self.delete_form.add_field("Table", "text", "Enter table name")
        self.delete_form.add_field("Condition", "text", "WHERE clause")
        self.delete_form.set_submit_handler(lambda data: self.crud_operator.delete(data['Table'], data['Condition'], ()))
    
        crud_layout.addWidget(self.insert_form)
        crud_layout.addWidget(self.update_form)
        crud_layout.addWidget(self.delete_form)
    
        # Schema Operations Panel
        schema_panel = QWidget()
        schema_layout = QHBoxLayout(schema_panel)
    
        # Table Creation Form
        self.create_table_form = InputFormWidget()
        self.create_table_form.add_field("Table Name", "text", "Enter new table name")
        self.create_table_form.add_field("Columns", "text", "name:type,name2:type2")
        self.create_table_form.add_field("Constraints", "text", "PRIMARY KEY(id),...")
        self.create_table_form.set_submit_handler(lambda data: self.schema_manager.create_table(
            data['Table Name'],
            dict(col.split(':') for col in data['Columns'].split(',')),
            data['Constraints'].split(',') if data['Constraints'] else None))
    
        # Column Operations Form
        self.column_ops_form = InputFormWidget()
        self.column_ops_form.add_field("Operation", "text", "add_column/rename_column")
        self.column_ops_form.add_field("Table", "text", "Table name")
        self.column_ops_form.add_field("Column Info", "text", "old_name:new_name or name:type")
        self.column_ops_form.set_submit_handler(self.handle_column_operation)
    
        schema_layout.addWidget(self.create_table_form)
        schema_layout.addWidget(self.column_ops_form)
    
        # Data Display
        self.data_table = DataTableWidget()
        self.search_bar = SearchBar()
        self.search_bar.search_input.textChanged.connect(self.handle_search)
        self.pagination = PaginationControl()
        self.pagination.page_changed.connect(self.load_table_data)
    
        # Layout Assembly
        db_layout.addWidget(table_list_panel)
        db_layout.addWidget(crud_panel)
        db_layout.addWidget(schema_panel)
        db_layout.addWidget(self.search_bar)
        db_layout.addWidget(self.data_table)
        db_layout.addWidget(self.pagination)
        self.tabs.addTab(db_management, "Database Management")
        
        # System Tables Tab
        sys_tables = QWidget()
        sys_layout = QVBoxLayout(sys_tables)
        
        # Buttons for system tables management
        buttons_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_system_tables)
        buttons_layout.addWidget(refresh_btn)
        
        # Combo box to select system table
        self.sys_table_selector = QComboBox()
        self.sys_table_selector.addItems(['sys_tables', 'sys_columns', 'sys_indexes', 'sys_constraints', 'sys_logs'])
        self.sys_table_selector.currentTextChanged.connect(self.load_system_table)
        buttons_layout.addWidget(self.sys_table_selector)
        
        sys_layout.addLayout(buttons_layout)
        
        # Table view for system data
        self.sys_tables_view = DataTableWidget()
        sys_layout.addWidget(self.sys_tables_view)
        
        # Form for editing system tables
        self.sys_table_form = InputFormWidget()
        self.sys_table_form.add_field("Operation", "text", "INSERT/UPDATE/DELETE")
        self.sys_table_form.add_field("Data", "text", "column1:value1,column2:value2")
        self.sys_table_form.add_field("Condition", "text", "WHERE clause (for UPDATE/DELETE)")
        self.sys_table_form.set_submit_handler(self.handle_system_table_operation)
        sys_layout.addWidget(self.sys_table_form)
        
        self.tabs.addTab(sys_tables, "System Tables")        # Query Editor Tab with Logs
        query_widget = QWidget()
        query_layout = QVBoxLayout(query_widget)
        self.query_input = InputFormWidget()
        self.query_input.add_field("SQL Query", "text", "Enter your SQL query here")
        self.query_input.set_submit_handler(self.execute_query)
        self.query_results = DataTableWidget()
        self.query_logs = DataTableWidget()
        query_layout.addWidget(self.query_input)
        query_layout.addWidget(self.query_results)
        query_layout.addWidget(self.query_logs)
        self.tabs.addTab(query_widget, "Query Editor")
        
        # Schema Manager Tab with Metadata
        schema_widget = QWidget()
        schema_layout = QVBoxLayout(schema_widget)
        self.schema_form = InputFormWidget()
        self.schema_form.add_field("Operation", "text", "create_table/alter_table")
        self.schema_form.add_field("Table Name", "text", "Enter table name")
        self.schema_form.add_field("Columns", "text", "column1:type,column2:type")
        self.schema_form.add_field("Constraints", "text", "Optional constraints")
        self.schema_form.set_submit_handler(self.handle_schema_operation)
        self.schema_table = DataTableWidget()
        self.metadata_table = DataTableWidget()
        schema_layout.addWidget(self.schema_form)
        schema_layout.addWidget(self.schema_table)
        schema_layout.addWidget(self.metadata_table)
        self.tabs.addTab(schema_widget, "Schema Manager")
        
        # Data Import/Export Tab
        import_export = QWidget()
        import_layout = QVBoxLayout(import_export)
        self.file_uploader = FileUploader()
        self.chart_display = ChartDisplay()
        self.file_uploader.file_uploaded.connect(self.handle_file_import)
        import_layout.addWidget(self.file_uploader)
        import_layout.addWidget(self.chart_display)
        self.tabs.addTab(import_export, "Import/Export")
        
        # Settings & Profile Tab
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        self.user_profile = UserProfile(self.settings_manager)
        self.notification_settings = NotificationSettings(self.settings_manager)
        settings_layout.addWidget(self.user_profile)
        settings_layout.addWidget(self.notification_settings)
        self.tabs.addTab(settings_widget, "Settings")
        
        # Help & Feedback Tab
        help_widget = QWidget()
        help_layout = QVBoxLayout(help_widget)
        self.help_dialog = HelpDialog()
        self.feedback_form = FeedbackForm()
        help_layout.addWidget(self.help_dialog)
        help_layout.addWidget(self.feedback_form)
        self.tabs.addTab(help_widget, "Help & Feedback")
        
        # Add status message at bottom
        layout.addWidget(self.status_message)
        
        # Initialize confirmation dialog
        self.confirmation_dialog = ConfirmationDialog()

    def handle_search(self):
        search_text = self.search_bar.get_search_text()
        table_conditions = "WHERE table_name LIKE ? OR description LIKE ?"
        params = (f"%{search_text}%", f"%{search_text}%")
        results = self.crud_operator.read("sys_tables", table_conditions, params)
        
        if results:
            # Get column names from first row
            headers = list(results[0].keys())
            self.data_table.set_headers(headers)
            self.data_table.clear()
            
            # Add each row to table
            for row in results:
                row_data = list(row.values())
                self.data_table.add_row(row_data)

    def load_table_data(self, page):
        limit = self.pagination.items_per_page
        offset = (page - 1) * limit
        query = """
            SELECT t.*, COUNT(c.id) as column_count, 
                   (SELECT COUNT(*) FROM sys_constraints WHERE table_id = t.id) as constraint_count
            FROM sys_tables t
            LEFT JOIN sys_columns c ON t.id = c.table_id
            GROUP BY t.id
            LIMIT ? OFFSET ?
        """
        results = self.query_executor.execute_query(query, (limit, offset))
        
        if results:
            # Get column names from query result
            headers = [desc[0] for desc in self.query_executor.get_column_names()]
            self.data_table.set_headers(headers)
            self.data_table.clear()
            
            # Add each row to table
            for row in results:
                self.data_table.add_row(row)

    def execute_query(self):
        form_data = self.query_input.fields["SQL Query"].text()
        try:
            results = self.query_executor.execute_query(form_data)
            
            if results:
                # Set up query results table
                headers = [desc[0] for desc in self.query_executor.get_column_names()]
                self.query_results.set_headers(headers)
                self.query_results.clear()
                for row in results:
                    self.query_results.add_row(row)
            
            # Get and display logs
            log_query = "SELECT operation_timestamp, operation_type, status, message FROM sys_logs ORDER BY operation_timestamp DESC LIMIT 10"
            log_results = self.query_executor.execute_query(log_query)
            
            if log_results:
                self.query_logs.set_headers(["Timestamp", "Operation", "Status", "Message"])
                self.query_logs.clear()
                for log in log_results:
                    self.query_logs.add_row(log)
            
            self.status_message.show_success("Query executed successfully")
        except Exception as e:
            self.status_message.show_error(f"Query error: {str(e)}")

    def handle_schema_operation(self):
        form_data = {
            "operation": self.schema_form.fields["Operation"].text(),
            "table_name": self.schema_form.fields["Table Name"].text(),
            "columns": eval(self.schema_form.fields["Columns"].text()),  # Convert string to dictionary
            "constraints": self.schema_form.fields["Constraints"].text()
        }
        
        try:
            if form_data["operation"] == "create_table":
                self.schema_manager.create_table(
                    form_data["table_name"],
                    form_data["columns"],
                    form_data["constraints"]
                )
                
                metadata_query = """
                    SELECT t.table_name, c.column_name, c.data_type, c.is_nullable,
                           con.constraint_type, con.constraint_definition
                    FROM sys_tables t
                    LEFT JOIN sys_columns c ON t.id = c.table_id
                    LEFT JOIN sys_constraints con ON t.id = con.table_id
                    WHERE t.table_name = ?
                """
                metadata = self.query_executor.execute_query(metadata_query, (form_data["table_name"],))
                
                if metadata:
                    self.metadata_table.set_headers([
                        "Table Name", "Column Name", "Data Type", 
                        "Nullable", "Constraint Type", "Constraint Definition"
                    ])
                    self.metadata_table.clear()
                    for row in metadata:
                        self.metadata_table.add_row(row)
                
            elif form_data["operation"] == "alter_table":
                self.schema_manager.rename_table(
                    form_data["table_name"],
                    form_data["new_name"]
                )
            self.status_message.show_success("Schema operation completed")
            self.schema_form.clear_fields()
        except Exception as e:
            self.status_message.show_error(f"Schema operation error: {str(e)}")

    def handle_file_import(self, file_path):        
        try:
            # Add implementation for file import
            self.status_message.show_success("File imported successfully")
        except Exception as e:
            self.status_message.show_error(f"Import error: {str(e)}")

    def closeEvent(self, event):
        self.crud_operator.close()
        self.query_executor.close()
        self.data_viewer.close()
        event.accept()
    def handle_column_operation(self, form_data):
            try:
                if form_data["operation"] == "add_column":
                    metadata_query = """
                        ALTER TABLE ? ADD COLUMN ? ? 
                        """ + ("NOT NULL" if not form_data["is_nullable"] else "")
                    self.query_executor.execute_query(
                        metadata_query, 
                        (form_data["table_name"], 
                        form_data["column_name"], 
                        form_data["data_type"])
                    )
                    
                    # Update metadata
                    self._update_table_metadata(form_data["table_name"])
                    self._log_operation(
                        "ALTER", 
                        form_data["table_name"], 
                        f"Added column: {form_data['column_name']}"
                    )
                    
                elif form_data["operation"] == "drop_column":
                    metadata_query = "ALTER TABLE ? DROP COLUMN ?"
                    self.query_executor.execute_query(
                        metadata_query,
                        (form_data["table_name"], form_data["column_name"])
                    )
                    
                    # Update metadata
                    self._update_table_metadata(form_data["table_name"])
                    self._log_operation(
                        "ALTER", 
                        form_data["table_name"], 
                        f"Dropped column: {form_data['column_name']}"
                    )
                    
                elif form_data["operation"] == "modify_column":
                    metadata_query = """
                        ALTER TABLE ? MODIFY COLUMN ? ? 
                        """ + ("NOT NULL" if not form_data["is_nullable"] else "")
                    self.query_executor.execute_query(
                        metadata_query,
                        (form_data["table_name"], 
                        form_data["column_name"], 
                        form_data["new_data_type"])
                    )
                    
                    # Update metadata
                    self._update_table_metadata(form_data["table_name"])
                    self._log_operation(
                        "ALTER", 
                        form_data["table_name"], 
                        f"Modified column: {form_data['column_name']}"
                    )
                    
                self.status_message.show_success("Column operation completed successfully")
                self.schema_form.clear_fields()
                
            except Exception as e:
                self.status_message.show_error(f"Column operation error: {str(e)}")
                logging.error(f"Column operation failed: {str(e)}")
    def refresh_system_tables(self):
            """Rafraîchit l'affichage de la table système sélectionnée"""
            current_table = self.sys_table_selector.currentText()
            self.load_system_table(current_table)
    
    def load_system_table(self, table_name):
        """Charge les données d'une table système dans la vue"""
        try:
            results = self.crud_operator.read(table_name)
            if results:
                self.sys_tables_view.set_data(results)
                self.status_message.show_success(f"Loaded {table_name} successfully")
            else:
                self.sys_tables_view.clear()
                self.status_message.show_info(f"No data in {table_name}")
        except Exception as e:
            self.status_message.show_error(f"Error loading {table_name}: {str(e)}")
            logging.error(f"Failed to load system table {table_name}: {str(e)}")

    def handle_system_table_operation(self, form_data):
        """Gère les opérations CRUD sur les tables système"""
        try:
            table_name = self.sys_table_selector.currentText()
            operation = form_data["Operation"].upper()
            
            if operation == "INSERT":
                # Parse data string into dictionary
                data_dict = dict(item.split(":") for item in form_data["Data"].split(","))
                self.crud_operator.create(table_name, data_dict)
                
            elif operation == "UPDATE":
                # Parse data and conditions
                data_dict = dict(item.split(":") for item in form_data["Data"].split(","))
                conditions = form_data["Condition"]
                self.crud_operator.update(table_name, data_dict, conditions, ())
                
            elif operation == "DELETE":
                conditions = form_data["Condition"]
                self.crud_operator.delete(table_name, conditions, ())
                
            else:
                raise ValueError(f"Invalid operation: {operation}")
            
            self.status_message.show_success(f"{operation} operation completed successfully")
            self.refresh_system_tables()
            self.sys_table_form.clear_fields()
            
        except Exception as e:
            self.status_message.show_error(f"System table operation error: {str(e)}")
            logging.error(f"System table operation failed: {str(e)}")
    def handle_table_selection(self, item):
            """Handles the selection of a table from the table list"""
            try:
                table_name = item.text()
                # Get table data
                results = self.crud_operator.read(table_name)
                
                if results:
                    # Get column names from first row
                    headers = list(results[0].keys())
                    self.data_table.set_headers(headers)
                    self.data_table.clear()
                    
                    # Add each row to table
                    for row in results:
                        self.data_table.add_row(list(row.values()))
                    
                    # Update forms with selected table
                    self.insert_form.fields["Table"].setText(table_name)
                    self.update_form.fields["Table"].setText(table_name)
                    self.delete_form.fields["Table"].setText(table_name)
                    
                    # Show success message
                    self.status_message.show_success(f"Loaded table {table_name} successfully")
                else:
                    self.data_table.clear()
                    self.status_message.show_info(f"No data in table {table_name}")
                    
            except Exception as e:
                self.status_message.show_error(f"Error loading table: {str(e)}")
                logging.error(f"Failed to load table {table_name}: {str(e)}")
    
    def refresh_table_list(self):
            """Refreshes the list of available tables"""
            try:
                # Query to get all user tables
                results = self.query_executor.execute_query(
                    "SELECT table_name FROM sys_tables WHERE table_type = 'USER'"
                )
                
                # Clear existing items
                self.table_list.clear()
                
                # Add tables to list widget
                if results:
                    for row in results:
                        self.table_list.addItem(row[0])
                    self.status_message.show_success("Table list refreshed successfully")
                else:
                    self.status_message.show_info("No tables found")
                    
            except Exception as e:
                self.status_message.show_error(f"Error refreshing table list: {str(e)}")
                logging.error(f"Failed to refresh table list: {str(e)}")

    def _update_table_metadata(self, table_name):
        """Updates the metadata display for a given table"""
        try:
            metadata_query = """
                SELECT column_name, data_type, is_nullable, 
                    column_default, character_maximum_length
                FROM sys_columns 
                WHERE table_name = ?
                ORDER BY ordinal_position
            """
            metadata = self.query_executor.execute_query(metadata_query, (table_name,))
            
            if metadata:
                self.metadata_table.set_headers([
                    "Column Name", "Data Type", "Nullable",
                    "Default Value", "Max Length"
                ])
                self.metadata_table.clear()
                for row in metadata:
                    self.metadata_table.add_row(row)
                    
        except Exception as e:
            logging.error(f"Failed to update metadata for table {table_name}: {str(e)}")

    def _log_operation(self, operation_type, table_name, message):
        """Logs database operations to sys_logs table"""
        try:
            log_query = """
                INSERT INTO sys_logs 
                (operation_timestamp, operation_type, table_name, status, message)
                VALUES (CURRENT_TIMESTAMP, ?, ?, 'SUCCESS', ?)
            """
            self.query_executor.execute_query(log_query, (operation_type, table_name, message))
            
        except Exception as e:
            logging.error(f"Failed to log operation: {str(e)}")
