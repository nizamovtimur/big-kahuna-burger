<template>
  <div class="candidate-portal">
    <div class="container-fluid h-100">
      <div class="row h-100">
        <!-- Main Chat Section -->
        <div class="col-lg-8 chat-column">
          <div class="card h-100 border-0 shadow-sm chat-card">
            <!-- Chat Header -->
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center">
                <h5 class="mb-0 me-3">
                  <i class="fas fa-robot"></i> Мой HR Помощник
                </h5>
                <!-- Current Context -->
                <div v-if="selectedJob" class="badge bg-light text-dark">
                  <i class="fas fa-briefcase"></i> {{ selectedJob.title }}
                </div>
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
                <div class="d-flex justify-content-between align-items-center mt-3">
                  <button 
                    class="btn btn-outline-secondary btn-sm"
                    @click="clearJobContext"
                  >
                    Очистить контекст
                  </button>
                  <button 
                    class="btn btn-primary btn-sm"
                    @click="showJobSelector = false"
                  >
                    Готово
                  </button>
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
                  v-if="currentMode === 'apply' && !uploadedFile"
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
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="col-lg-4 sidebar-column">
          <!-- Sessions List (Collapsible) -->
          <div v-if="showSessionsList" class="card border-0 shadow-sm mb-3 sessions-card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h6 class="mb-0">
                <i class="fas fa-history"></i> История чатов
              </h6>
              <button 
                class="btn btn-outline-secondary btn-sm"
                @click="showSessionsList = false"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
            
            <div class="card-body p-0">
              <!-- Search -->
              <div class="p-3 border-bottom">
                <div class="input-group input-group-sm">
                  <input 
                    v-model="sessionSearchTerm" 
                    type="text" 
                    class="form-control" 
                    placeholder="Поиск..."
                  />
                  <button 
                    class="btn btn-outline-secondary" 
                    @click="clearSessionSearch"
                    v-if="sessionSearchTerm"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
              
              <!-- Sessions -->
              <div class="sessions-list">
                <div v-for="(sessions, date) in groupedSessions" :key="date" class="mb-2">
                  <div class="px-3 py-1 bg-light border-bottom">
                    <small class="text-muted fw-bold">
                      {{ formatSessionDate(date) }}
                    </small>
                  </div>
                  
                  <div
                    v-for="session in sessions"
                    :key="session.id"
                    class="session-item p-2 border-bottom cursor-pointer"
                    :class="{ 'bg-light border-primary': currentChatSession?.id === session.id }"
                    @click="loadSession(session.id)"
                  >
                    <div class="d-flex justify-content-between align-items-start">
                      <div class="flex-grow-1">
                        <div class="fw-bold small mb-1">
                          Чат #{{ session.id }}
                          <span v-if="session.job_id" class="badge bg-secondary ms-1">
                            Job #{{ session.job_id }}
                          </span>
                        </div>
                        <div class="text-muted small">
                          {{ formatTime(session.updated_at) }}
                        </div>
                      </div>
                      
                      <button
                        class="btn btn-outline-danger btn-sm"
                        @click.stop="deleteSession(session.id)"
                        title="Удалить"
                      >
                        <i class="fas fa-trash-alt"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Current Job Context -->
          <div class="card border-0 shadow-sm mb-3">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="fas fa-briefcase"></i> Контекст вакансии
              </h6>
            </div>
            <div class="card-body">
              <div v-if="selectedJob">
                <h6>{{ selectedJob.title }}</h6>
                <p class="small text-muted mb-2">{{ selectedJob.location }}</p>
                <div class="small mb-3">
                  <strong>Режим:</strong> 
                  <span class="badge" :class="getModeClass()">
                    {{ getModeText() }}
                  </span>
                </div>
                <div class="d-grid gap-2">
                  <button 
                    class="btn btn-outline-primary btn-sm"
                    @click="changeMode('discussion')"
                  >
                    <i class="fas fa-comments"></i> Обсуждение
                  </button>
                  <button 
                    class="btn btn-sm"
                    :class="hasAppliedToCurrentJob ? 'btn-outline-secondary' : 'btn-outline-success'"
                    @click="changeMode('apply')"
                    :disabled="hasAppliedToCurrentJob"
                  >
                    <i :class="hasAppliedToCurrentJob ? 'fas fa-check' : 'fas fa-paper-plane'"></i> 
                    {{ hasAppliedToCurrentJob ? 'Заявка уже подана' : 'Подать заявку' }}
                  </button>
                </div>
              </div>
              <div v-else>
                <p class="text-muted small mb-3">Выберите вакансию для обсуждения</p>
                <button 
                  class="btn btn-primary btn-sm w-100"
                  @click="showJobSelector = true"
                >
                  <i class="fas fa-briefcase"></i> Выбрать вакансию
                </button>
              </div>
            </div>
          </div>
          
          <!-- Quick Actions -->
          <div class="card border-0 shadow-sm mb-3">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="fas fa-bolt"></i> Быстрые действия
              </h6>
            </div>
            <div class="card-body">
              <div class="d-grid gap-2">
                <button 
                  class="btn btn-outline-primary btn-sm"
                  @click="useExamplePrompt('Расскажите о доступных вакансиях')"
                >
                  <i class="fas fa-list"></i> Список вакансий
                </button>
                <button 
                  class="btn btn-outline-primary btn-sm"
                  @click="useExamplePrompt('Какие льготы в компании?')"
                >
                  <i class="fas fa-gift"></i> Льготы
                </button>
                <button 
                  class="btn btn-outline-primary btn-sm"
                  @click="useExamplePrompt('Как проходит собеседование?')"
                >
                  <i class="fas fa-handshake"></i> Собеседование
                </button>
              </div>
            </div>
          </div>
          
          <!-- My Applications Status -->
          <div class="card border-0 shadow-sm">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="fas fa-clipboard-list"></i> Мои заявки
              </h6>
            </div>
            <div class="card-body">
              <div v-if="applications.length > 0">
                <div 
                  v-for="app in applications.slice(0, 3)" 
                  :key="app.id"
                  class="border-bottom pb-2 mb-2"
                >
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <div class="fw-bold small">Job #{{ app.job_id }}</div>
                      <span class="badge badge-sm" :class="getStatusBadgeClass(app.status)">
                        {{ getStatusText(app.status) }}
                      </span>
                    </div>
                  </div>
                </div>
                <div v-if="applications.length > 3" class="text-center">
                  <small class="text-muted">И еще {{ applications.length - 3 }}...</small>
                </div>
              </div>
              <div v-else class="text-muted small text-center">
                Заявок пока нет
              </div>
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
      currentMode: 'discussion', // 'discussion' or 'apply'
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
    
    groupedSessions() {
      const grouped = {}
      
      this.filteredSessions.forEach(session => {
        const date = new Date(session.updated_at).toISOString().split('T')[0]
        if (!grouped[date]) {
          grouped[date] = []
        }
        grouped[date].push(session)
      })
      
      const sortedGrouped = {}
      Object.keys(grouped)
        .sort((a, b) => new Date(b) - new Date(a))
        .forEach(date => {
          sortedGrouped[date] = grouped[date].sort((a, b) => 
            new Date(b.updated_at) - new Date(a.updated_at)
          )
        })
      
      return sortedGrouped
    },

    hasAppliedToCurrentJob() {
      return this.applications.some(app => app.job_id === this.selectedJob?.id);
    },

    canSendMessage() {
      // Always require at least a message
      if (!this.currentMessage.trim()) return false;
      
      // For apply mode: 
      if (this.currentMode === 'apply') {
        // If user hasn't applied yet AND no file attached, require file
        if (!this.hasAppliedToCurrentJob && !this.uploadedFile) {
          return false;
        }
        // If user already applied OR has file attached, allow message
        return true;
      }
      
      // For other modes: require only message
      return true;
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
          jobId: this.selectedJob?.id || null,
          mode: this.currentMode
        }
        
        // If we have a file in apply mode, add it to the message
        if (this.uploadedFile && this.currentMode === 'apply') {
          messageData.file = this.uploadedFile
        }
        
        const result = await this.sendChatMessage(messageData)
        
        console.log('Message sent, result:', result)
        
        // Check if we just submitted an application
        const hadUploadedFile = !!this.uploadedFile;
        const isApplyMode = this.currentMode === 'apply';
        
        this.currentMessage = ''
        this.uploadedFile = null
        
        // If we sent a file in apply mode, refresh applications to update hasAppliedToCurrentJob
        if (hadUploadedFile && isApplyMode) {
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
      this.$store.commit('SET_CURRENT_CHAT_SESSION', null)
      this.scrollToBottom()
    },
    
    async loadSession(sessionId) {
      try {
        await this.fetchChatSession(sessionId)
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
    
    clearJobContext() {
      this.selectedJob = null
      this.currentMode = 'discussion'
      this.showJobSelector = false
      this.showFileUpload = false
      this.uploadedFile = null
    },

    selectJob(job) {
      this.selectedJob = job;
      this.showJobSelector = false;
      this.currentMode = 'discussion';
      this.showFileUpload = false;
      this.uploadedFile = null;
    },

    changeMode(mode) {
      this.currentMode = mode;
      this.showFileUpload = false;
      this.uploadedFile = null;
    },

    getModeClass() {
      switch (this.currentMode) {
        case 'discussion': return 'bg-primary text-white';
        case 'apply': return 'bg-success text-white';
        default: return 'bg-secondary';
      }
    },

    getModeText() {
      switch (this.currentMode) {
        case 'discussion': return 'Обсуждение';
        case 'apply': return 'Подача заявки';
        default: return 'Неизвестный режим';
      }
    },

    getEmptyStateTitle() {
      if (this.selectedJob) {
        if (this.currentMode === 'apply') {
          return 'Подача заявки';
        } else {
          return 'Обсуждение вакансии';
        }
      }
      return 'Начните новую беседу';
    },

    getEmptyStateSubtitle() {
      if (this.selectedJob) {
        if (this.currentMode === 'apply') {
          return 'Прикрепите резюме и расскажите о себе';
        } else {
          return 'Задайте вопрос о вакансии: ' + this.selectedJob.title;
        }
      }
      return 'Выберите вакансию или задайте общий вопрос';
    },

    getInputPlaceholder() {
      if (this.currentMode === 'apply') {
        // If user already applied, they can send follow-up messages
        if (this.hasAppliedToCurrentJob) {
          return 'Отвечайте на вопросы HR-агента...';
        }
        // If user hasn't applied yet
        if (this.uploadedFile) {
          return 'Резюме прикреплено! Напишите сопроводительное письмо и отправьте...';
        } else {
          return 'Прикрепите резюме и напишите сопроводительное письмо...';
        }
      }
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

    getStatusBadgeClass(status) {
      switch (status) {
        case 'approved': return 'bg-success';
        case 'rejected': return 'bg-danger';
        case 'pending': return 'bg-warning';
        default: return 'bg-secondary';
      }
    },

    getStatusText(status) {
      switch (status) {
        case 'approved': return 'Одобрено';
        case 'rejected': return 'Отклонено';
        case 'pending': return 'Ожидается';
        default: return status;
      }
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
      const { job, mode, application_id } = this.$route.query;
      
      if (job) {
        // Find job in available jobs
        const jobData = this.availableJobs.find(j => j.id == job);
        if (jobData) {
          this.selectedJob = jobData;
        }
      }
      
      if (mode) {
        this.currentMode = mode;
      }
      
      // If it's apply mode, show file upload
      if (mode === 'apply') {
        this.showFileUpload = true;
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
  min-height: calc(100vh - 120px);
  background-color: #f8f9fa;
  padding: 0;
}

.h-100 {
  height: calc(100vh - 120px) !important;
  max-height: calc(100vh - 120px) !important;
}

.chat-column {
  display: flex;
  flex-direction: column;
  padding: 15px 10px 15px 15px;
  height: calc(100vh - 120px);
}

.sidebar-column {
  display: flex;
  flex-direction: column;
  padding: 15px 15px 15px 10px;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
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
  .chat-column,
  .sidebar-column {
    padding: 10px;
  }
  
  .chat-body {
    flex: 1;
  }
  
  .message {
    max-width: 95%;
  }
  
  .sidebar-column {
    max-height: none;
  }
}

/* Scrollbar styling */
.chat-container::-webkit-scrollbar,
.sessions-list::-webkit-scrollbar,
.sidebar-column::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-track,
.sessions-list::-webkit-scrollbar-track,
.sidebar-column::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb,
.sessions-list::-webkit-scrollbar-thumb,
.sidebar-column::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover,
.sessions-list::-webkit-scrollbar-thumb:hover,
.sidebar-column::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 
