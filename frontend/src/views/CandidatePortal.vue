<template>
  <div class="candidate-portal">
    <div class="container-fluid">
      <div class="row">
        <!-- Chat Section -->
        <div class="col-lg-8">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">
                <i class="fas fa-robot"></i> Chat with Big Kahuna AI Assistant
              </h5>
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
                    placeholder="Ask me about job openings, company culture, benefits..."
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
          <!-- Job Context -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header">
              <h6 class="mb-0">Job Context</h6>
            </div>
            <div class="card-body">
              <div v-if="selectedJob">
                <h6>{{ selectedJob.title }}</h6>
                <p class="small text-muted">{{ selectedJob.location }}</p>
                <button 
                  class="btn btn-outline-secondary btn-sm"
                  @click="clearJobContext"
                >
                  Clear Context
                </button>
              </div>
              <div v-else>
                <p class="text-muted small">No job selected. Chat about general topics.</p>
                <router-link to="/jobs" class="btn btn-primary btn-sm">
                  Browse Jobs
                </router-link>
              </div>
            </div>
          </div>
          
          <!-- My Applications -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header">
              <h6 class="mb-0">My Applications</h6>
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
                      <h6 class="small mb-1">Application #{{ app.id }}</h6>
                      <p class="small text-muted mb-1">Job ID: {{ app.job_id }}</p>
                      <span class="badge badge-sm" :class="getStatusBadgeClass(app.status)">
                        {{ app.status }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-muted small">
                No applications yet.
              </div>
            </div>
          </div>
          
          <!-- Chat Help -->
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-info text-white">
              <h6 class="mb-0">
                <i class="fas fa-question-circle"></i> Need Help?
              </h6>
            </div>
            <div class="card-body">
              <p class="small">
                Our AI assistant can help you with:
              </p>
              <ul class="small mb-0">
                <li>Job descriptions and requirements</li>
                <li>Company culture and benefits</li>
                <li>Application process questions</li>
                <li>Career development opportunities</li>
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
      vulnerabilityInfo: `Vulnerabilities Present:
1. Direct prompt injection in user messages
2. XSS via unescaped HTML in chat display  
3. No rate limiting on AI requests
4. System prompt can be overridden
5. Sensitive context leaked in responses`
    }
  },
  computed: {
    ...mapGetters(['chatHistory', 'applications'])
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
        alert('Failed to send message: ' + error.message)
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
</style> 