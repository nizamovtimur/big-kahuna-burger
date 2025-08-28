<template>
  <div class="job-detail-page">
    <div class="container py-4">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="mt-2">Загрузка деталей вакансии...</p>
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
                <span class="badge bg-success fs-6">Активна</span>
              </div>

              <div class="row mb-4">
                <div class="col">
                  <h3>Описание вакансии</h3>
                  <div class="job-content" v-html="job.description"></div>
                </div>
              </div>

              <div class="row mb-4">
                <div class="col">
                  <h3>Требования</h3>
                  <div class="job-content" v-html="job.requirements"></div>
                </div>
              </div>

              <div v-if="job.additional_info" class="row mb-4">
                <div class="col">
                  <h3>Дополнительная информация</h3>
                  <div class="alert alert-info" v-html="job.additional_info"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <!-- Action Section -->
          <div v-if="isAuthenticated" class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-gradient-primary text-white">
              <h5 class="mb-0">
                <i class="fas fa-rocket"></i> Взаимодействие с вакансией
              </h5>
            </div>
            <div class="card-body">
              <!-- Job Discussion Button -->
              <button 
                class="btn btn-outline-primary w-100 mb-3"
                @click="startJobDiscussion"
              >
                <i class="fas fa-comments"></i>
                Задать вопрос о вакансии
              </button>
              
              <!-- Application Status -->
              <div v-if="applicationStatus.has_applied" class="alert alert-info mb-3">
                <div class="d-flex align-items-center">
                  <i class="fas fa-check-circle me-2"></i>
                  <div>
                    <strong>Заявка подана</strong>
                    <br>
                    <small>Статус: {{ getStatusText(applicationStatus.status) }}</small>
                  </div>
                </div>
              </div>
              
              <!-- Application Button -->
              <button 
                class="btn w-100 mb-3"
                @click="handleApplicationAction"
                :class="applicationStatus.has_applied ? 'btn-outline-secondary' : 'btn-success'"
                :disabled="applicationStatus.has_applied"
              >
                <i :class="applicationStatus.has_applied ? 'fas fa-check' : 'fas fa-paper-plane'"></i>
                {{ applicationStatus.has_applied ? 'Заявка уже подана' : 'Откликнуться в чате' }}
              </button>
              
              <hr>
              
              <div class="text-center">
                <small class="text-muted">
                  {{ applicationStatus.has_applied 
                    ? 'Продолжите общение с HR-агентом в чате' 
                    : 'Отправьте резюме и пообщайтесь с HR-агентом' }}
                </small>
              </div>
            </div>
          </div>

          <!-- Login Prompt -->
          <div v-else class="card border-0 shadow-sm mb-4">
            <div class="card-body text-center">
              <i class="fas fa-lock fa-3x text-muted mb-3"></i>
              <h5>Требуется вход</h5>
              <p class="text-muted">Пожалуйста, войдите, чтобы взаимодействовать с вакансией</p>
              <router-link to="/login" class="btn btn-primary">
                <i class="fas fa-sign-in-alt"></i> Войти
              </router-link>
            </div>
          </div>

          <!-- Job Info -->
          <div class="card border-0 shadow-sm">
            <div class="card-header">
              <h6 class="mb-0">Информация о вакансии</h6>
            </div>
            <div class="card-body">
              <ul class="list-unstyled mb-0">
                <li class="mb-2">
                  <strong>Местоположение:</strong> {{ job.location }}
                </li>
                <li class="mb-2">
                  <strong>Зарплата:</strong> {{ job.salary_range }}
                </li>
                <li class="mb-2">
                  <strong>Опубликовано:</strong> {{ formatDate(job.created_at) }}
                </li>
                <li>
                  <strong>ID вакансии:</strong> {{ job.id }}
                </li>
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
  name: 'JobDetail',
  props: ['id'],
  data() {
    return {
      job: null,
      loading: true,
      applicationStatus: {
        has_applied: false,
        application_id: null,
        status: null,
        applied_at: null
      }
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'user', 'apiClient'])
  },
  methods: {
    ...mapActions(['fetchJobById']),
    
    async loadJob() {
      try {
        this.job = await this.fetchJobById(this.id)
        if (this.isAuthenticated) {
          await this.checkApplicationStatus()
        }
      } catch (error) {
        console.error('Failed to load job:', error)
        this.$router.push('/jobs')
      } finally {
        this.loading = false
      }
    },
    
    async checkApplicationStatus() {
      try {
        const response = await this.apiClient.get(`/applications/check/${this.id}`)
        this.applicationStatus = response.data
      } catch (error) {
        console.error('Failed to check application status:', error)
      }
    },
    
    startJobDiscussion() {
      // Redirect to chat with job context
      this.$router.push({
        path: '/candidate-portal',
        query: { 
          job: this.job.id
        }
      })
    },
    
    handleApplicationAction() {
      // Always go to chat with job context
      this.$router.push({
        path: '/candidate-portal',
        query: { 
          job: this.job.id
        }
      })
    },
    
    getStatusText(status) {
      const statusMap = {
        'pending': 'На рассмотрении',
        'approved': 'Одобрена',
        'rejected': 'Отклонена'
      }
      return statusMap[status] || status
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
  min-height: calc(100vh - 120px);
}

/* WARNING: Styles that allow XSS */
.job-content {
  /* Raw HTML rendering - XSS vulnerability */
  line-height: 1.6;
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
}

.card {
  border: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.btn {
  transition: all 0.2s ease;
}

.btn:hover {
  transform: translateY(-1px);
}

.alert {
  border: none;
  border-radius: 10px;
}
</style> 