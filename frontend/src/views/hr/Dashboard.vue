<template>
  <div class="hr-dashboard">
    <div class="container py-4">
      <h1 class="display-6 mb-4">
        <i class="fas fa-chart-line text-primary"></i> HR Dashboard
      </h1>
      
      <!-- Statistics Cards -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <i class="fas fa-file-alt fa-2x text-primary mb-2"></i>
              <h3 class="mb-1">{{ applicationStats.total || 0 }}</h3>
              <small class="text-muted">Total Applications</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <i class="fas fa-clock fa-2x text-warning mb-2"></i>
              <h3 class="mb-1">{{ applicationStats.pending || 0 }}</h3>
              <small class="text-muted">Pending Review</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <i class="fas fa-check-circle fa-2x text-success mb-2"></i>
              <h3 class="mb-1">{{ applicationStats.accepted || 0 }}</h3>
              <small class="text-muted">Accepted</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <i class="fas fa-briefcase fa-2x text-info mb-2"></i>
              <h3 class="mb-1">{{ jobStats.active || 0 }}</h3>
              <small class="text-muted">Active Jobs</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Applications -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">
                <i class="fas fa-clock"></i> Recent Applications
              </h5>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-3">
                <div class="spinner-border text-primary" role="status"></div>
              </div>
              <div v-else-if="recentApplications.length > 0">
                <div class="table-responsive">
                  <table class="table table-sm mb-0">
                    <thead>
                      <tr>
                        <th>Candidate</th>
                        <th>Job</th>
                        <th>Score</th>
                        <th>Status</th>
                        <th>Applied</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="app in recentApplications.slice(0, 5)" :key="app.id">
                        <td>{{ app.user?.full_name || 'Unknown' }}</td>
                        <td>{{ app.job?.title || 'N/A' }}</td>
                        <td>
                          <span class="badge" :class="getScoreBadgeClass(app.cv_score)">
                            {{ app.cv_score || 'N/A' }}/10
                          </span>
                        </td>
                        <td>
                          <span class="badge" :class="getStatusBadgeClass(app.status)">
                            {{ app.status }}
                          </span>
                        </td>
                        <td>{{ formatDate(app.applied_at) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div v-else class="text-center text-muted py-3">
                <i class="fas fa-inbox fa-2x mb-2"></i>
                <p>No applications yet</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Action Cards -->
      <div class="row">
        <div class="col-md-6">
          <router-link to="/hr/applications" class="card border-0 shadow-sm text-decoration-none">
            <div class="card-body text-center">
              <i class="fas fa-file-alt fa-3x text-success mb-3"></i>
              <h5>Review Applications</h5>
              <p class="text-muted">Manage and review job applications from candidates</p>
            </div>
          </router-link>
        </div>
        <div class="col-md-6">
          <router-link to="/hr/jobs" class="card border-0 shadow-sm text-decoration-none">
            <div class="card-body text-center">
              <i class="fas fa-briefcase fa-3x text-primary mb-3"></i>
              <h5>Manage Jobs</h5>
              <p class="text-muted">Create, edit, and manage job postings</p>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import axios from 'axios'

export default {
  name: 'HRDashboard',
  data() {
    return {
      loading: false,
      recentApplications: [],
      applicationStats: {
        total: 0,
        pending: 0,
        accepted: 0,
        rejected: 0
      },
      jobStats: {
        active: 0,
        total: 0
      }
    }
  },
  computed: {
    ...mapGetters(['isHR'])
  },
  methods: {
    async fetchDashboardData() {
      try {
        this.loading = true
        
        // Fetch applications
        const applicationsResponse = await axios.get('/applicants/hr')
        this.recentApplications = applicationsResponse.data || []
        
        // Calculate statistics
        this.applicationStats.total = this.recentApplications.length
        this.applicationStats.pending = this.recentApplications.filter(app => app.status === 'pending').length
        this.applicationStats.accepted = this.recentApplications.filter(app => app.status === 'accepted').length
        this.applicationStats.rejected = this.recentApplications.filter(app => app.status === 'rejected').length
        
        // Fetch jobs
        const jobsResponse = await axios.get('/jobs/')
        const jobs = jobsResponse.data.jobs || []
        this.jobStats.active = jobs.filter(job => job.is_active).length
        this.jobStats.total = jobs.length
        
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        this.loading = false
      }
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
    await this.fetchDashboardData()
  }
}
</script> 