<template>
  <div class="jobs-page">
    <div class="container py-5">
      <div class="text-center mb-5">
        <h1 class="display-5 fw-bold">Current Job Openings</h1>
        <p class="lead text-muted">Find your perfect career opportunity at Big Kahuna Burger</p>
      </div>

      <!-- Search and Filters -->
      <div class="row mb-4">
        <div class="col-md-4">
          <input 
            v-model="searchTerm" 
            type="text" 
            class="form-control" 
            placeholder="Search jobs..."
            @input="filterJobs"
          >
        </div>
        <div class="col-md-3">
          <select v-model="selectedDepartment" class="form-select" @change="filterJobs">
            <option value="">All Departments</option>
            <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
          </select>
        </div>
        <div class="col-md-3">
          <select v-model="selectedLocation" class="form-select" @change="filterJobs">
            <option value="">All Locations</option>
            <option v-for="location in locations" :key="location" :value="location">{{ location }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <button class="btn btn-outline-secondary w-100" @click="clearFilters">
            <i class="fas fa-times me-1"></i>Clear
          </button>
        </div>
      </div>

      <!-- Job Listings -->
      <div class="row g-4">
        <div class="col-lg-6 col-xl-4" v-for="job in filteredJobs" :key="job.id">
          <div class="card h-100 shadow-sm">
            <div class="card-body">
              <h5 class="card-title">{{ job.title }}</h5>
              <div class="mb-2">
                <span class="badge bg-primary me-2">{{ job.department }}</span>
                <span class="badge bg-secondary">{{ job.location }}</span>
              </div>
              <p class="card-text text-muted small">
                {{ job.description.substring(0, 120) }}...
              </p>
              <div class="mb-3" v-if="job.salary_min && job.salary_max">
                <small class="text-success fw-bold">
                  <i class="fas fa-dollar-sign me-1"></i>
                  ${{ job.salary_min.toLocaleString() }} - ${{ job.salary_max.toLocaleString() }}
                </small>
              </div>
            </div>
            <div class="card-footer bg-transparent">
              <router-link :to="`/jobs/${job.id}`" class="btn btn-primary w-100">
                View Details
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- No Results -->
      <div v-if="filteredJobs.length === 0" class="text-center py-5">
        <i class="fas fa-search fa-3x text-muted mb-3"></i>
        <h3 class="text-muted">No jobs found</h3>
        <p class="text-muted">Try adjusting your search criteria</p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex'

export default {
  name: 'Jobs',
  data() {
    return {
      searchTerm: '',
      selectedDepartment: '',
      selectedLocation: '',
      filteredJobs: []
    }
  },
  computed: {
    ...mapGetters(['allJobs']),
    ...mapState(['loading']),
    departments() {
      return [...new Set(this.allJobs.map(job => job.department))]
    },
    locations() {
      return [...new Set(this.allJobs.map(job => job.location))]
    }
  },
  methods: {
    ...mapActions(['fetchJobs']),
    
    filterJobs() {
      this.filteredJobs = this.allJobs.filter(job => {
        const matchesSearch = !this.searchTerm || 
          job.title.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
          job.description.toLowerCase().includes(this.searchTerm.toLowerCase())
        
        const matchesDepartment = !this.selectedDepartment || 
          job.department === this.selectedDepartment
        
        const matchesLocation = !this.selectedLocation || 
          job.location === this.selectedLocation
        
        return matchesSearch && matchesDepartment && matchesLocation
      })
    },
    
    clearFilters() {
      this.searchTerm = ''
      this.selectedDepartment = ''
      this.selectedLocation = ''
      this.filterJobs()
    }
  },
  
  async mounted() {
    await this.fetchJobs()
    this.filterJobs()
  },
  
  watch: {
    allJobs() {
      this.filterJobs()
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-2px);
}
</style> 