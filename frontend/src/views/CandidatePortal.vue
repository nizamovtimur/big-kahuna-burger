<template>
  <div class="candidate-portal">
    <div class="container">
        <!-- Main Chat Section -->
        <div class="col-lg-12 chat-column">
          <div class="card border-0 shadow-sm chat-card">
            <!-- Chat Header -->
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center">
                <h5 class="mb-0 me-3">
                  <i class="fas fa-robot"></i> Мой HR
                </h5>
                <!-- Current Context -->
                <router-link 
                  v-if="selectedJob" 
                  :to="`/jobs/${selectedJob.id}`" 
                  class="badge bg-light text-dark text-decoration-none"
                  title="Открыть вакансию"
                >
                  <i class="fas fa-briefcase"></i> {{ selectedJob.title }}
                </router-link>
              </div>
              
              <!-- Chat Controls -->
              <div class="btn-group">
                <button 
                  class="btn btn-outline-light btn-sm"
                  @click="showSessionsList = !showSessionsList"
                  title="История чатов"
                >
                  <i class="fas fa-history"></i>
                </button>
                <button 
                  class="btn btn-outline-light btn-sm"
                  @click="startNewSession"
                  title="Новый чат"
                >
                  <i class="fas fa-plus"></i>
                </button>
                <button 
                  class="btn btn-outline-light btn-sm"
                  @click="showJobSelector = !showJobSelector"
                  title="Выбрать вакансию"
                >
                  <i class="fas fa-briefcase"></i>
                </button>
              </div>
            </div>
            
            <!-- Sessions Panel-->
            <div v-if="showSessionsList" class="job-selector-panel border-bottom">
              <div class="p-3">
                <h6 class="mb-3">
                  <i class="fas fa-history"></i> Выбрать чат
                </h6>
                <div class="row g-2">
                  <div class="col-md-6" v-for="session in chatSessions" :key="session.id">
                    <div 
                      class="job-card p-2 border rounded cursor-pointer"
                      :class="{ 'border-primary bg-light': currentChatSession?.id === session.id }"
                      @click="loadSession(session.id); showSessionsList = false"
                    >
                    <button
                      class="btn btn-outline-danger btn-sm float-end"
                      @click.stop="deleteSession(session.id)"
                      title="Удалить"
                    >
                      <i class="fas fa-trash-alt"></i>
                    </button>
                    <div class="fw-bold small">Чат #{{ session.id }}</div>
                      <div class="text-muted small">
                        {{ session.job_id? getJobTitle(session.job_id) : "Без вакансии" }}
                      </div>
                      <div class="text-muted small">
                        {{ formatTime(session.updated_at) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- Job Selector Panel -->
            <div v-if="showJobSelector" class="job-selector-panel border-bottom">
              <div class="p-3">
                <h6 class="mb-3">
                  <i class="fas fa-briefcase"></i> Выбрать вакансию для обсуждения
                </h6>
                <div class="row g-2">
                  <div class="col-md-6" v-for="job in availableJobs" :key="job.id">
                    <div 
                      class="job-card p-2 border rounded cursor-pointer"
                      :class="{ 'border-primary bg-light': selectedJob?.id === job.id }"
                      @click="selectJob(job)"
                    >
                      <div class="fw-bold small">{{ job.title }}</div>
                      <div class="text-muted small">{{ job.location }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Chat Messages -->
            <div class="card-body p-0 d-flex flex-column chat-body">
              <div class="chat-container flex-grow-1" ref="chatContainer">
                <!-- Empty State -->
                <div v-if="currentSessionMessages.length === 0" class="empty-chat-state">
                  <i class="fas fa-comments fa-3x mb-3 text-muted"></i>
                  <h5 class="text-muted">{{ getEmptyStateTitle() }}</h5>
                  <p class="text-muted small mb-0">{{ getEmptyStateSubtitle() }}</p>
                </div>
                
                <!-- Messages -->
                <div 
                  v-for="message in currentSessionMessages" 
                  :key="message.id"
                  class="message-wrapper"
                >
                  <div class="message" :class="message.role + '-message'">
                    <div class="message-content">
                      <div class="message-header">
                        <strong>{{ message.role === 'user' ? 'Вы' : 'HR Assistant' }}</strong>
                        <small class="text-muted">{{ formatTime(message.created_at) }}</small>
                      </div>
                      <div class="message-text" v-html="renderMarkdown(message.content)"></div>
                    </div>
                  </div>
                </div>
                
                <!-- Loading indicator -->
                <div v-if="sendingMessage" class="message-wrapper">
                  <div class="message assistant-message">
                    <div class="message-content">
                      <div class="message-header">
                        <strong>HR Assistant</strong>
                        <small class="text-muted">печатает...</small>
                      </div>
                      <div class="message-text">
                        <div class="typing-indicator">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Chat Input -->
            <div class="card-footer bg-light">
              <!-- File Upload Area -->
              <div v-if="showFileUpload" class="mb-2 p-2 border border-dashed rounded bg-light">
                <h6 class="mb-2">
                  <i class="fas fa-file-upload"></i> Загрузить резюме
                </h6>
                <input 
                  type="file" 
                  class="form-control" 
                  @change="handleFileUpload"
                  accept=".pdf,.doc,.docx"
                  ref="fileInput"
                />
                <div class="form-text">
                  Поддерживаемые форматы: PDF, DOC, DOCX (макс. 10МБ)
                </div>
              </div>
              
              <!-- Show attached file -->
              <div v-if="uploadedFile" class="mb-2 p-2 bg-light border rounded">
                <div class="d-flex align-items-center text-success">
                  <i class="fas fa-paperclip me-2"></i>
                  <span class="small">{{ uploadedFile.name }}</span>
                  <button 
                    class="btn btn-sm btn-outline-danger ms-auto"
                    @click="removeFile"
                    title="Удалить файл"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <div class="small text-muted mt-1">
                  Файл готов к отправке вместе с сообщением
                </div>
              </div>

              <!-- Message Input -->
              <div class="input-group">
                <input 
                  v-model="currentMessage" 
                  type="text" 
                  class="form-control" 
                  :placeholder="getInputPlaceholder()" 
                  @keyup.enter="sendMessage"
                  :disabled="sendingMessage"
                />
                <button 
                  class="btn btn-outline-secondary" 
                  @click="showFileUpload = !showFileUpload"
                  type="button"
                >
                  <i class="fas fa-paperclip"></i>
                </button>
                <button 
                  class="btn btn-primary" 
                  @click="sendMessage"
                  :disabled="sendingMessage || !canSendMessage"
                >
                  <i class="fas fa-paper-plane"></i>
                </button>
              </div>

              <!-- Suggetions -->
              <div class="mt-2 d-flex gap-2 flex-wrap">
                <button
                  class="btn btn-outline-primary btn-sm"
                  @click="useExamplePrompt('Какие вакансии доступны')">
                  <i class="fas fa-list"></i> Список вакансий
                </button>

                <button
                  class="btn btn-outline-primary btn-sm"
                  @click="useExamplePrompt('Какие льготы есть в компании?')">
                  <i class="fas fa-gift"></i> Льготы
                </button>

                <button
                  class="btn btn-outline-primary btn-sm"
                  @click="useExamplePrompt('Как проходит собеседование?')">
                  <i class="fas fa-handshake"></i> Собеседование
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { marked } from 'marked'

export default {
  name: 'CandidatePortal',
  data() {
    return {
      currentMessage: '',
      sendingMessage: false,
      selectedJob: null,
      showSessionsList: false,
      sessionSearchTerm: '',
      showJobSelector: false,
      showFileUpload: false,
      uploadedFile: null,
    }
  },
  computed: {
    ...mapGetters(['chatSessions', 'currentChatSession', 'applications', 'availableJobs']),
    
    currentSessionMessages() {
      return this.currentChatSession?.messages || []
    },
    
    filteredSessions() {
      if (!this.sessionSearchTerm.trim()) {
        return this.chatSessions
      }
      
      const searchTerm = this.sessionSearchTerm.toLowerCase()
      return this.chatSessions.filter(session => {
        const titleMatch = session.title?.toLowerCase().includes(searchTerm)
        const jobMatch = session.job_id?.toString().includes(searchTerm)
        const messageMatch = session.messages?.some(msg => 
          msg.content.toLowerCase().includes(searchTerm)
        )
        
        return titleMatch || jobMatch || messageMatch
      })
    },
    

    hasAppliedToCurrentJob() {
      return this.applications.some(app => app.job_id === this.selectedJob?.id);
    },

    canSendMessage() {
      return !!this.currentMessage.trim();
    }
  },
  methods: {
    ...mapActions(['sendChatMessage', 'fetchChatSessions', 'fetchChatSession', 'fetchApplications', 'deleteChatSession', 'clearAllChatSessions', 'fetchJobs']),
    renderMarkdown(raw) {
      try {
        // Minimal config; 'marked' escapes by default where needed
        return marked.parse(raw || '')
      } catch (e) {
        return raw || ''
      }
    },
    
    async sendMessage() {
      if (!this.canSendMessage) return
      
      try {
        this.scrollToBottom()
        this.sendingMessage = true
        console.log('Sending message:', this.currentMessage)
        console.log('Current session ID:', this.currentChatSession?.id)
        console.log('Selected job ID:', this.selectedJob?.id)
        console.log('Current mode:', this.currentMode)
        console.log('Uploaded file:', this.uploadedFile)
        console.log('Selected job object:', this.selectedJob)
        
        const messageData = {
          message: this.currentMessage,
          sessionId: this.currentChatSession?.id || null,
          jobId: this.selectedJob?.id || null
        }
        
        // If we have a file in apply mode, add it to the message
        if (this.uploadedFile) {
          messageData.file = this.uploadedFile
        }
        
        const result = await this.sendChatMessage(messageData)
        
        console.log('Message sent, result:', result)
        
        // Check if we just submitted an application
        const hadUploadedFile = !!this.uploadedFile;
        
        this.currentMessage = ''
        this.uploadedFile = null
        
        // If we sent a file in apply mode, refresh applications to update hasAppliedToCurrentJob
        if (hadUploadedFile) {
          try {
            await this.fetchApplications();
          } catch (error) {
            console.error('Failed to refresh applications:', error);
          }
        }
        this.showFileUpload = false
        this.scrollToBottom()
      } catch (error) {
        console.error('Failed to send message:', error)
        alert('Не удалось отправить сообщение: ' + error.message)
      } finally {
        this.sendingMessage = false
      }
    },
    
    async startNewSession() {
      this.selectJob(null);
      this.$store.commit('SET_CURRENT_CHAT_SESSION', null)
      this.scrollToBottom()
    },
    
    async loadSession(sessionId) {
      try {
        const session = await this.fetchChatSession(sessionId)
        // Sync selected job to the session's job_id
        if (session?.job_id) {
          const jobData = this.availableJobs.find(j => j.id === session.job_id)
          if (jobData) {
            this.selectedJob = jobData
          }
        } else {
          this.selectedJob = null
        }
        this.scrollToBottom()
      } catch (error) {
        alert('Не удалось загрузить сессию: ' + error.message)
      }
    },
    
    async deleteSession(sessionId) {
      if (confirm('Удалить эту сессию? Это действие нельзя отменить.')) {
        try {
          await this.deleteChatSession(sessionId)
        } catch (error) {
          alert('Не удалось удалить сессию: ' + error.message)
        }
      }
    },
    
    async clearAllSessions() {
      if (confirm('Очистить все сессии чата? Это действие нельзя отменить.')) {
        try {
          await this.clearAllChatSessions()
          this.showSessionsList = false
        } catch (error) {
          alert('Не удалось очистить сессии: ' + error.message)
        }
      }
    },
    
    async exportSessions() {
      try {
        // Create export data from current sessions
        const exportData = {
          exported_at: new Date().toISOString(),
          total_sessions: this.chatSessions.length,
          sessions: this.chatSessions.map(session => ({
            id: session.id,
            created_at: session.created_at,
            updated_at: session.updated_at,
            job_id: session.job_id,
            title: session.title,
            messages: session.messages || []
          }))
        }
        
        const dataStr = JSON.stringify(exportData, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        
        const link = document.createElement('a')
        link.href = URL.createObjectURL(dataBlob)
        link.download = `chat-sessions-export-${new Date().toISOString().split('T')[0]}.json`
        link.click()
        
        setTimeout(() => URL.revokeObjectURL(link.href), 100)
        
        alert(`Экспорт завершен! Сохранено ${exportData.total_sessions} сессий.`)
        
      } catch (error) {
        alert('Не удалось экспортировать сессии: ' + error.message)
      }
    },
    
    clearSessionSearch() {
      this.sessionSearchTerm = ''
    },
    
    formatSessionDate(dateString) {
      const date = new Date(dateString)
      const today = new Date()
      const yesterday = new Date(today)
      yesterday.setDate(yesterday.getDate() - 1)
      
      if (date.toDateString() === today.toDateString()) {
        return 'Сегодня'
      } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Вчера'
      } else {
        return date.toLocaleDateString('ru-RU', { 
          day: 'numeric', 
          month: 'long' 
        })
      }
    },
    
    useExamplePrompt(prompt) {
      this.currentMessage = prompt
    },

    selectJob(job) {
      this.selectedJob = job;
      this.showJobSelector = false;
      this.showFileUpload = false;
      this.uploadedFile = null;
    },

    getEmptyStateTitle() {
      if (this.selectedJob) {
        return 'Обсуждение вакансии';
      }
      return 'Начните новую беседу';
    },

    getEmptyStateSubtitle() {
      if (this.selectedJob) {
        return 'Задайте вопрос о вакансии: ' + this.selectedJob.title;
      }
      return 'Выберите вакансию или задайте общий вопрос';
    },

    getInputPlaceholder() {
      return 'Напишите сообщение...';
    },

    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.uploadedFile = file;
        this.showFileUpload = false;
        console.log('File attached:', file.name);
        // File is just attached, not sent automatically
        // User must write a message and send manually
      }
    },

    removeFile() {
      this.uploadedFile = null;
      this.$refs.fileInput.value = '';
    },

    getJobTitle(jobId) {
      const job = this.availableJobs.find(j => j.id === jobId)
      return job ? job.title : `Job #${jobId}`
    },
    
    formatTime(dateString) {
      return new Date(dateString).toLocaleTimeString()
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.chatContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },

    async processQueryParams() {
      const { job } = this.$route.query;
      
      if (job) {
        // Find job in available jobs
        const jobData = this.availableJobs.find(j => j.id == job);
        if (jobData) {
          this.selectedJob = jobData;
        }
      }
    }
  },
  
  async mounted() {
    console.log('CandidatePortal mounted - starting to fetch data')
    try {
      await Promise.all([
        this.fetchChatSessions(),
        this.fetchApplications(),
        this.fetchJobs()
      ])

      // Process query parameters after data is loaded
      await this.processQueryParams()
      
      this.scrollToBottom()
    } catch (error) {
      console.error('Error in mounted:', error)
    }
  },

  watch: {
    '$route.query': {
      handler: 'processQueryParams',
      deep: true
    }
  }
}
</script>

<style scoped>
.candidate-portal {
  min-height: calc(100vh - 60px);
  background-color: #f8f9fa;
  padding: 0;
}

.chat-column {
  display: flex;
  flex-direction: column;
  padding: 15px 10px 15px 15px;
  height: calc(100vh - 60px);
}

.chat-card {
  background-color: #f8f9fa !important;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  min-height: 0;
  overflow: hidden;
}

.chat-container {
  overflow-y: auto;
  padding: 1rem;
  background: #f8f9fa;
  position: relative;
  flex: 1;
  min-height: 0;
  max-height: 100%;
}

.empty-chat-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  width: 100%;
  min-height: 200px;
  padding: 2rem;
}

.message-wrapper {
  margin-bottom: 1rem;
}

.message {
  max-width: 85%;
  margin-bottom: 0.5rem;
  display: flex;
  flex-direction: column;
}

.user-message {
  margin-left: auto;
  align-items: flex-end;
}

.assistant-message {
  margin-right: auto;
  align-items: flex-start;
}

.user-message .message-content {
  background: #007bff;
  color: white;
  border-radius: 18px 18px 4px 18px;
  padding: 12px 16px;
  max-width: 100%;
}

.assistant-message .message-content {
  background: white;
  color: #333;
  border-radius: 18px 18px 18px 4px;
  padding: 12px 16px;
  border: 1px solid #e9ecef;
  max-width: 100%;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 0.8rem;
}

.message-text {
  line-height: 1.4;
  word-wrap: break-word;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background: #6c757d;
  border-radius: 50%;
  display: inline-block;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.job-selector-panel {
  background: #f8f9fa !important;
  border-top: 1px solid #dee2e6;
}

.job-card {
  transition: all 0.2s ease;
  cursor: pointer;
}

.job-card:hover {
  background-color: #e9ecef !important;
}

.sessions-card {
  max-height: 400px;
}

.sessions-list {
  max-height: 300px;
  overflow-y: auto;
}

.session-item {
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.session-item:hover {
  background-color: #f8f9fa !important;
  border-left-color: #007bff;
}

.session-item.bg-light {
  border-left-color: #007bff;
}

.cursor-pointer {
  cursor: pointer;
}

.badge-sm {
  font-size: 0.75rem;
}

.card {
  border: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.btn {
  transition: all 0.2s ease;
}

.btn:hover {
  transform: translateY(-1px);
}

/* Input area styling */
.card-footer {
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa !important;
  padding: 0.75rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .chat-column {
    padding: 10px;
  }
  
  .chat-body {
    flex: 1;
  }
  
  .message {
    max-width: 95%;
  }
}

/* Scrollbar styling */
.chat-container::-webkit-scrollbar,
.sessions-list::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-track,
.sessions-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb,
.sessions-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover,
.sessions-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 
