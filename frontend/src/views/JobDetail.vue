<template>
  <div class="job-detail-page">
    <div class="container py-4">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Loading job details...</p>
      </div>

      <!-- Job Details -->
      <div v-else-if="job" class="row">
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-4">
                <div>
                  <h1 class="h2 mb-2">{{ job.title }}</h1>
                  <div class="text-muted">
                    <i class="fas fa-map-marker-alt"></i> {{ job.location }}
                    <span class="mx-2">•</span>
                    <i class="fas fa-dollar-sign"></i> {{ job.salary_range }}
                  </div>
                </div>
                <span class="badge bg-success fs-6">Active</span>
              </div>

              <div class="row mb-4">
                <div class="col">
                  <h3>Job Description</h3>
                  <div class="job-content" v-html="job.description"></div>
                </div>
              </div>

              <div class="row mb-4">
                <div class="col">
                  <h3>Requirements</h3>
                  <div class="job-content" v-html="job.requirements"></div>
                </div>
              </div>

              <div v-if="job.additional_info" class="row mb-4">
                <div class="col">
                  <h3>Additional Information</h3>
                  <div class="alert alert-info" v-html="job.additional_info"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <!-- Apply Section -->
          <div v-if="isAuthenticated" class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-success text-white">
              <h5 class="mb-0">
                <i class="fas fa-paper-plane"></i> Apply for this Position
              </h5>
            </div>
            <div class="card-body">
              <button 
                class="btn btn-success w-100 mb-3"
                @click="showApplicationForm = true"
                :disabled="hasApplied"
              >
                <i class="fas fa-file-upload"></i>
                {{ hasApplied ? 'Already Applied' : 'Submit Application' }}
              </button>
              
              <hr>
              
              <h6>Quick Chat with AI</h6>
              <p class="small text-muted mb-3">
                Ask our AI assistant about this position
              </p>
              <router-link 
                :to="`/candidate-portal?job=${job.id}`" 
                class="btn btn-outline-primary w-100"
              >
                <i class="fas fa-robot"></i> Chat About This Job
              </router-link>
            </div>
          </div>

          <!-- Login Prompt -->
          <div v-else class="card border-0 shadow-sm mb-4">
            <div class="card-body text-center">
              <i class="fas fa-lock fa-3x text-muted mb-3"></i>
              <h5>Login Required</h5>
              <p class="text-muted">Please login to apply for this position</p>
              <router-link to="/login" class="btn btn-primary">
                <i class="fas fa-sign-in-alt"></i> Login
              </router-link>
            </div>
          </div>

          <!-- Job Info -->
          <div class="card border-0 shadow-sm">
            <div class="card-header">
              <h6 class="mb-0">Job Information</h6>
            </div>
            <div class="card-body">
              <ul class="list-unstyled mb-0">
                <li class="mb-2">
                  <strong>Location:</strong> {{ job.location }}
                </li>
                <li class="mb-2">
                  <strong>Salary:</strong> {{ job.salary_range }}
                </li>
                <li class="mb-2">
                  <strong>Posted:</strong> {{ formatDate(job.created_at) }}
                </li>
                <li>
                  <strong>Job ID:</strong> {{ job.id }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Application Modal -->
      <div v-if="showApplicationForm" class="modal d-block" style="background-color: rgba(0,0,0,0.5)">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Apply for {{ job?.title }}</h5>
              <button 
                type="button" 
                class="btn-close" 
                @click="showApplicationForm = false"
              ></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="submitApplication">
                <div class="mb-3">
                  <label for="coverLetter" class="form-label">Cover Letter *</label>
                  <textarea 
                    class="form-control" 
                    id="coverLetter"
                    v-model="applicationForm.cover_letter"
                    rows="5"
                    required
                    placeholder="Tell us why you're interested in this position..."
                  ></textarea>
                  <div class="form-text text-muted">
                    <small>Share your motivation and relevant experience for this role</small>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="cvFile" class="form-label">CV/Resume *</label>
                  <input 
                    type="file" 
                    class="form-control" 
                    id="cvFile"
                    @change="handleFileUpload"
                    accept=".pdf,.doc,.docx"
                    required
                  >
                  <div class="form-text text-muted">
                    <small>Accepted formats: PDF, DOC, DOCX (max 10MB)</small>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="additionalInfo" class="form-label">Additional Information</label>
                  <textarea 
                    class="form-control" 
                    id="additionalInfo"
                    v-model="applicationForm.additional_info"
                    rows="3"
                    placeholder="Any additional information you'd like to share..."
                  ></textarea>
                </div>

                <div class="d-grid gap-2">
                  <button type="submit" class="btn btn-success" :disabled="submitting">
                    <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                    <i class="fas fa-paper-plane"></i> Submit Application
                  </button>
                  <button 
                    type="button" 
                    class="btn btn-secondary" 
                    @click="showApplicationForm = false"
                  >
                    Cancel
                  </button>
                </div>
              </form>
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
  name: 'JobDetail',
  props: ['id'],
  data() {
    return {
      job: null,
      loading: true,
      showApplicationForm: false,
      submitting: false,
      hasApplied: false,
      applicationForm: {
        cover_letter: '',
        additional_info: '',
        cv_file: null
      }
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated'])
  },
  methods: {
    ...mapActions(['fetchJobById', 'submitApplication']),
    
    async loadJob() {
      try {
        this.job = await this.fetchJobById(this.id)
      } catch (error) {
        console.error('Failed to load job:', error)
        this.$router.push('/jobs')
      } finally {
        this.loading = false
      }
    },
    
    handleFileUpload(event) {
      this.applicationForm.cv_file = event.target.files[0]
    },
    
    async submitApplication() {
      if (!this.applicationForm.cv_file) {
        alert('Please select a CV file')
        return
      }
      
      try {
        this.submitting = true
        
        const applicationData = {
          job_id: this.job.id,
          cover_letter: this.applicationForm.cover_letter,
          additional_answers: {
            additional_info: this.applicationForm.additional_info
          },
          cv_file: this.applicationForm.cv_file
        }
        
        await this.submitApplication(applicationData)
        
        this.showApplicationForm = false
        this.hasApplied = true
        
        alert('Application submitted successfully!')
      } catch (error) {
        alert('Failed to submit application: ' + error.message)
      } finally {
        this.submitting = false
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  },
  
  async created() {
    await this.loadJob()
  }
}
</script>

<style scoped>
.job-detail-page {
  background-color: #f8f9fa;
  min-height: 100vh;
}

/* WARNING: Styles that allow XSS */
.job-content {
  /* Raw HTML rendering - XSS vulnerability */
  line-height: 1.6;
}

.modal {
  display: block;
}

.card {
  border: none;
}
</style> 