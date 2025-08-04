<template>
  <div class="hr-applications">
    <div class="container py-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="display-6 mb-0">
          <i class="fas fa-file-alt text-primary"></i> Управление заявками
        </h1>
        <router-link to="/hr/dashboard" class="btn btn-secondary">
          <i class="fas fa-arrow-left"></i> Назад к панели управления
        </router-link>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка заявок...</span>
        </div>
      </div>

      <!-- Applications List -->
      <div v-else-if="applications.length > 0" class="row">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="fas fa-list"></i> Все заявки ({{ applications.length }})
                <span v-if="selectedApplications.length > 0" class="badge bg-warning text-dark ms-2">
                  {{ selectedApplications.length }} выбрано
                </span>
              </h5>
              <div v-if="selectedApplications.length > 0" class="btn-group">
                <button 
                  class="btn btn-outline-light btn-sm"
                  @click="confirmBulkDelete"
                >
                  <i class="fas fa-trash"></i> Удалить выбранные ({{ selectedApplications.length }})
                </button>
                <button 
                  class="btn btn-outline-light btn-sm"
                  @click="clearSelection"
                >
                  <i class="fas fa-times"></i> Отменить выбор
                </button>
              </div>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th width="40">
                        <input 
                          type="checkbox" 
                          class="form-check-input"
                          @change="toggleAllSelection"
                          :checked="isAllSelected"
                          :indeterminate="isPartiallySelected"
                        >
                      </th>
                      <th>Кандидат</th>
                      <th>Название вакансии</th>
                      <th>Оценка резюме</th>
                      <th>Дата подачи</th>
                      <th>Статус</th>
                      <th>Действия</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="application in applications" :key="application.id">
                      <td>
                        <input 
                          type="checkbox" 
                          class="form-check-input"
                          :value="application.id"
                          v-model="selectedApplications"
                        >
                      </td>
                      <td>
                        <div>
                          <strong>{{ application.user?.full_name || 'Неизвестно' }}</strong><br>
                          <small class="text-muted">{{ application.user?.email || 'Н/Д' }}</small>
                        </div>
                      </td>
                      <td>
                        <div>
                          <strong>{{ application.job?.title || 'Вакансия не найдена' }}</strong><br>
                          <small class="text-muted">{{ application.job?.location || '' }}</small>
                        </div>
                      </td>
                      <td>
                        <span class="badge" :class="getScoreBadgeClass(application.cv_score)">
                          {{ application.cv_score || 'Н/Д' }}/10
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
                            <i class="fas fa-eye"></i> Просмотр
                          </button>
                          <div class="dropdown">
                            <button 
                              class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                              type="button" 
                              data-bs-toggle="dropdown"
                            >
                              Статус
                            </button>
                            <ul class="dropdown-menu">
                              <li><a class="dropdown-item" href="#" @click.prevent="updateStatus(application.id, 'pending')">Ожидание</a></li>
                              <li><a class="dropdown-item" href="#" @click.prevent="updateStatus(application.id, 'reviewing')">Рассмотрение</a></li>
                              <li><a class="dropdown-item" href="#" @click.prevent="updateStatus(application.id, 'interview')">Собеседование</a></li>
                              <li><a class="dropdown-item" href="#" @click.prevent="updateStatus(application.id, 'accepted')">Принят</a></li>
                              <li><a class="dropdown-item" href="#" @click.prevent="updateStatus(application.id, 'rejected')">Отклонен</a></li>
                            </ul>
                          </div>
                          <button 
                            class="btn btn-sm btn-outline-danger"
                            @click="confirmDelete(application)"
                            title="Удалить заявку навсегда"
                          >
                            <i class="fas fa-trash"></i>
                          </button>
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
        <h4 class="text-muted">Заявок пока нет</h4>
        <p class="text-muted">Когда кандидаты подадут заявки на работу, они появятся здесь.</p>
      </div>

      <!-- Application Detail Modal -->
      <div class="modal fade" id="applicationModal" tabindex="-1" v-if="selectedApplication">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                Детали заявки - {{ selectedApplication.user?.full_name }}
              </h5>
              <button type="button" class="btn-close" @click="closeApplicationModal"></button>
            </div>
            <div class="modal-body">
              <div class="row">
                <div class="col-md-6">
                  <h6>Информация о кандидате</h6>
                  <p><strong>Имя:</strong> {{ selectedApplication.user?.full_name }}</p>
                  <p><strong>Email:</strong> {{ selectedApplication.user?.email }}</p>
                  <p><strong>Имя пользователя:</strong> {{ selectedApplication.user?.username }}</p>
                </div>
                <div class="col-md-6">
                  <h6>Детали заявки</h6>
                  <p><strong>Вакансия:</strong> {{ selectedApplication.job?.title }}</p>
                  <p><strong>Оценка резюме:</strong> {{ selectedApplication.cv_score }}/10</p>
                  <p><strong>Статус:</strong> {{ selectedApplication.status }}</p>
                  <p><strong>Подано:</strong> {{ formatDate(selectedApplication.applied_at) }}</p>
                </div>
              </div>
              
              <div class="mt-3">
                <h6>Сопроводительное письмо</h6>
                <div class="border rounded p-3 bg-light" v-html="selectedApplication.cover_letter"></div>
              </div>
              
              <div class="mt-3" v-if="selectedApplication.additional_answers">
                <h6>Дополнительная информация</h6>
                <div class="border rounded p-3 bg-light">
                  <!-- VULNERABILITY: XSS through additional_answers (educational purposes) -->
                  <div v-for="(value, key) in selectedApplication.additional_answers" :key="key" class="mb-2">
                    <strong>{{ key }}:</strong> 
                    <div class="mt-1">
                      <!-- XSS vulnerability: renders HTML if value is string, JSON if object -->
                      <span v-if="isString(value)" v-html="value"></span>
                      <pre v-else class="bg-white p-2 rounded border small">{{ formatValue(value) }}</pre>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-3" v-if="selectedApplication.cv_filename">
                <h6>Файл резюме</h6>
                <p><i class="fas fa-file-pdf text-danger"></i> {{ selectedApplication.cv_filename }}</p>
              </div>

              <div class="mt-3" v-if="selectedApplication.feedback">
                <h6>Обратная связь от HR</h6>
                <div class="border rounded p-3 bg-light">
                  <!-- VULNERABILITY: XSS through feedback (educational purposes) -->
                  <div v-html="selectedApplication.feedback"></div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeApplicationModal">Закрыть</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div class="modal fade" id="deleteModal" tabindex="-1" v-if="applicationToDelete">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header bg-danger text-white">
              <h5 class="modal-title">
                <i class="fas fa-exclamation-triangle"></i> Подтвердите удаление
              </h5>
                             <button type="button" class="btn-close btn-close-white" @click="closeDeleteModal"></button>
            </div>
            <div class="modal-body">
              <div class="alert alert-warning">
                <h6><i class="fas fa-warning"></i> ВНИМАНИЕ!</h6>
                <p class="mb-0">Вы собираетесь <strong>БЕЗВОЗВРАТНО</strong> удалить заявку:</p>
              </div>
              
              <div class="card">
                <div class="card-body">
                  <h6>{{ applicationToDelete.user?.full_name || 'Неизвестный кандидат' }}</h6>
                  <p class="mb-1"><strong>Вакансия:</strong> {{ applicationToDelete.job?.title || 'Н/Д' }}</p>
                  <p class="mb-1"><strong>Email:</strong> {{ applicationToDelete.user?.email || 'Н/Д' }}</p>
                  <p class="mb-0"><strong>ID заявки:</strong> {{ applicationToDelete.id }}</p>
                </div>
              </div>
              
              <div class="mt-3">
                <p class="text-danger">
                  <i class="fas fa-trash"></i> 
                  Это действие удалит заявку, резюме и все связанные данные из базы данных навсегда!
                </p>
                <p class="small text-muted">
                  Убедитесь, что вы действительно хотите выполнить это действие.
                </p>
              </div>
            </div>
            <div class="modal-footer">
                             <button type="button" class="btn btn-secondary" @click="closeDeleteModal">
                 <i class="fas fa-times"></i> Отмена
               </button>
              <button 
                type="button" 
                class="btn btn-danger" 
                @click="performDelete"
                :disabled="deleting"
              >
                <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
                <i class="fas fa-trash"></i> Удалить навсегда
              </button>
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
      selectedApplication: null,
      applicationToDelete: null,
      deleting: false,
      selectedApplications: [],
      bulkDeleting: false
    }
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'isHR', 'applications']),
    
    isAllSelected() {
      return this.applications.length > 0 && this.selectedApplications.length === this.applications.length
    },
    
    isPartiallySelected() {
      return this.selectedApplications.length > 0 && this.selectedApplications.length < this.applications.length
    }
  },
  methods: {
    ...mapActions(['logout', 'deleteApplication', 'bulkDeleteApplications']),
    
    // Helper methods for displaying additional_answers with XSS vulnerability
    isString(value) {
      return typeof value === 'string'
    },
    
    formatValue(value) {
      if (typeof value === 'object' && value !== null) {
        return JSON.stringify(value, null, 2)
      }
      return String(value)
    },
    
         async fetchApplications() {
       await this.$store.dispatch('fetchAllApplications')
     },

     async updateStatus(applicationId, newStatus) {
       try {
         await axios.put(`/applications/${applicationId}/status`, {
           status: newStatus,
           feedback: `Status updated to ${newStatus} by HR`
         })
        
        // Update local application
        const app = this.applications.find(a => a.id === applicationId)
        if (app) {
          app.status = newStatus
        }
                 
        this.$toast?.success(`Статус заявки обновлен на ${newStatus}`)
      } catch (error) {
        console.error('Failed to update status:', error)
        alert('Не удалось обновить статус заявки')
      }
    },

    viewApplication(application) {
      this.selectedApplication = application
      // Use Vue's $nextTick to ensure DOM is updated
      this.$nextTick(() => {
        try {
          const modalElement = document.getElementById('applicationModal')
          if (modalElement) {
            // Check if bootstrap is available
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
              const modal = new bootstrap.Modal(modalElement)
              modal.show()
            } else {
              // Fallback: show modal manually
              modalElement.style.display = 'block'
              modalElement.classList.add('show')
              document.body.classList.add('modal-open')
              
              // Create backdrop
              const backdrop = document.createElement('div')
              backdrop.className = 'modal-backdrop fade show'
              backdrop.id = 'view-modal-backdrop'
              document.body.appendChild(backdrop)
            }
          }
        } catch (error) {
          console.error('Error showing application modal:', error)
          // Fallback: show simplified info in alert
          const app = application
          const info = `
Кандидат: ${app.user?.full_name || 'Неизвестно'}
Email: ${app.user?.email || 'Н/Д'}
Вакансия: ${app.job?.title || 'Н/Д'}
Статус: ${app.status}
Оценка: ${app.cv_score || 'Н/Д'}/10
Дата подачи: ${this.formatDate(app.applied_at)}
          `
          alert(`Детали заявки:\n${info}`)
        }
      })
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
    },

    confirmDelete(application) {
      this.applicationToDelete = application
      // Use Vue's $nextTick to ensure DOM is updated
      this.$nextTick(() => {
        try {
          const modalElement = document.getElementById('deleteModal')
          if (modalElement) {
            // Check if bootstrap is available
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
              const modal = new bootstrap.Modal(modalElement)
              modal.show()
            } else {
              // Fallback: show modal manually
              modalElement.style.display = 'block'
              modalElement.classList.add('show')
              document.body.classList.add('modal-open')
              
              // Create backdrop
              const backdrop = document.createElement('div')
              backdrop.className = 'modal-backdrop fade show'
              backdrop.id = 'modal-backdrop'
              document.body.appendChild(backdrop)
            }
          }
        } catch (error) {
          console.error('Error showing modal:', error)
          // Fallback: use simple confirm dialog
          if (confirm(`Удалить заявку от ${application.user?.full_name}? Это действие необратимо!`)) {
            this.applicationToDelete = application
            this.performDelete()
          }
        }
      })
    },

    async performDelete() {
      if (!this.applicationToDelete) return
      
      try {
        this.deleting = true
        
                 const response = await this.$store.dispatch('deleteApplication', this.applicationToDelete.id)
         
         // Close modal
         this.closeDeleteModal()
         
         // Show success message
         alert(`Заявка успешно удалена! ${response.message}`)
        
      } catch (error) {
        console.error('Failed to delete application:', error)
        alert('Не удалось удалить заявку: ' + (error.message || 'Unknown error'))
             } finally {
         this.deleting = false
       }
     },

     toggleAllSelection() {
       if (this.isAllSelected) {
         this.selectedApplications = []
       } else {
         this.selectedApplications = this.applications.map(app => app.id)
       }
     },

     clearSelection() {
       this.selectedApplications = []
     },

     confirmBulkDelete() {
       if (this.selectedApplications.length === 0) return
       
       const count = this.selectedApplications.length
       const confirmMessage = `Вы действительно хотите БЕЗВОЗВРАТНО удалить ${count} заявок? Это действие нельзя отменить!`
       
       if (confirm(confirmMessage)) {
         this.performBulkDelete()
       }
     },

     async performBulkDelete() {
       try {
         this.bulkDeleting = true
         
         const response = await this.$store.dispatch('bulkDeleteApplications', {
           applicationIds: this.selectedApplications,
           confirmDeletion: true
         })
         
         this.selectedApplications = []
         
         alert(`Успешно удалено заявок: ${response.deleted_applications.length}`)
         
       } catch (error) {
         console.error('Failed to bulk delete:', error)
         alert('Не удалось удалить заявки: ' + (error.message || 'Unknown error'))
       } finally {
         this.bulkDeleting = false
       }
     },

     closeDeleteModal() {
       try {
         const modalElement = document.getElementById('deleteModal')
         if (modalElement) {
           if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
             const modal = bootstrap.Modal.getInstance(modalElement)
             if (modal) {
               modal.hide()
             }
           } else {
             // Manual modal hiding
             modalElement.style.display = 'none'
             modalElement.classList.remove('show')
             document.body.classList.remove('modal-open')
             
             // Remove backdrop
             const backdrop = document.getElementById('modal-backdrop')
             if (backdrop) {
               backdrop.remove()
             }
           }
         }
       } catch (error) {
         console.error('Error closing modal:', error)
       }
       
       // Clear selected application
       this.applicationToDelete = null
     },

     closeApplicationModal() {
       try {
         const modalElement = document.getElementById('applicationModal')
         if (modalElement) {
           if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
             const modal = bootstrap.Modal.getInstance(modalElement)
             if (modal) {
               modal.hide()
             }
           } else {
             // Manual modal hiding
             modalElement.style.display = 'none'
             modalElement.classList.remove('show')
             document.body.classList.remove('modal-open')
             
             // Remove backdrop
             const backdrop = document.getElementById('view-modal-backdrop')
             if (backdrop) {
               backdrop.remove()
             }
           }
         }
       } catch (error) {
         console.error('Error closing application modal:', error)
       }
       
       // Clear selected application
       this.selectedApplication = null
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