<template>
  <div class="jobs-page">
    <div class="container py-4">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col">
          <h1 class="display-6 mb-3">
            <i class="fas fa-briefcase text-primary"></i> Возможности трудоустройства
          </h1>
          <p class="lead">Откройте для себя захватывающие карьерные возможности в Big Kahuna Burger!</p>
        </div>
      </div>

      <!-- Search Section -->
      <div class="row mb-4">
        <div class="col">
          <div class="card border-primary">
            <div class="card-header bg-primary text-white">
              <h5 class="card-title mb-0">
                <i class="fas fa-search"></i> Поиск вакансий
              </h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="performSearch">
                <div class="row g-3">
                  <div class="col-md-8">
                    <div class="form-floating">
                      <input 
                        type="text" 
                        class="form-control" 
                        id="searchTerm"
                        v-model="searchForm.search_term"
                        placeholder="Поиск вакансий..."
                      >
                      <label for="searchTerm">Поисковый запрос</label>
                    </div>
                  </div>
                  <div class="col-md-2">
                    <button type="submit" class="btn btn-primary h-100 w-100" style="background-color: #0d6efd; border-color: #0d6efd;">
                      <i class="fas fa-search"></i> Поиск
                    </button>
                  </div>
                  <div class="col-md-2">
                    <button type="button" class="btn btn-outline-secondary h-100 w-100" @click="resetSearch">
                      <i class="fas fa-times"></i> Сброс
                    </button>
                  </div>
                </div>

              </form>
            </div>
          </div>
        </div>
      </div>



      <!-- Loading -->
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="mt-2">Загрузка вакансий...</p>
      </div>

      <!-- Jobs Grid -->
      <div v-else class="row g-4">
        <div v-for="job in jobs" :key="job.id" class="col-lg-6 col-xl-4">
          <div class="card h-100 shadow-sm border-0">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <h5 class="card-title">{{ job.title }}</h5>
                <span class="badge bg-success">Активна</span>
              </div>
              
                              <div class="job-description mb-3" v-html="job.description"></div>
              
              <div class="mb-3">
                <h6 class="text-muted mb-2">Требования:</h6>
                <div class="small" v-html="job.requirements"></div>
              </div>
              
              <div class="row text-muted small mb-3">
                <div class="col">
                  <i class="fas fa-map-marker-alt"></i> {{ job.location }}
                </div>
                <div class="col text-end">
                  <i class="fas fa-dollar-sign"></i> {{ job.salary_range }}
                </div>
              </div>
              
              <div v-if="job.additional_info" class="alert alert-info small" v-html="job.additional_info"></div>
            </div>
            
            <div class="card-footer bg-transparent">
              <div class="d-grid gap-2">
                <router-link 
                  :to="`/jobs/${job.id}`" 
                  class="btn btn-primary"
                >
                  <i class="fas fa-eye"></i> Подробнее
                </router-link>
                <button 
                  v-if="isAuthenticated" 
                  class="btn"
                  :class="hasAppliedToJob(job.id) ? 'btn-outline-secondary' : 'btn-outline-success'"
                  @click="quickApply(job.id)"
                  :disabled="hasAppliedToJob(job.id)"
                >
                  <i :class="hasAppliedToJob(job.id) ? 'fas fa-check' : 'fas fa-paper-plane'"></i> 
                  {{ hasAppliedToJob(job.id) ? 'Заявка уже подана' : 'Быстрая подача' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Jobs -->
      <div v-if="!loading && jobs.length === 0" class="text-center py-5">
        <i class="fas fa-briefcase display-1 text-muted mb-3"></i>
        <h3 class="text-muted">Нет доступных вакансий</h3>
        <p class="text-muted">Загляните позже для поиска новых возможностей!</p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Jobs',
  data() {
    return {
      searchForm: {
        search_term: ''
      }
    }
  },
  computed: {
    ...mapGetters(['jobs', 'loading', 'isAuthenticated', 'applications'])
  },
  methods: {
    ...mapActions(['fetchJobs', 'vulnerableJobSearch', 'fetchApplications']),
    
    async performSearch() {
      try {
        // Prepare search data
        const searchData = {
          search_term: this.searchForm.search_term,
          filters: {}
        }
        
        const searchResults = await this.vulnerableJobSearch(searchData)
        
        // Update jobs list with search results
        if (searchResults && searchResults.results) {
          this.$store.commit('SET_JOBS', searchResults.results)
        }
      } catch (error) {
        console.error('Search failed:', error)
      }
    },
    
    async resetSearch() {
      // Clear search form
      this.searchForm.search_term = ''
      
      // Reload all jobs
      await this.fetchJobs()
    },
    
    quickApply(jobId) {
      if (this.hasAppliedToJob(jobId)) {
        return; // Do nothing if already applied
      }
      // Redirect to chat with job context for application
      this.$router.push({
        path: '/candidate-portal',
        query: { 
          job: jobId,
          mode: 'apply'
        }
      })
    },
    
    hasAppliedToJob(jobId) {
      return this.applications.some(app => app.job_id === jobId);
    }
  },
  
  async created() {
    await this.fetchJobs()
    if (this.isAuthenticated) {
      await this.fetchApplications()
    }
  }
}
</script>

<style scoped>
.jobs-page {
  background-color: #f8f9fa;
  min-height: calc(100vh - 120px);
}

.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

/* WARNING: Styles that could be exploited */
.job-description {
  /* Raw HTML rendering - XSS vulnerability */
  max-height: 150px;
  overflow: hidden;
}

.font-monospace {
  font-family: 'Courier New', monospace;
}

code {
  color: #e83e8c;
  background-color: #f8f9fa;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
}

.alert-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}
</style> 