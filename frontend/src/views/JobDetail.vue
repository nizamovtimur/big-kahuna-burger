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
          <!-- Apply Section -->
          <div v-if="isAuthenticated" class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-success text-white">
              <h5 class="mb-0">
                <i class="fas fa-paper-plane"></i> Подать заявку на эту позицию
              </h5>
            </div>
            <div class="card-body">
              <button 
                class="btn btn-success w-100 mb-3"
                @click="showApplicationForm = true"
                :disabled="hasApplied"
              >
                <i class="fas fa-file-upload"></i>
                {{ hasApplied ? 'Уже подана заявка' : 'Подать заявку' }}
              </button>
              
              <hr>
              
              <h6>Быстрый чат с ИИ</h6>
              <p class="small text-muted mb-3">
                Спросите нашего ИИ-помощника об этой позиции
              </p>
              <router-link 
                :to="`/candidate-portal?job=${job.id}`" 
                class="btn btn-outline-primary w-100"
              >
                <i class="fas fa-robot"></i> Обсудить эту вакансию
              </router-link>
            </div>
          </div>

          <!-- Login Prompt -->
          <div v-else class="card border-0 shadow-sm mb-4">
            <div class="card-body text-center">
              <i class="fas fa-lock fa-3x text-muted mb-3"></i>
              <h5>Требуется вход</h5>
              <p class="text-muted">Пожалуйста, войдите, чтобы подать заявку на эту позицию</p>
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

      <!-- Application Modal -->
      <div v-if="showApplicationForm" class="modal d-block" style="background-color: rgba(0,0,0,0.5)">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Подать заявку на {{ job?.title }}</h5>
              <button 
                type="button" 
                class="btn-close" 
                @click="showApplicationForm = false"
              ></button>
            </div>
            <div class="modal-body">
              <form @submit.prevent="handleSubmitApplication">
                <div class="mb-3">
                  <label for="coverLetter" class="form-label">Сопроводительное письмо *</label>
                  <textarea 
                    class="form-control" 
                    id="coverLetter"
                    v-model="applicationForm.cover_letter"
                    rows="5"
                    required
                    placeholder="Расскажите, почему вас интересует эта позиция..."
                  ></textarea>
                  <div class="form-text text-muted">
                    <small>Поделитесь своей мотивацией и релевантным опытом для этой роли</small>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="cvFile" class="form-label">Резюме *</label>
                  <input 
                    type="file" 
                    class="form-control" 
                    id="cvFile"
                    @change="handleFileUpload"
                    accept=".pdf,.doc,.docx"
                    required
                  >
                  <div class="form-text text-muted">
                    <small>Поддерживаемые форматы: PDF, DOC, DOCX (макс. 10МБ)</small>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="additionalInfo" class="form-label">Дополнительная информация</label>
                  <textarea 
                    class="form-control" 
                    id="additionalInfo"
                    v-model="applicationForm.additional_info"
                    rows="3"
                    placeholder="Любая дополнительная информация, которой хотели бы поделиться..."
                  ></textarea>
                </div>

                <div class="d-grid gap-2">
                  <button type="submit" class="btn btn-success" :disabled="submitting">
                    <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                    <i class="fas fa-paper-plane"></i> Подать заявку
                  </button>
                  <button 
                    type="button" 
                    class="btn btn-secondary" 
                    @click="showApplicationForm = false"
                  >
                    Отменить
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
    
    async handleSubmitApplication() {
      if (!this.applicationForm.cv_file) {
        alert('Пожалуйста, выберите файл резюме')
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
        
        alert('Заявка успешно подана!')
      } catch (error) {
        alert('Не удалось подать заявку: ' + error.message)
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