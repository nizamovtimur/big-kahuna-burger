<template>
  <div class="candidate-portal">
    <div class="container-fluid h-100">
      <div class="row h-100">
        <!-- Job Listings Sidebar -->
        <div class="col-lg-4 bg-light border-end">
          <div class="p-4">
            <h4 class="mb-4">
              <i class="fas fa-briefcase me-2"></i>Available Jobs
            </h4>
            
            <!-- Job Filters -->
            <div class="mb-4">
              <div class="row g-2">
                <div class="col">
                  <input 
                    v-model="filters.department" 
                    type="text" 
                    class="form-control form-control-sm" 
                    placeholder="Department"
                    @input="filterJobs"
                  >
                </div>
                <div class="col">
                  <input 
                    v-model="filters.location" 
                    type="text" 
                    class="form-control form-control-sm" 
                    placeholder="Location"
                    @input="filterJobs"
                  >
                </div>
              </div>
            </div>

            <!-- Job List -->
            <div class="job-list" style="max-height: 60vh; overflow-y: auto;">
              <div 
                v-for="job in filteredJobList" 
                :key="job.id"
                class="card mb-3 job-card"
                :class="{ 'border-primary': selectedJob?.id === job.id }"
                @click="selectJob(job)"
                style="cursor: pointer;"
              >
                <div class="card-body p-3">
                  <h6 class="card-title mb-1">{{ job.title }}</h6>
                  <small class="text-muted d-block">{{ job.department }}</small>
                  <small class="text-muted d-block">
                    <i class="fas fa-map-marker-alt me-1"></i>{{ job.location }}
                  </small>
                  <div class="mt-2" v-if="job.salary_min && job.salary_max">
                    <small class="badge bg-success">
                      ${{ job.salary_min.toLocaleString() }} - ${{ job.salary_max.toLocaleString() }}
                    </small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Interface -->
        <div class="col-lg-8 d-flex flex-column">
          <div class="p-4 border-bottom bg-white">
            <h4 class="mb-2">
              <i class="fas fa-robot me-2 text-primary"></i>AI Career Assistant
            </h4>
            <p class="text-muted mb-0">
              Ask me anything about our job openings, company culture, or application process!
            </p>
            <div v-if="selectedJob" class="mt-2">
              <small class="badge bg-primary">
                Discussing: {{ selectedJob.title }}
              </small>
            </div>
          </div>

          <!-- Chat Messages -->
          <div class="flex-grow-1 p-4 chat-container" style="overflow-y: auto; max-height: 50vh;">
            <div v-if="chatMessages.length === 0" class="text-center text-muted py-5">
              <i class="fas fa-comments fa-3x mb-3"></i>
              <p>Start a conversation! Ask me about jobs, benefits, or anything else.</p>
            </div>
            
            <div v-for="(message, index) in chatMessages" :key="index" class="mb-3">
              <div 
                class="d-flex"
                :class="message.role === 'user' ? 'justify-content-end' : 'justify-content-start'"
              >
                <div 
                  class="message p-3 rounded"
                  :class="message.role === 'user' ? 'bg-primary text-white user-message' : 'bg-light assistant-message'"
                  style="max-width: 70%;"
                >
                  {{ message.content }}
                </div>
              </div>
            </div>
            
            <div v-if="isTyping" class="d-flex justify-content-start mb-3">
              <div class="bg-light p-3 rounded">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Chat Input -->
          <div class="p-4 border-top bg-white">
            <form @submit.prevent="sendMessage">
              <div class="input-group">
                <input 
                  v-model="newMessage" 
                  type="text" 
                  class="form-control" 
                  placeholder="Type your message..." 
                  :disabled="isTyping"
                >
                <button 
                  class="btn btn-primary" 
                  type="submit" 
                  :disabled="!newMessage.trim() || isTyping"
                >
                  <i class="fas fa-paper-plane"></i>
                </button>
              </div>
            </form>
            
            <!-- Quick Actions -->
            <div class="mt-3">
              <small class="text-muted d-block mb-2">Quick questions:</small>
              <div class="d-flex flex-wrap gap-2">
                <button 
                  class="btn btn-outline-secondary btn-sm" 
                  @click="sendQuickMessage('Tell me about company benefits')"
                  :disabled="isTyping"
                >
                  Benefits
                </button>
                <button 
                  class="btn btn-outline-secondary btn-sm" 
                  @click="sendQuickMessage('What is the application process?')"
                  :disabled="isTyping"
                >
                  Application Process
                </button>
                <button 
                  class="btn btn-outline-secondary btn-sm" 
                  @click="sendQuickMessage('Tell me about company culture')"
                  :disabled="isTyping"
                >
                  Company Culture
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Application Modal -->
    <div class="modal fade" id="applicationModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Apply for {{ selectedJob?.title }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitApplication">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input v-model="applicationForm.fullName" type="text" class="form-control" required>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="applicationForm.email" type="email" class="form-control" required>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input v-model="applicationForm.phone" type="tel" class="form-control">
              </div>
              
              <div class="mb-3">
                <label class="form-label">Cover Letter</label>
                <textarea v-model="applicationForm.coverLetter" class="form-control" rows="4"></textarea>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Resume (paste text)</label>
                <textarea v-model="applicationForm.resume" class="form-control" rows="6" placeholder="Paste your resume text here..."></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="submitApplication">Submit Application</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex'

export default {
  name: 'CandidatePortal',
  data() {
    return {
      newMessage: '',
      isTyping: false,
      selectedJob: null,
      filters: {
        department: '',
        location: ''
      },
      filteredJobList: [],
      applicationForm: {
        fullName: '',
        email: '',
        phone: '',
        coverLetter: '',
        resume: ''
      }
    }
  },
  computed: {
    ...mapGetters(['allJobs']),
    ...mapState(['chatMessages'])
  },
  methods: {
    ...mapActions(['fetchJobs', 'chatWithAI', 'createApplicant', 'submitApplication']),
    
    async sendMessage() {
      if (!this.newMessage.trim()) return
      
      const message = this.newMessage.trim()
      this.newMessage = ''
      this.isTyping = true
      
      try {
        await this.chatWithAI({
          message,
          jobId: this.selectedJob?.id,
          applicantEmail: this.applicationForm.email || null
        })
      } catch (error) {
        console.error('Chat error:', error)
      } finally {
        this.isTyping = false
        this.scrollToBottom()
      }
    },
    
    sendQuickMessage(message) {
      this.newMessage = message
      this.sendMessage()
    },
    
    selectJob(job) {
      this.selectedJob = job
    },
    
    filterJobs() {
      this.filteredJobList = this.allJobs.filter(job => {
        const departmentMatch = !this.filters.department || 
          job.department.toLowerCase().includes(this.filters.department.toLowerCase())
        const locationMatch = !this.filters.location || 
          job.location.toLowerCase().includes(this.filters.location.toLowerCase())
        return departmentMatch && locationMatch
      })
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const chatContainer = document.querySelector('.chat-container')
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight
        }
      })
    },
    
    async submitApplication() {
      // Create applicant profile first
      const applicantResult = await this.createApplicant({
        email: this.applicationForm.email,
        full_name: this.applicationForm.fullName,
        phone: this.applicationForm.phone,
        resume_text: this.applicationForm.resume
      })
      
      if (applicantResult.success && this.selectedJob) {
        // Submit application
        const applicationResult = await this.submitApplication({
          applicantId: applicantResult.applicant.id,
          applicationData: {
            job_id: this.selectedJob.id,
            cover_letter: this.applicationForm.coverLetter
          }
        })
        
        if (applicationResult.success) {
          alert('Application submitted successfully!')
          // Close modal
          const modal = document.getElementById('applicationModal')
          const bsModal = new bootstrap.Modal(modal)
          bsModal.hide()
          
          // Reset form
          this.applicationForm = {
            fullName: '',
            email: '',
            phone: '',
            coverLetter: '',
            resume: ''
          }
        }
      }
    }
  },
  
  async mounted() {
    await this.fetchJobs()
    this.filterJobs()
  },
  
  watch: {
    chatMessages() {
      this.scrollToBottom()
    }
  }
}
</script>

<style scoped>
.candidate-portal {
  height: calc(100vh - 76px); /* Account for navbar */
}

.job-card:hover {
  background-color: #f8f9fa;
}

.user-message {
  background-color: #007bff !important;
}

.assistant-message {
  background-color: #f8f9fa;
}

.typing-indicator {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-container {
  background-color: #fafafa;
}
</style> 