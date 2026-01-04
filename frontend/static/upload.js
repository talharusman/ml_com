const API_BASE = ""
let currentTaskId = null
let currentLeaderboardFilter = 'all'
let participantSubmissionCount = {}

// Initialize page on load
document.addEventListener("DOMContentLoaded", () => {
  navigateTo('home')
  // Refresh leaderboard every 5 seconds when on leaderboard page
  setInterval(() => {
    if (document.getElementById('leaderboard-page').classList.contains('active')) {
      loadLeaderboard()
    }
  }, 5000)
})

function navigateTo(page) {
  // Hide all pages
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'))
  
  // Show selected page
  const selectedPage = document.getElementById(`${page}-page`)
  if (selectedPage) {
    selectedPage.classList.add('active')
  }
  
  // Load page-specific content
  if (page === 'challenges') {
    loadTasks()
  } else if (page === 'leaderboard') {
    loadLeaderboard()
  }
  
  // Scroll to top
  window.scrollTo(0, 0)
}

// Load tasks from API
async function loadTasks() {
  try {
    const response = await fetch(`${API_BASE}/tasks?t=${Date.now()}`)
    const tasks = await response.json()

    const tasksGrid = document.getElementById("tasksGrid")
    tasksGrid.innerHTML = ""

    tasks.forEach((task) => {
      const taskCard = createTaskCard(task)
      tasksGrid.appendChild(taskCard)
    })
  } catch (error) {
    console.error("Error loading tasks:", error)
  }
}

// Create task card HTML
function createTaskCard(task) {
  const card = document.createElement("div")
  card.className = "task-card"

  const metricText = task.type === "eda" ? `Score: ${task.metric}` : `Metric: ${task.metric}`

  card.innerHTML = `
    <div class="task-card-header">
      <div class="task-id">${task.id}</div>
      <div class="task-name">${task.name}</div>
    </div>
    <p class="task-description">${task.description}</p>
    <div class="task-metric">${metricText}</div>
    <div class="task-actions">
      <button class="btn btn-secondary" onclick="openTaskDetail(${task.id})">View Details</button>
      <button class="btn btn-primary" onclick="openUploadModal(${task.id})">Submit</button>
    </div>
  `

  return card
}

async function openTaskDetail(taskId) {
  currentTaskId = taskId
  const modal = document.getElementById("taskDetailModal")

  try {
    // Fetch task info
    const tasksResponse = await fetch(`${API_BASE}/tasks?t=${Date.now()}`)
    if (!tasksResponse.ok) {
      const msg = await tasksResponse.text()
      throw new Error(`Failed to load tasks: ${msg}`)
    }
    const tasks = await tasksResponse.json()
    const task = tasks.find((t) => t.id === taskId)

    if (!task) {
      alert("Question not found")
      return
    }

    // Fetch template code
    const templateResponse = await fetch(`${API_BASE}/template/${taskId}?t=${Date.now()}`)
    if (!templateResponse.ok) {
      const msg = await templateResponse.text()
      throw new Error(`Failed to load template: ${msg}`)
    }
    const templateData = await templateResponse.json()

    // Fetch sample data
    let sampleData = { columns: [], data: [], shape: [0,0] }
    try {
      const dataResponse = await fetch(`${API_BASE}/sample-data/${taskId}?t=${Date.now()}`)
      if (dataResponse.ok) {
        sampleData = await dataResponse.json()
      } else {
        console.warn("Sample data request failed:", await dataResponse.text())
      }
    } catch (e) {
      console.warn("Error loading sample data:", e)
    }

    // Populate modal
    document.getElementById("taskDetailTitle").textContent = `${task.name} - Question ${taskId}`
    document.getElementById("taskDetailDescription").textContent = task.description
    document.getElementById("taskDetailMetric").textContent =
      task.type === "eda" ? `Score Method: ${task.metric}` : `Evaluation Metric: ${task.metric}`

    // Display template code directly
    document.getElementById("templateCode").textContent = templateData.code

    // Display sample data table
    displaySampleData(sampleData)

    // Show modal
    modal.classList.add("active")
  } catch (error) {
    console.error("Error opening question detail:", error)
    alert("Failed to load question details")
  }
}

// Display sample data as table
function displaySampleData(data) {
  const container = document.getElementById("sampleDataContainer")

  if (!data.data || data.data.length === 0) {
    container.innerHTML = "<p>No data available</p>"
    return
  }

  const columns = data.columns
  let html = `<p class="data-info">Showing ${data.data.length} rows from dataset with ${data.shape[1]} columns</p>`
  html += '<table class="sample-data-table"><thead><tr>'

  // Header
  columns.forEach((col) => {
    html += `<th>${col}</th>`
  })
  html += "</tr></thead><tbody>"

  // Rows
  data.data.forEach((row) => {
    html += "<tr>"
    columns.forEach((col) => {
      const value = row[col]
      const displayValue = value === null ? "null" : typeof value === "number" ? value.toFixed(2) : value
      html += `<td>${displayValue}</td>`
    })
    html += "</tr>"
  })

  html += "</tbody></table>"
  container.innerHTML = html
}

// Copy template code to clipboard
function copyTemplateCode() {
  const code = document.getElementById("templateCode").textContent
  navigator.clipboard
    .writeText(code)
    .then(() => {
      alert("Template code copied to clipboard!")
    })
    .catch((err) => {
      console.error("Failed to copy:", err)
    })
}

// Close task modal
function closeTaskModal() {
  const modal = document.getElementById("taskDetailModal")
  modal.classList.remove("active")
  currentTaskId = null
}

// Go to task upload from modal
function goToTaskCard() {
  closeTaskModal()
  if (currentTaskId !== null) {
    openUploadModal(currentTaskId)
  }
}

// Trigger upload modal from the task detail SUBMIT button
function submitEditedCode() {
  if (currentTaskId !== null) {
    openUploadModal(currentTaskId)
  } else {
    alert("Please select a question first")
  }
}

// Open upload modal
function openUploadModal(taskId) {
  const modal = document.createElement("div")
  modal.className = "modal active"
  modal.innerHTML = `
    <div class="modal-content">
      <span class="modal-close" onclick="this.parentElement.parentElement.remove()">×</span>
      <h3>Submit Solution for Question ${taskId}</h3>
      <form onsubmit="submitFile(event, ${taskId})">
        <div class="form-group">
          <label for="file-${taskId}">Select Python File</label>
          <label class="file-input-label">
            Click to browse or drag files here
            <input type="file" id="file-${taskId}" accept=".py" required>
          </label>
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%;">Submit</button>
      </form>
    </div>
  `

  document.body.appendChild(modal)

  // Close modal on background click
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.remove()
  })

  // File drag and drop
  const fileInput = document.getElementById(`file-${taskId}`)
  const label = fileInput.parentElement

  label.addEventListener("dragover", (e) => {
    e.preventDefault()
    label.style.borderColor = "var(--primary-color)"
    label.style.background = "var(--bg-light)"
  })

  label.addEventListener("dragleave", () => {
    label.style.borderColor = ""
    label.style.background = ""
  })

  label.addEventListener("drop", (e) => {
    e.preventDefault()
    fileInput.files = e.dataTransfer.files
    label.style.borderColor = ""
  })
}

// Submit file
async function submitFile(event, taskId) {
  event.preventDefault()

  const fileInput = event.target.querySelector('input[type="file"]')
  const file = fileInput.files[0]

  if (!file) {
    alert("Please select a file")
    return
  }

  const formData = new FormData()
  formData.append("file", file)

  try {
    // Upload file
    const uploadResponse = await fetch(`${API_BASE}/upload/${taskId}`, {
      method: "POST",
      body: formData,
    })
    if (!uploadResponse.ok) {
      let msg = await uploadResponse.text()
      try {
        const parsed = JSON.parse(msg)
        if (parsed?.detail) msg = parsed.detail
      } catch (e) {
        // keep raw text if not JSON
      }
      const lowerMsg = (msg || "").toLowerCase()
      if (uploadResponse.status === 400 && lowerMsg.includes("submission limit")) {
        alert(msg || "Submission limit reached for this task (max 3)")
        return
      }
      alert(msg || "Upload failed")
      return
    }
    const uploadData = await uploadResponse.json()
    const submissionId = uploadData.submission_id

    // Auto-evaluate
    const evalResponse = await fetch(`${API_BASE}/evaluate/${submissionId}?task_id=${taskId}`, {
      method: "POST",
    })
    if (!evalResponse.ok) {
      let msg = await evalResponse.text()
      try {
        const parsed = JSON.parse(msg)
        if (parsed?.detail) msg = parsed.detail
      } catch (e) {
        // ignore parse
      }
      alert(msg || "Evaluation failed")
      return
    }
    const evalData = await evalResponse.json()

    // Close modal
    event.target.closest(".modal").remove()
    
    // Update leaderboard
    loadLeaderboard()

    // Show result
    alert(`Submission evaluated!\nScore: ${evalData.score}\nStatus: ${evalData.status}`)
  } catch (error) {
    console.error("Error submitting file:", error)
    alert(error?.message || "Error submitting file. Check console for details.")
  }
}

function filterLeaderboard(taskId) {
  currentLeaderboardFilter = taskId
  
  // Update filter buttons
  document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'))
  event.target.classList.add('active')
  
  loadLeaderboard()
}

async function loadLeaderboard() {
  try {
    const response = await fetch(`${API_BASE}/leaderboard`)
    const data = await response.json()

    // Count submissions per participant
    participantSubmissionCount = {}
    const perTaskSubmissionCount = {}
    data.submissions.forEach(sub => {
      const participantId = sub.submission_id.split('_')[0]
      if (!participantSubmissionCount[participantId]) {
        participantSubmissionCount[participantId] = 0
      }
      participantSubmissionCount[participantId]++

      const key = `${participantId}-${sub.task_id}`
      if (!perTaskSubmissionCount[key]) {
        perTaskSubmissionCount[key] = 0
      }
      perTaskSubmissionCount[key]++
    })

    // Filter based on current filter
    let allSubmissions = data.submissions
    
    if (currentLeaderboardFilter !== 'all') {
      allSubmissions = allSubmissions.filter(s => s.task_id === currentLeaderboardFilter)
    }
    
    allSubmissions = allSubmissions.sort((a, b) => b.score - a.score).slice(0, 100)

    const tbody = document.getElementById("leaderboardBody")

    if (allSubmissions.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px;">No submissions yet</td></tr>'
      return
    }

    tbody.innerHTML = allSubmissions
      .map(
        (sub, idx) => {
          const participantId = sub.submission_id.split('_')[0]
          const totalSubmissions = participantSubmissionCount[participantId] || 0
          const perTaskCount = perTaskSubmissionCount[`${participantId}-${sub.task_id}`] || 0
          return `
            <tr>
              <td>${idx + 1}</td>
              <td><strong>Q${sub.task_id}</strong></td>
              <td>${participantId}</td>
              <td><strong>${sub.score.toFixed(4)}</strong></td>
              <td>${perTaskCount}</td>
              <td>${totalSubmissions}</td>
              <td>${new Date(sub.timestamp).toLocaleString()}</td>
            </tr>
          `
        }
      )
      .join("")
  } catch (error) {
    console.error("Error loading leaderboard:", error)
  }
}
