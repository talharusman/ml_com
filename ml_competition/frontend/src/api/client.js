/**
 * API client for F1-Score Grand Prix
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Get auth headers if token is available
 */
function getAuthHeaders() {
  const token = localStorage.getItem('token');
  if (token) {
    return { 'Authorization': `Bearer ${token}` };
  }
  return {};
}

/**
 * Fetch all tasks
 */
export async function fetchTasks() {
  const response = await fetch(`${API_BASE}/tasks?t=${Date.now()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch tasks');
  }
  return response.json();
}

/**
 * Fetch template code for a task
 */
export async function fetchTemplate(taskId) {
  const response = await fetch(`${API_BASE}/template/${taskId}?t=${Date.now()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch template');
  }
  return response.json();
}

/**
 * Fetch sample data for a task
 */
export async function fetchSampleData(taskId) {
  const response = await fetch(`${API_BASE}/sample-data/${taskId}?t=${Date.now()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch sample data');
  }
  return response.json();
}

/**
 * Download training data for a task
 */
export function getDownloadUrl(taskId) {
  return `${API_BASE}/download/${taskId}`;
}

/**
 * Fetch leaderboard data
 */
export async function fetchLeaderboard() {
  const response = await fetch(`${API_BASE}/leaderboard`);
  if (!response.ok) {
    throw new Error('Failed to fetch leaderboard');
  }
  return response.json();
}

/**
 * Upload a submission file
 */
export async function uploadSubmission(taskId, file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE}/upload/${taskId}`, {
    method: 'POST',
    body: formData,
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    const text = await response.text();
    let detail = text;
    try {
      const parsed = JSON.parse(text);
      if (parsed?.detail) detail = parsed.detail;
    } catch (e) {
      // keep raw text
    }
    throw new Error(detail || 'Upload failed');
  }
  
  return response.json();
}

/**
 * Evaluate a submission
 */
export async function evaluateSubmission(submissionId, taskId) {
  const response = await fetch(`${API_BASE}/evaluate/${submissionId}?task_id=${taskId}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    const text = await response.text();
    let detail = text;
    try {
      const parsed = JSON.parse(text);
      if (parsed?.detail) detail = parsed.detail;
    } catch (e) {
      // keep raw text
    }
    throw new Error(detail || 'Evaluation failed');
  }
  
  return response.json();
}

/**
 * Register a new user
 */
export async function register(username, password, email = null) {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, email }),
  });
  
  if (!response.ok) {
    const text = await response.text();
    let detail = text;
    try {
      const parsed = JSON.parse(text);
      if (parsed?.detail) detail = parsed.detail;
    } catch (e) {
      // keep raw text
    }
    throw new Error(detail || 'Registration failed');
  }
  
  return response.json();
}

/**
 * Login user
 */
export async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString(),
  });
  
  if (!response.ok) {
    const text = await response.text();
    let detail = text;
    try {
      const parsed = JSON.parse(text);
      if (parsed?.detail) detail = parsed.detail;
    } catch (e) {
      // keep raw text
    }
    throw new Error(detail || 'Login failed');
  }
  
  return response.json();
}

/**
 * Get current user info
 */
export async function getCurrentUser() {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to get user info');
  }
  
  return response.json();
}
