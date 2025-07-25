<template>
  <div class="hr-applications">
    <div class="container py-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="display-6 mb-0">
          <i class="fas fa-file-alt text-primary"></i> Application Management
        </h1>
        <router-link to="/hr/dashboard" class="btn btn-secondary">
          <i class="fas fa-arrow-left"></i> Back to Dashboard
        </router-link>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading applications...</span>
        </div>
      </div>

      <!-- Applications List -->
      <div v-else-if="applications.length > 0" class="row">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">
                <i class="fas fa-list"></i> All Applications ({{ applications.length }})
              </h5>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Candidate</th>
                      <th>Job Title</th>
                      <th>CV Score</th>
                      <th>Applied Date</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="application in applications" :key="application.id">
                      <td>
                        <div>
                          <strong>{{ application.user?.full_name || 'Unknown' }}</strong><br>
                          <small class="text-muted">{{ application.user?.email || 'N/A' }}</small>
                        </div>
                      </td>
                      <td>
                        <div>
                          <strong>{{ application.job?.title || 'Job not found' }}</strong><br>
                          <small class="text-muted">{{ application.job?.location || '' }}</small>
                        </div>
                      </td>
                      <td>
                        <span class="badge" :class="getScoreBadgeClass(application.cv_score)">
                          {{ application.cv_score || 'N/A' }}/10
                        </span>
                      </td>
                      <td>
                        <small>{{ formatDate(application.applied_at) }}</small>
                      </td>
                      <td>
                        <span class="badge" :class="getStatusBadgeClass(application.status)">
                          {{ application.status }}
                        </span>
                      </td>
                      <td>
                        <div class="btn-group" role="group">
                          <button 
                            class="btn btn-sm btn-outline-primary"
                            @click="viewApplication(application)"
                          >
                            <i class="fas fa-eye"></i> View
                          </button>
                          <div class="dropdown">
                            <button 
                              class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                              type="button" 
                              data-bs-toggle="dropdown"
                            >
                              Status
                            </button>
                            <ul class="dropdown-menu">
                              <li><a class="dropdown-item" href="#" @click.prevent="updateStatus(application.id, 'pending')">Pending</a></li>
                              <li><a class="dropdown-item" href="#" @click.prevent="updateStatus(application.id, 'reviewing')">Reviewing</a></li>
                              <li><a class="dropdown-item" href="#" @click.prevent="updateStatus(application.id, 'interview')">Interview</a></li>
                              <li><a class="dropdown-item" href="#" @click.prevent="updateStatus(application.id, 'accepted')">Accepted</a></li>
                              <li><a class="dropdown-item" href="#" @click.prevent="updateStatus(application.id, 'rejected')">Rejected</a></li>
                            </ul>
                          </div>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Applications -->
      <div v-else class="text-center py-5">
        <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
        <h4 class="text-muted">No Applications Yet</h4>
        <p class="text-muted">When candidates apply for jobs, they'll appear here.</p>
      </div>

      <!-- Application Detail Modal -->
      <div class="modal fade" id="applicationModal" tabindex="-1" v-if="selectedApplication">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                Application Details - {{ selectedApplication.user?.full_name }}
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="row">
                <div class="col-md-6">
                  <h6>Candidate Information</h6>
                  <p><strong>Name:</strong> {{ selectedApplication.user?.full_name }}</p>
                  <p><strong>Email:</strong> {{ selectedApplication.user?.email }}</p>
                  <p><strong>Username:</strong> {{ selectedApplication.user?.username }}</p>
                </div>
                <div class="col-md-6">
                  <h6>Application Details</h6>
                  <p><strong>Job:</strong> {{ selectedApplication.job?.title }}</p>
                  <p><strong>CV Score:</strong> {{ selectedApplication.cv_score }}/10</p>
                  <p><strong>Status:</strong> {{ selectedApplication.status }}</p>
                  <p><strong>Applied:</strong> {{ formatDate(selectedApplication.applied_at) }}</p>
                </div>
              </div>
              
              <div class="mt-3">
                <h6>Cover Letter</h6>
                <div class="border rounded p-3 bg-light" v-html="selectedApplication.cover_letter"></div>
              </div>
              
              <div class="mt-3" v-if="selectedApplication.additional_answers">
                <h6>Additional Information</h6>
                <div class="border rounded p-3 bg-light">
                  <pre>{{ JSON.stringify(selectedApplication.additional_answers, null, 2) }}</pre>
                </div>
              </div>

              <div class="mt-3" v-if="selectedApplication.cv_filename">
                <h6>CV File</h6>
                <p><i class="fas fa-file-pdf text-danger"></i> {{ selectedApplication.cv_filename }}</p>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import axios from 'axios'

export default {
  name: 'HRApplications',
  data() {
    return {
      loading: false,
      applications: [],
      selectedApplication: null
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'isHR'])
  },
  methods: {
    ...mapActions(['logout']),
    
         async fetchApplications() {
       try {
         this.loading = true
         const response = await axios.get('/applicants/hr')
         this.applications = response.data
       } catch (error) {
         console.error('Failed to fetch applications:', error)
         if (error.response?.status === 401) {
           this.logout()
           this.$router.push('/login')
         }
       } finally {
         this.loading = false
       }
     },

     async updateStatus(applicationId, newStatus) {
       try {
         await axios.put(`/applicants/${applicationId}/status`, {
           status: newStatus,
           feedback: `Status updated to ${newStatus} by HR`
         })
        
        // Update local application
        const app = this.applications.find(a => a.id === applicationId)
        if (app) {
          app.status = newStatus
        }
        
        this.$toast?.success(`Application status updated to ${newStatus}`)
      } catch (error) {
        console.error('Failed to update status:', error)
        alert('Failed to update application status')
      }
    },

    viewApplication(application) {
      this.selectedApplication = application
      const modal = new bootstrap.Modal(document.getElementById('applicationModal'))
      modal.show()
    },

    getStatusBadgeClass(status) {
      switch (status) {
        case 'pending': return 'bg-warning text-dark'
        case 'reviewing': return 'bg-info'
        case 'interview': return 'bg-primary'
        case 'accepted': return 'bg-success'
        case 'rejected': return 'bg-danger'
        default: return 'bg-secondary'
      }
    },

    getScoreBadgeClass(score) {
      if (!score) return 'bg-secondary'
      if (score >= 8) return 'bg-success'
      if (score >= 6) return 'bg-warning text-dark'
      if (score >= 4) return 'bg-info'
      return 'bg-danger'
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  },

  async created() {
    if (!this.isHR) {
      this.$router.push('/')
      return
    }
    await this.fetchApplications()
  }
}
</script> 