# tabbed-interface Specification

## Purpose
Provide a tabbed interface in the main window to organize different views and enable future feature additions without UI clutter.

## ADDED Requirements

### Requirement: Tabbed Main Window
The system SHALL use a tabbed interface (ttk.Notebook) in the main window to organize views.

#### Scenario: Display tab bar on startup
- **WHEN** application launches
- **THEN** main window displays a tab bar with one tab: "Transactions"
- **AND** "Transactions" tab is selected by default
- **AND** tab bar uses ttk.Notebook widget
- **AND** tab bar is visible at the top of the main window

#### Scenario: Tab contains transaction table
- **WHEN** user views the "Transactions" tab
- **THEN** tab displays the transaction table (Treeview)
- **AND** toolbar with all buttons is visible (Add, Edit, Delete, Refresh, Import, Search, Clear Search)
- **AND** pagination footer is visible with Previous/Next buttons and page indicator
- **AND** layout is identical to the original single-view design

### Requirement: Preserve All Existing Functionality
The system SHALL maintain all existing transaction management features without regression.

#### Scenario: Add transaction from tab
- **WHEN** user clicks "Add Transaction" button in Transactions tab
- **THEN** Add Transaction dialog opens as a modal window
- **AND** dialog behavior is identical to original implementation
- **WHEN** user completes or cancels the dialog
- **THEN** dialog closes and Transactions tab refreshes to show updated data

#### Scenario: Edit transaction from tab
- **WHEN** user selects a transaction and clicks "Edit Transaction"
- **THEN** Edit Transaction dialog opens with selected transaction data
- **AND** user can modify transaction details
- **WHEN** user saves changes
- **THEN** transaction is updated in database and tab refreshes

#### Scenario: Delete transaction from tab
- **WHEN** user selects a transaction and clicks "Delete Transaction"
- **THEN** confirmation dialog appears
- **WHEN** user confirms deletion
- **THEN** transaction is deleted and tab refreshes

#### Scenario: Search transactions in tab
- **WHEN** user enters a keyword in search field and clicks Search
- **THEN** transaction table filters to show only matching transactions
- **AND** search indicator displays the keyword
- **AND** pagination works with filtered results

#### Scenario: Navigate pages in tab
- **WHEN** user clicks "Next" or "Previous" pagination buttons
- **THEN** transaction table updates to show the next/previous page
- **AND** page indicator updates (e.g., "Page 2 of 10")
- **AND** pagination state is preserved when switching to other tabs (future)

#### Scenario: Import statement from tab
- **WHEN** user clicks "Import Statement" button
- **THEN** Upload dialog opens
- **WHEN** user selects a PDF and imports transactions
- **THEN** transactions are added to database and tab refreshes

### Requirement: Modal Dialog Management
The system SHALL continue to manage modal dialogs (Add, Edit, Upload) from the Transactions tab.

#### Scenario: Single active dialog
- **WHEN** a dialog is already open (Add, Edit, or Upload)
- **AND** user clicks another button that would open a dialog
- **THEN** existing dialog is brought to front and focused
- **AND** no new dialog is created

#### Scenario: Dialog refresh behavior
- **WHEN** user closes a dialog (via Save, Cancel, or X button)
- **THEN** Transactions tab automatically refreshes to show latest data
- **AND** no manual refresh is required

### Requirement: Extensibility for Future Tabs
The system SHALL provide a framework for adding new tabs without modifying core MainWindow logic.

#### Scenario: Tab framework is reusable
- **WHEN** a new tab component is created (e.g., HeatmapTab)
- **THEN** it can inherit from tk.Frame
- **AND** it can be added to the notebook with `notebook.add(tab, text="TabName")`
- **AND** it can implement its own `refresh()` method for lazy loading
- **AND** it can access transaction_repo and other dependencies via constructor

### Requirement: Visual Consistency
The system SHALL maintain visual appearance and theme compatibility.

#### Scenario: Theme compatibility
- **WHEN** application uses ttkbootstrap "darkly" theme
- **THEN** tab bar and tab content use the theme correctly
- **AND** tab selection highlighting is visible
- **AND** all widgets render correctly within tabs

#### Scenario: Window resize behavior
- **WHEN** user resizes the main window
- **THEN** tab bar and tab content resize proportionally
- **AND** transaction table expands/contracts to fill available space
- **AND** no layout issues or widget clipping occurs
