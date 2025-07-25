<template>
  <div class="hr-dashboard">
    <div class="container py-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="fw-bold">HR Dashboard</h1>
          <p class="text-muted">Welcome back, {{ currentUser?.full_name }}</p>
        </div>
        <div>
          <router-link to="/hr/jobs" class="btn btn-primary me-2">
            <i class="fas fa-plus me-1"></i>New Job
          </router-link>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row g-4 mb-5">
        <div class="col-md-3">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h3 class="fw-bold">{{ stats.totalJobs }}</h3>
                  <p class="mb-0">Active Jobs</p>
                </div>
                <i class="fas fa-briefcase fa-2x opacity-75"></i>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="card bg-success text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h3 class="fw-bold">{{ stats.totalApplications }}</h3>
                  <p class="mb-0">Applications</p>
                </div>
                <i class="fas fa-file-alt fa-2x opacity-75"></i>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="card bg-warning text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h3 class="fw-bold">{{ stats.pendingReviews }}</h3>
                  <p class="mb-0">Pending Review</p>
                </div>
                <i class="fas fa-clock fa-2x opacity-75"></i>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="card bg-info text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h3 class="fw-bold">{{ stats.totalApplicants }}</h3>
                  <p class="mb-0">Total Applicants</p>
                </div>
                <i class="fas fa-users fa-2x opacity-75"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="row">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Recent Applications</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Applicant</th>
                      <th>Position</th>
                      <th>Status</th>
                      <th>Applied</th>
                      <th>Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="application in recentApplications" :key="application.id">
                      <td>{{ application.applicant?.full_name || 'N/A' }}</td>
                      <td>{{ application.job?.title || 'N/A' }}</td>
                      <td>
                        <span 
                          class="badge"
                          :class="getStatusBadgeClass(application.status)"
                        >
                          {{ application.status }}
                        </span>
                      </td>
                      <td>{{ formatDate(application.submitted_at) }}</td>
                      <td>
                        <span v-if="application.ai_match_score" class="badge bg-secondary">
                          {{ Math.round(application.ai_match_score) }}%
                        </span>
                        <span v-else class="text-muted">-</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-lg-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Quick Actions</h5>
            </div>
            <div class="card-body">
              <div class="d-grid gap-2">
                <router-link to="/hr/jobs" class="btn btn-outline-primary">
                  <i class="fas fa-plus me-2"></i>Create New Job
                </router-link>
                <router-link to="/hr/applications" class="btn btn-outline-info">
                  <i class="fas fa-list me-2"></i>Review Applications
                </router-link>
                <button class="btn btn-outline-success" @click="exportData">
                  <i class="fas fa-download me-2"></i>Export Reports
                </button>
              </div>
            </div>
          </div>
          
          <div class="card mt-4">
            <div class="card-header">
              <h5 class="mb-0">System Status</h5>
            </div>
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span>Database</span>
                <span class="badge bg-success">Online</span>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span>AI Services</span>
                <span class="badge bg-success">Active</span>
              </div>
              <div class="d-flex justify-content-between align-items-center">
                <span>Last Backup</span>
                <span class="text-muted small">2 hours ago</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'HRDashboard',
  data() {
    return {
      stats: {
        totalJobs: 0,
        totalApplications: 0,
        pendingReviews: 0,
        totalApplicants: 0
      },
      recentApplications: []
    }
  },
  computed: {
    ...mapGetters(['currentUser', 'allJobs'])
  },
  methods: {
    ...mapActions(['fetchJobs', 'fetchApplications']),
    
    getStatusBadgeClass(status) {
      const classes = {
        'submitted': 'bg-primary',
        'reviewing': 'bg-warning',
        'interview': 'bg-info',
        'hired': 'bg-success',
        'rejected': 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    },
    
    exportData() {
      alert('Export functionality would be implemented here')
    }
  },
  
  async mounted() {
    await this.fetchJobs()
    this.stats.totalJobs = this.allJobs.length
    
    // Mock data for demo
    this.stats.totalApplications = 45
    this.stats.pendingReviews = 12
    this.stats.totalApplicants = 38
    
    this.recentApplications = [
      {
        id: 1,
        applicant: { full_name: 'John Smith' },
        job: { title: 'Burger Specialist' },
        status: 'submitted',
        submitted_at: new Date().toISOString(),
        ai_match_score: 85
      },
      {
        id: 2,
        applicant: { full_name: 'Sarah Johnson' },
        job: { title: 'Shift Manager' },
        status: 'reviewing',
        submitted_at: new Date(Date.now() - 86400000).toISOString(),
        ai_match_score: 92
      }
    ]
  }
}
</script>

<style scoped>
.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.opacity-75 {
  opacity: 0.75;
}
</style> 