<template>
  <div class="candidate-portal">
    <div class="container-fluid">
      <div class="row">
        <!-- Chat Section -->
        <div class="col-lg-8">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="fas fa-robot"></i> Мой HR Помощник - Big Kahuna AI
              </h5>
              <div class="btn-group">
                <button 
                  class="btn btn-outline-light btn-sm"
                  @click="showSessionsList = !showSessionsList"
                  title="Список сессий"
                >
                  <i class="fas fa-list"></i>
                </button>
                <button 
                  class="btn btn-outline-light btn-sm"
                  @click="startNewSession"
                  title="Новая сессия"
                >
                  <i class="fas fa-plus"></i>
                </button>
                <button 
                  class="btn btn-outline-light btn-sm"
                  @click="clearAllSessions"
                  title="Очистить все сессии"
                >
                  <i class="fas fa-broom"></i>
                </button>
                <button 
                  class="btn btn-outline-light btn-sm"
                  @click="exportSessions"
                  title="Экспорт сессий"
                >
                  <i class="fas fa-download"></i>
                </button>
              </div>
            </div>
            
            <!-- Chat Messages -->
            <div class="card-body p-0 d-flex flex-column" style="height: calc(100vh - 350px);">
              <div class="chat-container flex-grow-1" ref="chatContainer">
                <div v-if="currentSessionMessages.length === 0" class="empty-chat-state">
                  <i class="fas fa-comments fa-3x mb-3 text-muted"></i>
                  <h5 class="text-muted">Начните новую беседу</h5>
                  <p class="text-muted small mb-0">Задайте вопрос о вакансиях, компании или процессе найма</p>
                </div>
                
                <div 
                  v-for="message in currentSessionMessages" 
                  :key="message.id"
                  class="message-wrapper"
                >
                  <!-- User or Assistant Message -->
                  <div class="message" :class="message.role + '-message'">
                    <div class="message-content">
                      <div class="message-header">
                        <strong>{{ message.role === 'user' ? 'You' : 'Big Kahuna AI' }}</strong>
                        <small class="text-muted">{{ formatTime(message.created_at) }}</small>
                      </div>
                      <div class="message-text" v-html="message.content"></div>
                    </div>
                  </div>
                </div>
                
                <!-- Loading indicator -->
                <div v-if="sendingMessage" class="message-wrapper">
                  <div class="message assistant-message">
                    <div class="message-content">
                      <div class="message-header">
                        <strong>Big Kahuna AI</strong>
                        <small class="text-muted">typing...</small>
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
              <!-- Job Context Display -->
              <div v-if="selectedJob" class="alert alert-info alert-sm mb-2 d-flex justify-content-between align-items-center">
                <span>
                  <i class="fas fa-briefcase"></i>
                  Контекст: {{ selectedJob.title }}
                </span>
                <button class="btn btn-sm btn-outline-secondary" @click="clearJobContext">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              
              <div class="input-group">
                <input 
                  v-model="currentMessage" 
                  type="text" 
                  class="form-control" 
                  placeholder="Напишите сообщение..." 
                  @keyup.enter="sendMessage"
                  :disabled="sendingMessage"
                />
                <button 
                  class="btn btn-primary" 
                  @click="sendMessage"
                  :disabled="sendingMessage || !currentMessage.trim()"
                >
                  <i class="fas fa-paper-plane"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Sessions List Panel -->
        <div v-if="showSessionsList" class="col-lg-4">
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h6 class="mb-0">
                <i class="fas fa-history"></i> Сессии чата
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
                    placeholder="Поиск в сессиях..."
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
              
              <!-- Sessions by Date -->
              <div class="sessions-list" style="max-height: 400px; overflow-y: auto;">
                <div v-for="(sessions, date) in groupedSessions" :key="date" class="mb-3">
                  <div class="px-3 py-2 bg-light border-bottom">
                    <small class="text-muted fw-bold">
                      {{ formatSessionDate(date) }}
                    </small>
                  </div>
                  
                  <div
                    v-for="session in sessions"
                    :key="session.id"
                    class="session-item p-3 border-bottom cursor-pointer position-relative"
                    :class="{ 'bg-light border-primary': currentChatSession?.id === session.id }"
                    @click="loadSession(session.id)"
                  >
                    <div class="d-flex justify-content-between align-items-start">
                      <div class="flex-grow-1">
                        <div class="fw-bold small mb-1">
                          Сессия #{{ session.id }}
                          <span v-if="session.job_id" class="badge bg-secondary ms-1">
                            Job #{{ session.job_id }}
                          </span>
                        </div>
                        <div class="text-muted small">
                          {{ formatTime(session.updated_at) }}
                        </div>
                        <div v-if="session.title" class="small text-truncate mt-1">
                          {{ session.title }}
                        </div>
                      </div>
                      
                      <button
                        class="btn btn-outline-danger btn-sm ms-2"
                        @click.stop="deleteSession(session.id)"
                        title="Удалить сессию"
                      >
                        <i class="fas fa-trash-alt"></i>
                      </button>
                    </div>
                  </div>
                </div>
                
                <div v-if="Object.keys(groupedSessions).length === 0" class="text-center text-muted small p-3">
                  <i class="fas fa-comments fa-2x mb-2"></i>
                  <p class="mb-0">Нет сессий</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Sidebar -->
        <div :class="showSessionsList ? 'col-lg-12 mt-4' : 'col-lg-4'">
          <!-- Job Context -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header">
              <h6 class="mb-0">Контекст вакансии</h6>
            </div>
            <div class="card-body">
              <div v-if="selectedJob">
                <h6>{{ selectedJob.title }}</h6>
                <p class="small text-muted">{{ selectedJob.location }}</p>
                <button 
                  class="btn btn-outline-secondary btn-sm"
                  @click="clearJobContext"
                >
                  Очистить контекст
                </button>
              </div>
              <div v-else>
                <p class="text-muted small">Вакансия не выбрана. Обсуждайте общие темы.</p>
                <router-link to="/jobs" class="btn btn-primary btn-sm">
                  Просмотреть вакансии
                </router-link>
              </div>
            </div>
          </div>
          
          <!-- Quick Actions -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header">
              <h6 class="mb-0">Быстрые действия</h6>
            </div>
            <div class="card-body">
              <div class="d-grid gap-2">
                <button 
                  class="btn btn-outline-primary btn-sm"
                  @click="useExamplePrompt('Расскажите о доступных вакансиях в Big Kahuna Burger')"
                >
                  <i class="fas fa-briefcase"></i> Посмотреть вакансии
                </button>
                <button 
                  class="btn btn-outline-primary btn-sm"
                  @click="useExamplePrompt('Какие льготы и бонусы предоставляет компания?')"
                >
                  <i class="fas fa-gift"></i> Узнать о льготах
                </button>
                <button 
                  class="btn btn-outline-primary btn-sm"
                  @click="useExamplePrompt('Расскажите о корпоративной культуре Big Kahuna Burger')"
                >
                  <i class="fas fa-users"></i> Корпоративная культура
                </button>
                <button 
                  class="btn btn-outline-primary btn-sm"
                  @click="useExamplePrompt('Как проходит процесс собеседования?')"
                >
                  <i class="fas fa-handshake"></i> Процесс найма
                </button>
              </div>
            </div>
          </div>
          
          <!-- My Applications -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header">
              <h6 class="mb-0">Мои заявки</h6>
            </div>
            <div class="card-body">
              <div v-if="applications.length > 0">
                <div 
                  v-for="app in applications" 
                  :key="app.id"
                  class="border-bottom pb-2 mb-2 last:border-0"
                >
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 class="small mb-1">Заявка #{{ app.id }}</h6>
                      <p class="small text-muted mb-1">ID вакансии: {{ app.job_id }}</p>
                      <span class="badge badge-sm" :class="getStatusBadgeClass(app.status)">
                        {{ app.status }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-muted small">
                Заявок пока нет.
              </div>
            </div>
          </div>
          
          <!-- Chat Help -->
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-info text-white">
              <h6 class="mb-0">
                <i class="fas fa-question-circle"></i> Нужна помощь?
              </h6>
            </div>
            <div class="card-body">
              <p class="small">
                Наш ИИ-помощник может помочь вам с:
              </p>
              <ul class="small mb-0">
                <li>Описанием вакансий и требованиями</li>
                <li>Корпоративной культурой и льготами</li>
                <li>Вопросами о процессе подачи заявок</li>
                <li>Возможностями карьерного развития</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'CandidatePortal',
  data() {
    return {
      currentMessage: '',
      sendingMessage: false,
      selectedJob: null,
      showVulnerabilityDetails: false,
      showSessionsList: false,
      sessionSearchTerm: '',
      vulnerabilityInfo: `Vulnerabilities Present:
1. Direct prompt injection in user messages
2. XSS via unescaped HTML in chat display  
3. No rate limiting on AI requests
4. System prompt can be overridden
5. Sensitive context leaked in responses`
    }
  },
  computed: {
    ...mapGetters(['chatSessions', 'currentChatSession', 'applications']),
    
    currentSessionMessages() {
      return this.currentChatSession?.messages || []
    },
    
    filteredSessions() {
      if (!this.sessionSearchTerm.trim()) {
        return this.chatSessions
      }
      
      const searchTerm = this.sessionSearchTerm.toLowerCase()
      return this.chatSessions.filter(session => {
        // Search in session title or job context
        const titleMatch = session.title?.toLowerCase().includes(searchTerm)
        const jobMatch = session.job_id?.toString().includes(searchTerm)
        
        // Search in messages if session has them loaded
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
      
      // Sort dates descending (newest first)
      const sortedGrouped = {}
      Object.keys(grouped)
        .sort((a, b) => new Date(b) - new Date(a))
        .forEach(date => {
          sortedGrouped[date] = grouped[date].sort((a, b) => 
            new Date(b.updated_at) - new Date(a.updated_at)
          )
        })
      
      return sortedGrouped
    }
  },
  methods: {
    ...mapActions(['sendChatMessage', 'fetchChatSessions', 'fetchChatSession', 'fetchApplications', 'deleteChatSession', 'clearAllChatSessions']),
    
    async sendMessage() {
      if (!this.currentMessage.trim()) return
      
      try {
        this.sendingMessage = true
        console.log('Sending message:', this.currentMessage)
        console.log('Current session ID:', this.currentChatSession?.id)
        console.log('Selected job ID:', this.selectedJob?.id)
        
        const result = await this.sendChatMessage({
          message: this.currentMessage,
          sessionId: this.currentChatSession?.id || null,
          jobId: this.selectedJob?.id || null
        })
        
        console.log('Message sent, result:', result)
        this.currentMessage = ''
        this.scrollToBottom()
      } catch (error) {
        console.error('Failed to send message:', error)
        alert('Не удалось отправить сообщение: ' + error.message)
      } finally {
        this.sendingMessage = false
      }
    },
    
    async startNewSession() {
      // Clear current session to start fresh
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
    },
    
    getStatusBadgeClass(status) {
      switch (status) {
        case 'approved': return 'bg-success'
        case 'rejected': return 'bg-danger'
        case 'pending': return 'bg-warning'
        default: return 'bg-secondary'
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
    }
  },
  
  async mounted() {
    console.log('CandidatePortal mounted - starting to fetch data')
    try {
      await this.fetchChatSessions()
      console.log('Chat sessions fetched:', this.chatSessions)
      await this.fetchApplications()
      console.log('Applications fetched:', this.applications)
      this.scrollToBottom()
    } catch (error) {
      console.error('Error in mounted:', error)
    }
  }
}
</script>

<style scoped>
.candidate-portal {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 0;
}

.chat-container {
  overflow-y: auto;
  padding: 1rem;
  background: #f8f9fa;
  position: relative;
  min-height: 400px;
}

.empty-chat-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  width: 100%;
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

.alert-sm {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.badge-sm {
  font-size: 0.75rem;
}

/* Card height adjustments */
.card.h-100 {
  height: calc(100vh - 40px) !important;
}

/* Input area styling */
.card-footer {
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
  padding: 1rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .card.h-100 {
    height: auto !important;
    min-height: 600px;
  }
  
  .card-body {
    height: 400px !important;
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