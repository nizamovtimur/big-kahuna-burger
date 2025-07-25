<template>
  <div class="job-detail">
    <div class="container py-5">
      <div v-if="job" class="row">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-body">
              <h1 class="fw-bold mb-3">{{ job.title }}</h1>
              <div class="mb-4">
                <span class="badge bg-primary me-2">{{ job.department }}</span>
                <span class="badge bg-secondary me-2">{{ job.location }}</span>
                <span v-if="job.salary_min && job.salary_max" class="badge bg-success">
                  ${{ job.salary_min.toLocaleString() }} - ${{ job.salary_max.toLocaleString() }}
                </span>
              </div>
              
              <h5>Job Description</h5>
              <p class="mb-4">{{ job.description }}</p>
              
              <h5 v-if="job.requirements">Requirements</h5>
              <p v-if="job.requirements" class="mb-4">{{ job.requirements }}</p>
              
              <div class="mt-4">
                <router-link to="/candidate" class="btn btn-primary btn-lg me-3">
                  <i class="fas fa-paper-plane me-2"></i>Apply Now
                </router-link>
                <router-link to="/candidate" class="btn btn-outline-info btn-lg">
                  <i class="fas fa-comments me-2"></i>Chat About This Job
                </router-link>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-lg-4">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Job Information</h5>
              <ul class="list-unstyled">
                <li class="mb-2">
                  <strong>Department:</strong> {{ job.department }}
                </li>
                <li class="mb-2">
                  <strong>Location:</strong> {{ job.location }}
                </li>
                <li class="mb-2">
                  <strong>Posted:</strong> {{ formatDate(job.created_at) }}
                </li>
                <li v-if="job.salary_min && job.salary_max" class="mb-2">
                  <strong>Salary:</strong> ${{ job.salary_min.toLocaleString() }} - ${{ job.salary_max.toLocaleString() }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Loading -->
      <div v-else-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      
      <!-- Error -->
      <div v-else class="text-center py-5">
        <h3 class="text-muted">Job not found</h3>
        <router-link to="/jobs" class="btn btn-primary">Browse All Jobs</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex'

export default {
  name: 'JobDetail',
  props: ['id'],
  data() {
    return {
      job: null
    }
  },
  computed: {
    ...mapState(['loading'])
  },
  methods: {
    ...mapActions(['fetchJob']),
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  },
  async mounted() {
    try {
      this.job = await this.fetchJob(this.id)
    } catch (error) {
      console.error('Error loading job:', error)
    }
  }
}
</script> 