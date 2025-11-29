# Proposal: Add Tabbed Interface to Main Window

## Overview
Refactor the main window to use a tabbed interface (ttk.Notebook) instead of a single-view layout. This provides an extensible framework for organizing different views (transactions, visualizations, metrics, settings, etc.) and improves the user experience by allowing seamless navigation between features.

## Motivation
The current single-view main window displays only the transaction table. As new features are added (visualizations, analytics, settings), the UI needs a scalable organization pattern. A tabbed interface:
- Provides clear separation of concerns between different views
- Allows users to switch contexts without opening/closing dialogs
- Is a familiar and intuitive pattern used in many applications
- Enables easy addition of future tabs without cluttering the UI
- Maintains state across tab switches (page number, filters, etc.)

## Scope
This change refactors the main window architecture without modifying transaction functionality:

**In Scope:**
- Refactor MainWindow to use ttk.Notebook (tabbed interface)
- Create new "Transactions" tab containing all existing transaction table functionality
- Extract transaction table logic into TransactionsTab component (expense_tracker/gui/tabs/transactions_tab.py)
- Create tabs/ directory structure for future tab components
- Lazy loading pattern: tabs refresh when activated
- Preserve all existing functionality (search, add, edit, delete, pagination, import)
- Modal dialogs (Add, Edit, Upload) continue to work from Transactions tab

**Out of Scope:**
- New features or tabs beyond the refactored Transactions tab
- Changes to transaction data model or database schema
- Modifications to dialog behavior or styling
- Performance optimizations beyond lazy loading

## User Impact
- **No Functional Changes**: All existing features work identically
- **UI Pattern Change**: Main window now has a tab bar (initially with one tab: "Transactions")
- **No Breaking Changes**: Existing workflows preserved
- **Foundation for Growth**: Easy to add new tabs in future without refactoring
- **Performance**: Minimal impact - lazy loading ensures tabs only refresh when viewed

## Dependencies
- Uses ttk.Notebook widget (standard in tkinter.ttk, no new dependencies)
- No external library changes required
- No database migrations needed
- Requires code reorganization but no API changes

## Success Criteria
1. Main window displays a tab bar with "Transactions" tab
2. Transactions tab contains all existing functionality (search, add, edit, delete, pagination, import)
3. All existing features work identically to the original single-view design
4. Modal dialogs (Add Transaction, Edit Transaction, Upload) open and function correctly
5. Search and pagination state is preserved across application sessions
6. Tab framework is ready for future tabs to be added
7. All existing tests pass without modification (no regression)
8. Performance is identical or better than original single-view design

## Alternatives Considered
1. **Keep single-view, add dialogs for new features**: Rejected because dialogs disrupt workflow and don't scale well for multiple features
2. **Side-by-side panels**: Rejected due to screen space constraints and responsive layout complexity
3. **Separate windows for each feature**: Rejected because managing multiple windows is cumbersome
4. **Dropdown menu navigation**: Rejected because tabs provide better visual indication of current context

## Implementation Strategy
This is a pure refactoring task with minimal risk:
1. Create new TransactionsTab class by extracting code from MainWindow
2. Update MainWindow to create Notebook and add TransactionsTab
3. Verify all functionality still works
4. Update tests if needed (import path changes only)

No new features are added - this is purely architectural preparation for future enhancements.

## Open Questions
None - this is a straightforward refactoring with clear requirements.
