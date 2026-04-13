# UI Architecture Documentation

## Overview
This document describes the current UI architecture of the productivity tracker application, focusing on the timer functionality and dynamic work/break time sessions, as well as JIRA integration.

## Current Architecture

### Main Components

1. **App.tsx** - Main application component that manages:
   - Overall application state
   - Timer logic and state management
   - Task list management
   - User authentication state
   - Time tracking state (currentTrackingTask, activeTimeSession, elapsedTime, etc.)
   - 60-minute session state management (work/break periods)
   - JIRA import/export state

2. **TaskList.tsx** - Displays tasks with:
   - Task information (title, description, priority, estimated time)
   - Timer buttons (Start/Stop)
   - Delete buttons
   - Edit buttons
   - Edit form for task details (title, description, priority, estimated minutes)
   - Visual indicators for active timers
   - Session type indicators
   - JIRA export buttons

3. **TimerDisplay.tsx** - Displays timer information:
   - Current timer value in MM:SS or HH:MM:SS format
   - Break time display
   - Active timer status

### State Management

#### App.tsx State Variables:
- `tasks`: Array of task objects
- `timeSpent`: Total time spent on all tasks (minutes)
- `currentUser`: Current logged-in user
- `isLoggedIn`: Authentication status
- `elapsedTime`: Current elapsed time in seconds
- `timerInterval`: Timer interval reference
- `currentTrackingTask`: ID of task currently being tracked
- `activeTimeSession`: ID of active time session
- `timeTracking`: Object mapping task IDs to time spent
- `active60MinSession`: Object mapping task IDs to active session IDs
- `taskSessionStates`: Object mapping task IDs to session state (isWorkPeriod, timeLeft)
- `workTime`: Configurable work time in minutes (default 45)
- `breakTime`: Configurable break time in minutes (default 15)
- `activeTimerType`: Type of active timer ('manual' or 'session')
- `confirmationModal`: State for managing confirmation modal display
- `jiraExportModal`: State for managing JIRA export modal
- `jiraImportModal`: State for managing JIRA import modal

### Timer Flow

1. **Start Timer**:
   - User clicks "Start Timer" button on a task
   - Calls `startTimer` function which:
     - Stops any currently active timer
     - Creates a new time session in the database
     - Sets `currentTrackingTask` to the task ID
     - Starts the timer

2. **Stop Timer**:
   - User clicks "Stop Timer" button
   - Calls `stopTimer` function which:
     - Updates the active time session with end time
     - Clears the active timer state
     - Resets timer display

3. **Start 60-Minute Session**:
   - User clicks "Start 60min Session" button on a task
   - Calls `start60MinSession` function which:
     - Stops any existing manual timer
     - Stops any active 60-minute session for any task
     - Creates a new time session in the database
     - Sets up session state with work period countdown
     - Starts the 60-minute session timer

4. **Stop 60-Minute Session**:
   - User clicks "Stop Session" button during active session
   - Calls `stop60MinSession` function which:
     - Updates the active time session with end time
     - Clears the session state
     - Stops the session timer

5. **Edit Task**:
   - User clicks "Edit" button on a task
   - Task enters edit mode with editable fields (title, description, priority, estimated minutes)
   - User modifies task details in the edit form
   - User clicks "Save" to save changes or "Cancel" to discard changes
   - Calls `onUpdateTask` function with task ID and updated data
   - Updates task in the UI and makes API call to backend

6. **Delete Task with Confirmation**:
   - User clicks "Delete" button on a task
   - Sets `confirmationModal` state to show confirmation dialog
   - User confirms deletion or cancels
   - Calls appropriate delete function or closes modal

## Current Timer Implementation Details

### Timer Logic:
- Timer counts up in HH:MM:SS format for manual timers
- Uses `setInterval` to update every second
- Tracks time in seconds and formats to display format
- Only one timer can be active at a time
- 60-minute sessions use a different timer logic with work/break periods
- Session timer uses a single interval that manages multiple tasks

### UI Components:
- Timer display shows current elapsed time
- Task list buttons toggle between Start/Stop states
- Active timer is visually indicated
- Session type indicators show work/break periods
- Session settings allow dynamic work/break time configuration

## Dynamic Work/Break Time Session Feature

### Current Implementation:
1. **Configurable Time Periods**:
   - Work time: 1-99 minutes (default 45)
   - Break time: 1-99 minutes (default 15)
   - Configurable through session settings UI

2. **Session Flow**:
   - Start 60min Session button (now dynamic based on workTime/breakTime)
   - Countdown from workTime to 00:00 (work period)
   - Countdown from breakTime to 00:00 (break period)
   - Automatic transition between work and break periods
   - Session state management for each task

3. **Database Integration**:
   - Session data saved to database with:
     - Start time
     - End time (when work period ends)
     - Session type (work/break period)
   - Automatic saving when work period ends
   - Manual saving when session is explicitly stopped

4. **Button Behavior**:
   - "Start {workTime}min Session" during idle periods
   - "Stop Session" during active work period
   - "Stop Break Session" during active break period
   - Automatic button text updates based on session state

### State Variables:
- `active60MinSession`: Object mapping task IDs to active session IDs
- `taskSessionStates`: Object mapping task IDs to session state (isWorkPeriod, timeLeft)
- `workTime`: Configurable work time in minutes (1-99)
- `breakTime`: Configurable break time in minutes (1-99)
- `activeTimerType`: Type of active timer ('manual' or 'session')

### Component Updates:
- TaskList.tsx: Displays dynamic session buttons based on work/break times
- App.tsx: Implements dynamic 60-minute session logic with configurable times
- Session settings UI: Allows configuration of workTime and breakTime

## JIRA Integration

### JIRA Export Functionality:
1. **Export Process**:
   - User clicks "Export to JIRA" button
   - Calls `exportToJira` function which:
     - Gathers all tasks and time sessions for the current user
     - Formats data in JIRA-compatible JSON structure
     - Opens download dialog for JSON file
     - Provides option to save or copy JSON

2. **Export Data Structure**:
   - Task data with title, description, priority, estimated time
   - Time session data with start/end times, duration
   - Proper JSON formatting for JIRA import

### JIRA Import Functionality:
1. **Import Process**:
   - User clicks "Import from JIRA" button
   - Opens file selection dialog for JSON file
   - Validates JSON structure
   - Processes data and creates/updates tasks and time sessions
   - Provides import status feedback

### UI Components for JIRA:
- JIRA export button in task list or user menu
- JIRA import button in user menu or settings
- Export confirmation modal
- Import file selection dialog
- Import status indicators

## Testing Instructions

### Manual Testing Steps:

1. **Timer Functionality Testing**:
   - Create a new task
   - Click "Start Timer" on the task
   - Verify timer starts counting up in HH:MM:SS format
   - Click "Stop Timer" 
   - Verify timer stops and time is recorded
   - Verify time appears in task list

2. **Confirmation Modal Testing**:
   - Click "Delete" button on any task
   - Verify confirmation modal appears with proper styling
   - Click "Cancel" and verify modal closes
   - Click "Delete" and verify task is removed from list
   - Verify modal closes after deletion

3. **60-Minute Session Testing**:
   - Configure work time to 1 minute and break time to 1 minute for testing
   - Start a 60-minute session
   - Verify session timer counts down
   - Verify automatic transition between work/break periods
   - Verify session state updates correctly
   - Stop session and verify data persistence

4. **Database Integration Testing**:
   - Verify time sessions are created in database when timers start
   - Verify time sessions are updated with end times when timers stop
   - Verify time calculations are accurate
   - Verify data persistence across application restarts

5. **JIRA Integration Testing**:
   - Test export functionality by exporting data
   - Verify exported JSON structure is valid
   - Test import functionality with sample JSON
   - Verify imported data appears correctly in application
