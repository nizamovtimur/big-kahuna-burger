<template>
  <div class="hr-applications">
    <div class="container py-4">
      <h1 class="fw-bold mb-4">Applications</h1>

      <!-- Filters -->
      <div class="card mb-4">
        <div class="card-body">
          <div class="row">
            <div class="col-md-3">
              <select v-model="statusFilter" class="form-select">
                <option value="">All Statuses</option>
                <option value="submitted">Submitted</option>
                <option value="reviewing">Reviewing</option>
                <option value="interview">Interview</option>
                <option value="hired">Hired</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
            <div class="col-md-3">
              <select v-model="jobFilter" class="form-select">
                <option value="">All Jobs</option>
                <option v-for="job in allJobs" :key="job.id" :value="job.id">
                  {{ job.title }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <input v-model="searchTerm" type="text" class="form-control" placeholder="Search applicants...">
            </div>
            <div class="col-md-3">
              <button class="btn btn-outline-secondary" @click="clearFilters">
                <i class="fas fa-times me-1"></i>Clear
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Applications Table -->
      <div class="card">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Applicant</th>
                  <th>Position</th>
                  <th>Status</th>
                  <th>AI Score</th>
                  <th>Applied</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="application in mockApplications" :key="application.id">
                  <td>
                    <div>
                      <strong>{{ application.applicant_name }}</strong>
                      <br>
                      <small class="text-muted">{{ application.applicant_email }}</small>
                    </div>
                  </td>
                  <td>{{ application.job_title }}</td>
                  <td>
                    <select 
                      v-model="application.status" 
                      class="form-select form-select-sm"
                      @change="updateStatus(application)"
                    >
                      <option value="submitted">Submitted</option>
                      <option value="reviewing">Reviewing</option>
                      <option value="interview">Interview</option>
                      <option value="hired">Hired</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </td>
                  <td>
                    <span v-if="application.ai_score" class="badge bg-secondary">
                      {{ application.ai_score }}%
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td>{{ formatDate(application.applied_date) }}</td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary" @click="viewApplication(application)">
                      <i class="fas fa-eye"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Application Detail Modal -->
    <div class="modal fade" id="applicationModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Application Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedApplication">
            <div class="row">
              <div class="col-md-6">
                <h6>Applicant Information</h6>
                <p><strong>Name:</strong> {{ selectedApplication.applicant_name }}</p>
                <p><strong>Email:</strong> {{ selectedApplication.applicant_email }}</p>
                <p><strong>Phone:</strong> {{ selectedApplication.phone || 'Not provided' }}</p>
              </div>
              <div class="col-md-6">
                <h6>Application Details</h6>
                <p><strong>Position:</strong> {{ selectedApplication.job_title }}</p>
                <p><strong>Applied:</strong> {{ formatDate(selectedApplication.applied_date) }}</p>
                <p><strong>AI Match Score:</strong> 
                  <span v-if="selectedApplication.ai_score" class="badge bg-success">
                    {{ selectedApplication.ai_score }}%
                  </span>
                  <span v-else>Not analyzed</span>
                </p>
              </div>
            </div>
            
            <hr>
            
            <h6>Cover Letter</h6>
            <p>{{ selectedApplication.cover_letter || 'No cover letter provided' }}</p>
            
            <h6>Resume</h6>
            <div class="bg-light p-3 rounded">
              <pre style="white-space: pre-wrap;">{{ selectedApplication.resume || 'No resume provided' }}</pre>
            </div>
            
            <h6 v-if="selectedApplication.ai_analysis">AI Analysis</h6>
            <div v-if="selectedApplication.ai_analysis" class="alert alert-info">
              {{ selectedApplication.ai_analysis }}
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-success" @click="updateApplicationStatus('interview')">
              Schedule Interview
            </button>
            <button type="button" class="btn btn-danger" @click="updateApplicationStatus('rejected')">
              Reject
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'HRApplications',
  data() {
    return {
      statusFilter: '',
      jobFilter: '',
      searchTerm: '',
      selectedApplication: null,
      // Mock data for demonstration
      mockApplications: [
        {
          id: 1,
          applicant_name: 'John Smith',
          applicant_email: 'john.smith@email.com',
          phone: '+1-555-0123',
          job_title: 'Burger Specialist',
          status: 'submitted',
          ai_score: 85,
          applied_date: new Date().toISOString(),
          cover_letter: 'I am very interested in this position...',
          resume: 'John Smith\nExperience: 3 years in food service...',
          ai_analysis: 'Strong candidate with relevant experience in food service. Good communication skills demonstrated in cover letter.'
        },
        {
          id: 2,
          applicant_name: 'Sarah Johnson',
          applicant_email: 'sarah.j@email.com',
          phone: '+1-555-0456',
          job_title: 'Shift Manager',
          status: 'reviewing',
          ai_score: 92,
          applied_date: new Date(Date.now() - 86400000).toISOString(),
          cover_letter: 'With my management experience...',
          resume: 'Sarah Johnson\nManagement Experience: 5 years...',
          ai_analysis: 'Excellent candidate with strong management background. Highly recommended for interview.'
        }
      ]
    }
  },
  computed: {
    ...mapGetters(['allJobs'])
  },
  methods: {
    ...mapActions(['fetchJobs']),
    
    clearFilters() {
      this.statusFilter = ''
      this.jobFilter = ''
      this.searchTerm = ''
    },
    
    updateStatus(application) {
      // Implementation would call API to update status
      console.log('Updating status for application', application.id, 'to', application.status)
    },
    
    viewApplication(application) {
      this.selectedApplication = application
      const modal = new window.bootstrap.Modal(document.getElementById('applicationModal'))
      modal.show()
    },
    
    updateApplicationStatus(status) {
      if (this.selectedApplication) {
        this.selectedApplication.status = status
        this.updateStatus(this.selectedApplication)
        // Close modal
        const modal = window.bootstrap.Modal.getInstance(document.getElementById('applicationModal'))
        modal.hide()
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  },
  
  async mounted() {
    await this.fetchJobs()
  }
}
</script> 