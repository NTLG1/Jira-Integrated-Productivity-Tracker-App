import React, { useState, useEffect } from 'react';
import './App.css';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import Header from './components/Header';
import Login from './components/Login';

function App() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeSpent, setTimeSpent] = useState(0);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [currentTrackingTask, setCurrentTrackingTask] = useState<number | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [timerInterval, setTimerInterval] = useState<NodeJS.Timeout | null>(null);
  const [activeTimeSession, setActiveTimeSession] = useState<number | null>(null);
  const [active60MinSession, setActive60MinSession] = useState<Record<number, number | null>>({});
  const [taskSessionStates, setTaskSessionStates] = useState<Record<number, { isWorkPeriod: boolean; timeLeft: number | null }>>({});
  const [sessionIntervals, setSessionIntervals] = useState<Record<number, NodeJS.Timeout | null>>({});
  const [activeTimerType, setActiveTimerType] = useState<'manual' | 'session' | null>(null);
  const [workTime, setWorkTime] = useState<number>(45); // minutes
  const [breakTime, setBreakTime] = useState<number>(15); // minutes
  const [showSessionSettings, setShowSessionSettings] = useState(false);
  const [notifications, setNotifications] = useState<{id: number; message: string}[]>([]);
  const shownNotificationsRef = React.useRef<Record<string, boolean>>({});
  const [showNotification, setShowNotification] = useState<{message: string; type: string; id: number} | null>(null);
  const [pendingNoteSession, setPendingNoteSession] = useState<{
    sessionId: number;
    endTime: string;
  } | null>(null);
  const [noteModal, setNoteModal] = useState<{
    sessionId: number;
    endTime: string;
  } | null>(null);

  const [noteInput, setNoteInput] = useState("");
  const intervalRef = React.useRef<NodeJS.Timeout | null>(null);
  // Notification timeout reference
  const notificationTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);
  // Create audio context for notification sound
  const notificationSoundRef = React.useRef<HTMLAudioElement | null>(null);

  // Format seconds to HH:MM:SS
  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Timer effect
  useEffect(() => {
    if (currentTrackingTask !== null) {
      const interval = setInterval(() => {
        setElapsedTime(prev => {
          const newTime = prev + 1;
          return newTime;
        });
      }, 1000);
      
      setTimerInterval(interval);
    } else {
      if (timerInterval) {
        clearInterval(timerInterval);
        setTimerInterval(null);
      }
      setElapsedTime(0);
    }

    return () => {
      if (timerInterval) {
        clearInterval(timerInterval);
      }
    };
  }, [currentTrackingTask]);

  // Check if user is already logged in (from localStorage)
  useEffect(() => {
    const savedUser = localStorage.getItem('productivity_user');
    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
      setIsLoggedIn(true);
    }
    
    // Request notification permission on app load
    if ("Notification" in window && Notification.permission !== "granted") {
      Notification.requestPermission();
    }
  }, []);

  // Fetch tasks when user is logged in
  useEffect(() => {
    if (isLoggedIn) {
      fetchTasks();
    }
  }, [isLoggedIn]);

  const saveSessionNote = async () => {
    if (!noteModal) return;

    try {
      await fetch(`http://localhost:8000/api/v1/time-sessions/${noteModal.sessionId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          end_time: noteModal.endTime,
          notes: noteInput || ""
        }),
      });
    } catch (e) {
      console.error("Error saving session note:", e);
    }

    setNoteModal(null);
    setNoteInput("");
  };

  const handleLogin = (username: string) => {
    const userId = username.toLowerCase() === 'alice' ? 1 : 
                   username.toLowerCase() === 'bob' ? 2 : 
                   username.toLowerCase() === 'charlie' ? 3 : 2;
    const user = { username, id: userId };
    setCurrentUser(user);
    setIsLoggedIn(true);
    localStorage.setItem('productivity_user', JSON.stringify(user));
    fetchTasks();
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setIsLoggedIn(false);
    localStorage.removeItem('productivity_user');
  };

  const fetchTasks = async () => {
    try {
      const baseUrl = 'http://localhost:8000/api/v1/tasks/';
      const url = currentUser?.id ? `${baseUrl}?user_id=${currentUser.id}` : baseUrl;
      const response = await fetch(url);
      const data = await response.json();
      setTasks(data);
      setLoading(false);
      
      const totalTime = data.reduce((sum: number, task: any) => sum + (task.estimated_minutes || 0), 0);
      setTimeSpent(totalTime);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      setLoading(false);
    }
  };

  const addTask = async (taskData: any) => {
    try {
      const taskWithUser = {
        ...taskData,
        user_id: currentUser?.id || 2
      };
      
      const response = await fetch('http://localhost:8000/api/v1/tasks/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskWithUser),
      });
      const newTask = await response.json();
      setTasks([...tasks, newTask]);
      
      setTimeSpent(prev => prev + (newTask.estimated_minutes || 0));
    } catch (error) {
      console.error('Error adding task:', error);
    }
  };

  const updateTask = async (taskId: number, taskData: any) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData),
      });
      
      if (response.ok) {
        const updatedTask = await response.json();
        setTasks(tasks.map(task => task.id === taskId ? updatedTask : task));
      }
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };

  const deleteTask = async (id: number) => {
    try {
      const taskToDelete = tasks.find(task => task.id === id);
      
      if (!taskToDelete) return;
      
      // Show confirmation for JIRA export
      let shouldExportToJira = true;
      if (taskToDelete.jira_issue_key) {
        // For tasks imported from Jira, ask if they want to add worklog
        shouldExportToJira = window.confirm('This task was imported from Jira. Export time tracking to Jira worklog?');
      } else {
        // For local tasks, ask if they want to create a Jira story
        shouldExportToJira = window.confirm('This task was created locally. Export to Jira as a new story?');
      }
      
      if (shouldExportToJira) {
        // Export to Jira - this will call the backend endpoint that handles the export
        try {
          const exportResponse = await fetch(`http://localhost:8000/api/v1/jira/tasks/${id}/export-to-jira`, {
            method: 'POST',
          });
          
          if (!exportResponse.ok) {
            console.warn('Failed to export to Jira for task', id);
          }
        } catch (exportError) {
          console.warn('Error exporting to Jira:', exportError);
        }
      }
      
      // First, try to delete the corresponding Jira issue if it exists
      try {
        const jiraResponse = await fetch(`http://localhost:8000/api/v1/tasks/${id}/jira`, {
          method: 'DELETE',
        });
        if (!jiraResponse.ok) {
          console.warn('Failed to delete Jira issue for task', id);
        }
      } catch (jiraError) {
        console.warn('Error deleting Jira issue:', jiraError);
      }
      
      await fetch(`http://localhost:8000/api/v1/tasks/${id}`, {
        method: 'DELETE',
      });
      setTasks(tasks.filter(task => task.id !== id));
      
      if (taskToDelete && taskToDelete.estimated_minutes) {
        setTimeSpent(prev => Math.max(0, prev - taskToDelete.estimated_minutes));
      }
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  const startTimer = async (taskId: number) => {
    // Stop any active 60-minute session for this task
    if (active60MinSession[taskId] !== undefined && active60MinSession[taskId] !== null) {
      await stop60MinSession(taskId);
    }
    
    // Stop any existing manual timer
    if (currentTrackingTask !== null) {
      await stopTimer(currentTrackingTask);
    }
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/time-sessions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_id: taskId,
          start_time: new Date().toISOString(),
        }),
      });
      
      if (response.ok) {
        const timeSession = await response.json();
        setActiveTimeSession(timeSession.id);
        setCurrentTrackingTask(taskId);
        setActiveTimerType('manual');
      }
    } catch (error) {
      console.error('Error starting timer:', error);
    }
  };

  const stopTimer = async (taskId: number) => {
    try {
      if (activeTimeSession) {
        const endTime = new Date().toISOString();
        await promptAndSaveSessionNote(activeTimeSession, endTime);
      }
      
      setCurrentTrackingTask(null);
      setActiveTimeSession(null);
      setActiveTimerType(null);
    } catch (error) {
      console.error('Error stopping timer:', error);
    }
  };

  // 60-minute session functions
  const start60MinSession = async (taskId: number) => {
    delete shownNotificationsRef.current[`work-${taskId}`];
    delete shownNotificationsRef.current[`break-${taskId}`];
    // Stop any existing manual timer
    if (currentTrackingTask !== null) {
      await stopTimer(currentTrackingTask);
    }
    
    // Stop any active 60-minute session for ANY task (only one session at a time)
    const activeTaskId = Object.keys(active60MinSession).find(key => active60MinSession[parseInt(key)] !== null);
    if (activeTaskId) {
      await stop60MinSession(parseInt(activeTaskId));
    }
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/time-sessions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_id: taskId,
          start_time: new Date().toISOString(),
        }),
      });
      
      if (response.ok) {
        const timeSession = await response.json();
        setActive60MinSession(prev => ({ ...prev, [taskId]: timeSession.id }));
        setTaskSessionStates(prev => ({ 
          ...prev, 
          [taskId]: { isWorkPeriod: true, timeLeft: workTime * 60 } 
        }));
        setActiveTimerType('session');
      }
    } catch (error) {
      console.error('Error starting 60-minute session:', error);
    }
  };

  const stop60MinSession = async (taskId: number) => {
    try {
      const sessionId = active60MinSession[taskId];
      if (sessionId) {
        const endTime = new Date().toISOString();
        await promptAndSaveSessionNote(sessionId, endTime);
      }
      
      // Clear the session state
      setActive60MinSession(prev => {
        const newSession = { ...prev };
        delete newSession[taskId];
        return newSession;
      });
      
      setTaskSessionStates(prev => {
        const newStates = { ...prev };
        delete newStates[taskId];
        return newStates;
      });
      
      // Clear interval if exists
      if (sessionIntervals[taskId]) {
        clearInterval(sessionIntervals[taskId]!);
        setSessionIntervals(prev => {
          const newIntervals = { ...prev };
          delete newIntervals[taskId];
          return newIntervals;
        });
      }
      
      setActiveTimerType(null);
    } catch (error) {
      console.error('Error stopping 60-minute session:', error);
    }
  };

  // Helper function to prompt user for session notes and save to backend
  const promptAndSaveSessionNote = async (sessionId: number, endTime: string) => {
    try {
      const userInput = prompt("What did you do in this session?");
      const notes = userInput !== null ? userInput : "";
      
      await fetch(`http://localhost:8000/api/v1/time-sessions/${sessionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          end_time: endTime,
          notes: notes
        }),
      });
    } catch (error) {
      console.error('Error saving session note:', error);
    }
  };
  
  const endBackendSession = async (taskId: number) => {
    try {
      const sessionId = active60MinSession[taskId];
      if (!sessionId) return;

      const endTime = new Date().toISOString();

      setPendingNoteSession({
        sessionId,
        endTime
      });

      // mark backend session closed but keep UI break session
      setActive60MinSession(prev => ({
        ...prev,
        [taskId]: null
      }));

    } catch (error) {
      console.error('Error ending backend session:', error);
    }
  };

  const is60MinSessionActive = (taskId: number): boolean => {
    return active60MinSession[taskId] !== undefined && active60MinSession[taskId] !== null;
  };

  const timeLeftFor60MinSession = (taskId: number): number | null => {
    return taskSessionStates[taskId]?.timeLeft ?? null;
  };

  const importJiraIssues = async () => {
    try {
      const projectKeyInput = document.getElementById('jira-project-key') as HTMLInputElement;
      const issuesInput = document.getElementById('jira-issues') as HTMLInputElement;
      
      if (!projectKeyInput || !issuesInput) {
        console.error('Jira input elements not found');
        return;
      }
      
      const projectKey = projectKeyInput.value.trim();
      const issues = issuesInput.value.trim();
      
      if (!projectKey || !issues) {
        alert('Please enter both Project Key and Issue Keys');
        return;
      }
      
      // Split comma-separated issue keys
      const issueKeys = issues.split(',').map(key => key.trim()).filter(key => key);
      
      if (issueKeys.length === 0) {
        alert('Please enter at least one valid issue key');
        return;
      }
      
      // Fetch issues from backend (which will call Jira API)
      const response = await fetch('http://localhost:8000/api/v1/jira/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_key: projectKey,
          issue_keys: issueKeys,
          user_id: currentUser?.id || 2
        }),
      });
      
      if (response.ok) {
        const result = await response.json();

        if (result.status === "success") {

          await fetchTasks();

          alert(`Successfully imported ${result.tasks.length} tasks from Jira`);

          projectKeyInput.value = '';
          issuesInput.value = '';

        } else {
          alert(`Error importing tasks: ${result.detail || "Unknown error"}`);
        }
      }
    } catch (error) {
        console.error('Error importing Jira issues:', error);
        alert('Error importing tasks from Jira');
    }
  };

  // Timer effect for 60-minute session
  useEffect(() => {

    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Only start interval if we have active sessions
    if (Object.keys(taskSessionStates).length > 0) {
      intervalRef.current = setInterval(() => {
        setTaskSessionStates(prev => {
          const newState = { ...prev };
          let shouldUpdate = false;

          const taskKeys = Object.keys(newState);

          taskKeys.forEach(taskIdStr => {
            const taskId = Number(taskIdStr);
            const state = newState[taskId];

            if (isNaN(taskId) || state?.timeLeft === null) return;
            if (!state) return;

            const timeLeftValue = state.timeLeft;
            const newTime = timeLeftValue - 1;

            if (newTime !== null) {

              if (newTime <= 0 && state.isWorkPeriod) {

                const notificationKey = `work-${taskId}`;

                if (!shownNotificationsRef.current[notificationKey] && typeof window !== 'undefined') {
                  setShowNotification({message: `Work period completed! Time for a ${breakTime}-minute break.`, type: 'info', id: Date.now()});
                  shownNotificationsRef.current[notificationKey] = true;
                }

                endBackendSession(taskId);

                newState[taskId] = {
                  isWorkPeriod: false,
                  timeLeft: breakTime * 60
                };

                shouldUpdate = true;

              } else if (newTime <= 0 && !state.isWorkPeriod) {

                const notificationKey = `break-${taskId}`;

                if (!shownNotificationsRef.current[notificationKey] && typeof window !== 'undefined') {
                  setShowNotification({message: `Break period completed! Back to work.`, type: 'info', id: Date.now()});
                  shownNotificationsRef.current[notificationKey] = true;
                }

                // Clear the session state completely when break ends
                delete newState[taskId];

                setActive60MinSession(prev => {
                  const copy = { ...prev };
                  delete copy[taskId];
                  return copy;
                });

                shouldUpdate = true;

              } else {

                newState[taskId] = {
                  ...state,
                  timeLeft: newTime
                };

                shouldUpdate = true;
              }
            }
          });

          return shouldUpdate ? newState : prev;
        });

      }, 1000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };

  }, [taskSessionStates, breakTime]);

  useEffect(() => {
    if (!pendingNoteSession) return;

    // Only trigger modal when user is BACK to tab
    if (document.visibilityState === "visible") {
      setNoteModal(pendingNoteSession);
      setPendingNoteSession(null);
    }

  }, [pendingNoteSession]);

  useEffect(() => {
    const handleVisibility = () => {
      if (document.visibilityState === "visible" && pendingNoteSession) {
        setNoteModal(pendingNoteSession);
        setPendingNoteSession(null);
      }
    };

    document.addEventListener("visibilitychange", handleVisibility);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [pendingNoteSession]);

  useEffect(() => {
    notificationSoundRef.current = new Audio('/notification.wav');
  }, []);

  useEffect(() => {
    if (showNotification) {
      if (notificationTimeoutRef.current) {
        clearTimeout(notificationTimeoutRef.current);
      }

      notificationTimeoutRef.current = setTimeout(() => {
        setShowNotification(null);
      }, 3000);

      // Play notification sound when notification is shown
      if (notificationSoundRef.current) {
        try {
          const audio = notificationSoundRef.current;
          audio.pause();
          audio.currentTime = 0;
          audio.play().catch(() => {});
        } catch (e) {
          console.log('Notification sound error:', e);
        }
      }
      // BACKGROUND NOTIFICATION
      if (Notification.permission === "granted") {
        new Notification("Productivity Tracker", {
          body: showNotification.message,
        });
      }
    }
  }, [showNotification]);

  // If not logged in, show login screen
  if (!isLoggedIn) {
    return (
      <div className="App">
        <Header currentUser={null} onLogout={() => {}} />
        <main className="main-content">
          <div className="container">
            <h1>Productivity Tracker</h1>
            <Login onLogin={handleLogin} />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="App">
      {noteModal && (
        <div className="note-modal-overlay">
          <div className="note-modal">
            <h3>Session Completed</h3>
            <textarea
              placeholder="What did you do?"
              value={noteInput}
              onChange={(e) => setNoteInput(e.target.value)}
            />
            <div className="note-actions">
              <button onClick={saveSessionNote}>Save</button>
              <button onClick={() => setNoteModal(null)}>Skip</button>
            </div>
          </div>
        </div>
      )}
      {showNotification && (
        <div className={`toast toast-${showNotification.type}`}>
          {showNotification.message}
        </div>
      )}
      <Header currentUser={currentUser} onLogout={handleLogout} />
      <main className="main-content">
        <div className="container">
          <h1>Productivity Tracker</h1>
          
          <div className="time-counter">
            <div className="session-settings">
              <button onClick={() => setShowSessionSettings(true)} className="session-settings-btn">
                Session Settings
              </button>
              {showSessionSettings && (
                <div className="session-settings-form">
                  <h3>Session Settings</h3>
                  <div className="setting-item">
                    <label>Work Time (minutes):</label>
                    <input 
                      type="number" 
                      value={workTime} 
                      onChange={(e) => setWorkTime(Math.min(99, Math.max(1, parseInt(e.target.value) || 1) ))}
                      max="99"
                      min="1"
                    />
                  </div>
                  <div className="setting-item">
                    <label>Break Time (minutes):</label>
                    <input 
                      type="number" 
                      value={breakTime} 
                      onChange={(e) => setBreakTime(Math.min(99, Math.max(1, parseInt(e.target.value) || 1) ))}
                      max="99"
                      min="1"
                    />
                  </div>
                  <button onClick={() => setShowSessionSettings(false)} className="save-settings-btn">
                    Save Settings
                  </button>
                </div>
              )}
            </div>
            {activeTimerType === 'manual' && currentTrackingTask !== null && (
              <div className="active-timer">
                <div className="timer-display">Active Timer: {formatTime(elapsedTime)}</div>
              </div>
            )}
            {activeTimerType === 'session' && Object.keys(taskSessionStates).length > 0 && (
              <div className="active-timer">
                <div className="session-timer">
                  {Object.entries(taskSessionStates).map(([taskId, state]) => (
                    <span key={taskId} className={state.isWorkPeriod ? 'work-period' : 'break-period'}>
                      {state.isWorkPeriod ? 'Work: ' : 'Break: '}
                      {state.timeLeft !== null && state.timeLeft > 0 
                        ? `${Math.floor(state.timeLeft / 60).toString().padStart(2, '0')}:${(state.timeLeft % 60).toString().padStart(2, '0')}`
                        : '00:00'}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          <div className="jira-import-section">
            <h2>Jira Import</h2>
            <div className="jira-import-form">
              <input 
                type="text" 
                id="jira-project-key" 
                placeholder="Enter Jira Project Key (e.g., PROJ)" 
                className="jira-input"
              />
              <input 
                type="text" 
                id="jira-issues" 
                placeholder="Enter Jira Issue Keys (comma-separated)" 
                className="jira-input"
              />
              <button onClick={() => importJiraIssues()} className="jira-import-btn">
                Import from Jira
              </button>
            </div>
          </div>
          
          <TaskForm onAddTask={addTask} />
          <TaskList 
            tasks={tasks} 
            loading={loading} 
            onDeleteTask={deleteTask} 
            currentTrackingTask={currentTrackingTask}
            onStartTimer={startTimer}
            onStopTimer={stopTimer}
            onStart60MinSession={start60MinSession}
            onStop60MinSession={stop60MinSession}
            is60MinSessionActive={is60MinSessionActive}
            timeLeftFor60MinSession={timeLeftFor60MinSession}
            workTime={workTime}
            onUpdateTask={updateTask}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
