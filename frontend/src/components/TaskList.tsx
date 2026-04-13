import React, { useState } from 'react';

interface Task {
  id: number;
  title: string;
  description: string;
  priority: string;
  completed: boolean;
  estimated_minutes?: number;
}

interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  onDeleteTask: (id: number) => void;
  currentTrackingTask: number | null;
  onStartTimer: (taskId: number) => void;
  onStopTimer: (taskId: number) => void;
  onStart60MinSession: (taskId: number) => void;
  onStop60MinSession: (taskId: number) => void;
  is60MinSessionActive: (taskId: number) => boolean;
  timeLeftFor60MinSession: (taskId: number) => number | null;
  workTime: number;
  onUpdateTask: (taskId: number, taskData: any) => void;
}

const TaskList: React.FC<TaskListProps> = ({ 
  tasks, 
  loading, 
  onDeleteTask, 
  currentTrackingTask, 
  onStartTimer, 
  onStopTimer,
  onStart60MinSession,
  onStop60MinSession,
  is60MinSessionActive,
  timeLeftFor60MinSession,
  workTime,
  onUpdateTask
}) => {
  const [confirmationModal, setConfirmationModal] = useState<{taskId: number, taskTitle: string} | null>(null);
  const [editingTask, setEditingTask] = useState<{id: number, title: string, description: string, priority: string, estimated_minutes?: number} | null>(null);
  const [editForm, setEditForm] = useState({
    title: '',
    description: '',
    priority: 'medium',
    estimated_minutes: ''
  });

  const handleDeleteClick = (taskId: number, taskTitle: string) => {
    setConfirmationModal({ taskId, taskTitle });
  };

  const confirmDelete = () => {
    if (confirmationModal) {
      onDeleteTask(confirmationModal.taskId);
      setConfirmationModal(null);
    }
  };

  const cancelDelete = () => {
    setConfirmationModal(null);
  };

  const startEditing = (task: Task) => {
    setEditingTask({
      id: task.id,
      title: task.title,
      description: task.description || '',
      priority: task.priority,
      estimated_minutes: task.estimated_minutes
    });
    setEditForm({
      title: task.title,
      description: task.description || '',
      priority: task.priority,
      estimated_minutes: task.estimated_minutes ? task.estimated_minutes.toString() : ''
    });
  };

  const cancelEditing = () => {
    setEditingTask(null);
    setEditForm({
      title: '',
      description: '',
      priority: 'medium',
      estimated_minutes: ''
    });
  };

  const handleEditChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setEditForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const saveEdit = () => {
    if (editingTask) {
      const taskData: any = {
        title: editForm.title,
        description: editForm.description,
        priority: editForm.priority,
      };
      
      if (editForm.estimated_minutes) {
        taskData.estimated_minutes = parseInt(editForm.estimated_minutes);
      } else {
        taskData.estimated_minutes = null;
      }
      
      onUpdateTask(editingTask.id, taskData);
      setEditingTask(null);
    }
  };

  if (loading) {
    return <div className="loading">Loading tasks...</div>;
  }

  if (tasks.length === 0) {
    return <div className="no-tasks">No tasks found. Add your first task!</div>;
  }

  return (
    <div className="task-list">
      <h2>Tasks ({tasks.length})</h2>
      {tasks.map((task) => (
        <div key={task.id} className={`task-item priority-${task.priority}`}>
          {editingTask?.id === task.id ? (
            <div className="task-edit-form">
              <input
                type="text"
                name="title"
                value={editForm.title}
                onChange={handleEditChange}
                className="edit-input"
              />
              <textarea
                name="description"
                value={editForm.description}
                onChange={handleEditChange}
                className="edit-textarea"
              />
              <select
                name="priority"
                value={editForm.priority}
                onChange={handleEditChange}
                className="edit-select"
              >
                <option value="lowest">Lowest Priority</option>
                <option value="low">Low Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="high">High Priority</option>
                <option value="highest">Highest Priority</option>
              </select>
              <input
                type="number"
                name="estimated_minutes"
                value={editForm.estimated_minutes}
                onChange={handleEditChange}
                placeholder="Estimated minutes"
                className="edit-input"
              />
              <div className="edit-buttons">
                <button onClick={saveEdit} className="save-button">Save</button>
                <button onClick={cancelEditing} className="cancel-button">Cancel</button>
              </div>
            </div>
          ) : (
            <>
              <div className="task-content">
                <h3>{task.title}</h3>
                <p>{task.description}</p>
                <div className="task-meta">
                  <span className={`priority-badge priority-${task.priority}`}>
                    {task.priority}
                  </span>
                  {task.completed && <span className="completed-badge">Completed</span>}
                  {task.estimated_minutes && (
                    <span className="estimated-time">
                      {task.estimated_minutes} min
                    </span>
                  )}
                </div>
              </div>
              <div className="task-actions">
                <button 
                  onClick={() => currentTrackingTask === task.id ? onStopTimer(task.id) : onStartTimer(task.id)}
                  className={`timer-button ${currentTrackingTask === task.id ? 'stop' : 'start'}`}
                >
                  {currentTrackingTask === task.id ? 'Stop Timer' : 'Start Timer'}
                </button>
                <button 
                  onClick={() => is60MinSessionActive(task.id) ? onStop60MinSession(task.id) : onStart60MinSession(task.id)}
                  className={`timer-button ${is60MinSessionActive(task.id) ? 'stop' : 'start'} session-button`}
                >
                  {is60MinSessionActive(task.id) ? 'Stop Work Session' : `Start ${workTime}min work session`}
                </button>
                <button 
                  onClick={() => startEditing(task)}
                  className="edit-button"
                >
                  Edit
                </button>
                <button 
                  onClick={() => handleDeleteClick(task.id, task.title)}
                  className="delete-button"
                >
                  Delete
                </button>
              </div>
            </>
          )}
        </div>
      ))}
      
      {confirmationModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Confirm Deletion</h3>
            <p>Are you sure you want to delete the task "{confirmationModal.taskTitle}"?</p>
            <p>This will also delete the corresponding Jira issue if it exists.</p>
            <div className="modal-buttons">
              <button onClick={confirmDelete} className="confirm-button">Delete</button>
              <button onClick={cancelDelete} className="cancel-button">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskList;
