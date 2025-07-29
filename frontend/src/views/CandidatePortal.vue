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
                  @click="showChatHistory = !showChatHistory"
                  title="История диалогов"
                >
                  <i class="fas fa-history"></i>
                </button>
                <button 
                  class="btn btn-outline-light btn-sm"
                  @click="clearChat"
                  title="Очистить чат"
                >
                  <i class="fas fa-broom"></i>
                </button>
                <button 
                  class="btn btn-outline-light btn-sm"
                  @click="exportChat"
                  title="Экспорт истории"
                >
                  <i class="fas fa-download"></i>
                </button>
              </div>
            </div>
            
            <!-- Chat Messages -->
            <div class="card-body p-0">
              <div class="chat-container" ref="chatContainer">
                <div 
                  v-for="message in chatHistory" 
                  :key="message.id || Math.random()"
                  class="message-wrapper"
                >
                  <!-- User Message -->
                  <div class="message user-message">
                    <div class="message-content">
                      <div class="message-header">
                        <strong>You</strong>
                        <small class="text-muted">{{ formatTime(message.created_at) }}</small>
                      </div>
                      <div class="message-text" v-html="message.user_message"></div>
                    </div>
                  </div>
                  
                  <!-- AI Response -->
                  <div class="message ai-message">
                    <div class="message-content">
                      <div class="message-header">
                        <strong><i class="fas fa-robot"></i> Big Kahuna AI</strong>
                        <small class="text-muted">{{ formatTime(message.created_at) }}</small>
                      </div>
                      <div class="message-text" v-html="message.ai_response"></div>
                    </div>
                  </div>
                </div>
                
                <!-- Loading indicator -->
                <div v-if="sendingMessage" class="message ai-message">
                  <div class="message-content">
                    <div class="message-header">
                      <strong><i class="fas fa-robot"></i> Big Kahuna AI</strong>
                    </div>
                    <div class="typing-indicator">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Message Input -->
            <div class="card-footer">
              <form @submit.prevent="sendMessage">
                <div class="input-group">
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="currentMessage"
                    placeholder="Спросите о вакансиях, корпоративной культуре, льготах..."
                    :disabled="sendingMessage"
                  >
                  <button 
                    type="submit" 
                    class="btn btn-primary"
                    :disabled="!currentMessage.trim() || sendingMessage"
                  >
                    <i class="fas fa-paper-plane"></i>
                  </button>
                </div>
                

              </form>
            </div>
          </div>
        </div>
        
        <!-- Sidebar -->
        <div class="col-lg-4">
          <!-- Chat History Panel -->
          <div v-if="showChatHistory" class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
              <h6 class="mb-0">
                <i class="fas fa-history"></i> История диалогов
              </h6>
              <button 
                class="btn btn-outline-light btn-sm"
                @click="showChatHistory = false"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="card-body p-2">
              <!-- Search -->
              <div class="mb-3">
                <div class="input-group input-group-sm">
                  <input 
                    type="text" 
                    class="form-control" 
                    placeholder="Поиск в истории..."
                    v-model="historySearchTerm"
                  >
                  <button class="btn btn-outline-secondary" @click="clearHistorySearch">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
              
              <!-- Chat Sessions by Date -->
              <div class="chat-sessions" style="max-height: 400px; overflow-y: auto;">
                <div v-for="(sessions, date) in groupedChatHistory" :key="date" class="mb-3">
                  <h6 class="text-muted small mb-2">{{ formatHistoryDate(date) }}</h6>
                                     <div 
                     v-for="session in sessions" 
                     :key="session.id || session.created_at"
                     class="chat-session-item p-2 border rounded mb-2 cursor-pointer"
                     :class="{ 'border-primary bg-light': selectedChatSession?.id === session.id || selectedChatSession?.created_at === session.created_at }"
                     @click="loadChatSession(session)"
                   >
                    <div class="d-flex justify-content-between align-items-start">
                      <div class="flex-grow-1">
                        <div class="small fw-bold text-truncate">
                          {{ session.user_message.substring(0, 50) }}{{ session.user_message.length > 50 ? '...' : '' }}
                        </div>
                        <div class="small text-muted">
                          <i class="fas fa-clock"></i> {{ formatTime(session.created_at) }}
                          <span v-if="session.job_id" class="badge bg-secondary ms-1">Вакансия</span>
                        </div>
                      </div>
                                             <button 
                         class="btn btn-outline-danger btn-sm"
                         @click.stop="deleteChatSession(session.id || session.created_at)"
                         title="Удалить"
                       >
                         <i class="fas fa-trash"></i>
                       </button>
                    </div>
                  </div>
                </div>
                
                <div v-if="Object.keys(groupedChatHistory).length === 0" class="text-center text-muted small">
                  <i class="fas fa-search"></i>
                  <p class="mb-0">История диалогов пуста</p>
                </div>
              </div>
            </div>
          </div>
          
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
      showChatHistory: false,
      historySearchTerm: '',
      selectedChatSession: null,
      vulnerabilityInfo: `Vulnerabilities Present:
1. Direct prompt injection in user messages
2. XSS via unescaped HTML in chat display  
3. No rate limiting on AI requests
4. System prompt can be overridden
5. Sensitive context leaked in responses`
    }
  },
  computed: {
    ...mapGetters(['chatHistory', 'applications']),
    
    filteredChatHistory() {
      if (!this.historySearchTerm.trim()) {
        return this.chatHistory
      }
      
      const searchTerm = this.historySearchTerm.toLowerCase()
      return this.chatHistory.filter(session => 
        session.user_message.toLowerCase().includes(searchTerm) ||
        session.ai_response.toLowerCase().includes(searchTerm)
      )
    },
    
    groupedChatHistory() {
      const grouped = {}
      
      this.filteredChatHistory.forEach(session => {
        const date = new Date(session.created_at).toISOString().split('T')[0]
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
            new Date(b.created_at) - new Date(a.created_at)
          )
        })
      
      return sortedGrouped
    }
  },
  methods: {
    ...mapActions(['sendChatMessage', 'fetchChatHistory', 'fetchApplications']),
    
    async sendMessage() {
      if (!this.currentMessage.trim()) return
      
      try {
        this.sendingMessage = true
        
        await this.sendChatMessage({
          message: this.currentMessage,
          job_id: this.selectedJob?.id || null
        })
        
        this.currentMessage = ''
        this.scrollToBottom()
      } catch (error) {
        alert('Не удалось отправить сообщение: ' + error.message)
      } finally {
        this.sendingMessage = false
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
    },

    clearHistorySearch() {
      this.historySearchTerm = ''
    },

    formatHistoryDate(dateString) {
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
          month: 'long',
          year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
        })
      }
    },

    loadChatSession(session) {
      this.selectedChatSession = session
      // Можно добавить функцию для отображения конкретного диалога
      // или перехода к нему в основном чате
    },

    async deleteChatSession(sessionId) {
      if (confirm('Удалить этот диалог? Это действие нельзя отменить.')) {
        try {
          await this.$store.dispatch('deleteChatSession', sessionId)
          
          if (this.selectedChatSession?.id === sessionId) {
            this.selectedChatSession = null
          }
          
          // Show success message
          this.$nextTick(() => {
            // Simple success feedback
            const button = event.target.closest('.chat-session-item')
            if (button) {
              button.style.opacity = '0.5'
              button.style.pointerEvents = 'none'
            }
          })
        } catch (error) {
          alert('Не удалось удалить диалог: ' + error.message)
        }
      }
    },

    async clearChat() {
      if (confirm('Очистить всю историю чатов? Это действие нельзя отменить.')) {
        try {
          await this.$store.dispatch('clearAllChatHistory')
          this.selectedChatSession = null
          this.showChatHistory = false
        } catch (error) {
          alert('Не удалось очистить историю: ' + error.message)
        }
      }
    },

    async exportChat() {
      try {
        // Use backend export functionality
        const exportData = await this.$store.dispatch('exportChatHistory')
        
        const dataStr = JSON.stringify(exportData, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        
        const link = document.createElement('a')
        link.href = URL.createObjectURL(dataBlob)
        link.download = `big-kahuna-chat-export-${new Date().toISOString().split('T')[0]}.json`
        link.click()
        
        // Cleanup
        setTimeout(() => URL.revokeObjectURL(link.href), 100)
        
        // Show success message
        alert(`Экспорт завершен! Сохранено ${exportData.total_sessions} диалогов.`)
        
      } catch (error) {
        console.error('Export error:', error)
        // Fallback to local export
        try {
          const chatData = {
            exported_at: new Date().toISOString(),
            total_messages: this.chatHistory.length,
            conversations: this.chatHistory.map(session => ({
              timestamp: session.created_at,
              user_message: session.user_message,
              ai_response: session.ai_response,
              job_context: session.job_id ? `Job ID: ${session.job_id}` : null
            }))
          }
          
          const dataStr = JSON.stringify(chatData, null, 2)
          const dataBlob = new Blob([dataStr], { type: 'application/json' })
          
          const link = document.createElement('a')
          link.href = URL.createObjectURL(dataBlob)
          link.download = `chat-history-local-${new Date().toISOString().split('T')[0]}.json`
          link.click()
          
          setTimeout(() => URL.revokeObjectURL(link.href), 100)
          
        } catch (fallbackError) {
          alert('Не удалось экспортировать историю: ' + error.message)
        }
      }
    }
  },
  
  async mounted() {
    await this.fetchChatHistory()
    await this.fetchApplications()
    this.scrollToBottom()
    
    // Check for job context from query params
    const jobId = this.$route.query.job
    if (jobId) {
      try {
        this.selectedJob = await this.$store.dispatch('fetchJobById', jobId)
      } catch (error) {
        console.error('Failed to load job context:', error)
      }
    }
  }
}
</script>

<style scoped>
.candidate-portal {
  background-color: #f8f9fa;
  min-height: 100vh;
  padding: 20px 0;
}

.chat-container {
  height: 500px;
  overflow-y: auto;
  padding: 20px;
  background-color: #fafafa;
}

.message-wrapper {
  margin-bottom: 20px;
}

.message {
  margin-bottom: 10px;
}

.message-content {
  max-width: 80%;
  padding: 10px 15px;
  border-radius: 18px;
  position: relative;
}

.user-message .message-content {
  background-color: #007bff;
  color: white;
  margin-left: auto;
  text-align: right;
}

.ai-message .message-content {
  background-color: white;
  border: 1px solid #dee2e6;
  color: #333;
}

.message-header {
  font-size: 0.8em;
  margin-bottom: 5px;
  opacity: 0.8;
}

/* WARNING: Styles that enable XSS */
.message-text {
  /* Raw HTML rendering - XSS vulnerability */
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
  background-color: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.badge-sm {
  font-size: 0.75em;
  padding: 0.25em 0.5em;
}

pre {
  font-size: 0.8em;
  white-space: pre-wrap;
}

/* Chat History Styles */
.chat-session-item {
  transition: all 0.2s ease;
  cursor: pointer;
}

.chat-session-item:hover {
  background-color: #f8f9fa !important;
  border-color: #0d6efd !important;
}

.chat-session-item.border-primary {
  background-color: #e7f3ff !important;
}

.cursor-pointer {
  cursor: pointer;
}
</style> 