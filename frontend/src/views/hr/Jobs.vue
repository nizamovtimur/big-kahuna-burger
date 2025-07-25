<template>
  <div class="hr-jobs">
    <div class="container py-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="fw-bold">Manage Jobs</h1>
        <button class="btn btn-primary" @click="showCreateModal = true">
          <i class="fas fa-plus me-2"></i>Create New Job
        </button>
      </div>

      <!-- Jobs Table -->
      <div class="card">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Department</th>
                  <th>Location</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="job in allJobs" :key="job.id">
                  <td>{{ job.title }}</td>
                  <td>{{ job.department }}</td>
                  <td>{{ job.location }}</td>
                  <td>
                    <span :class="job.is_active ? 'badge bg-success' : 'badge bg-secondary'">
                      {{ job.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td>{{ formatDate(job.created_at) }}</td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary me-2" @click="editJob(job)">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" @click="deleteJob(job)">
                      <i class="fas fa-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Job Modal -->
    <div class="modal fade" id="jobModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingJob ? 'Edit Job' : 'Create New Job' }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveJob">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Job Title</label>
                    <input v-model="jobForm.title" type="text" class="form-control" required>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Department</label>
                    <input v-model="jobForm.department" type="text" class="form-control" required>
                  </div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Location</label>
                    <input v-model="jobForm.location" type="text" class="form-control" required>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="mb-3">
                    <label class="form-label">Min Salary</label>
                    <input v-model="jobForm.salary_min" type="number" class="form-control">
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="mb-3">
                    <label class="form-label">Max Salary</label>
                    <input v-model="jobForm.salary_max" type="number" class="form-control">
                  </div>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Job Description</label>
                <textarea v-model="jobForm.description" class="form-control" rows="4" required></textarea>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Requirements</label>
                <textarea v-model="jobForm.requirements" class="form-control" rows="3"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveJob">
              {{ editingJob ? 'Update' : 'Create' }} Job
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
  name: 'HRJobs',
  data() {
    return {
      showCreateModal: false,
      editingJob: null,
      jobForm: {
        title: '',
        department: '',
        location: '',
        description: '',
        requirements: '',
        salary_min: null,
        salary_max: null
      }
    }
  },
  computed: {
    ...mapGetters(['allJobs'])
  },
  methods: {
    ...mapActions(['fetchJobs', 'createJob']),
    
    editJob(job) {
      this.editingJob = job
      this.jobForm = { ...job }
      this.showCreateModal = true
      this.openModal()
    },
    
    deleteJob(job) {
      if (confirm('Are you sure you want to delete this job?')) {
        // Implementation would call delete API
        alert('Delete functionality would be implemented here')
      }
    },
    
    async saveJob() {
      const result = await this.createJob(this.jobForm)
      if (result.success) {
        this.closeModal()
        this.resetForm()
        await this.fetchJobs()
      }
    },
    
    closeModal() {
      this.showCreateModal = false
      this.editingJob = null
      this.resetForm()
      // Close Bootstrap modal
      const modal = document.getElementById('jobModal')
      const bsModal = window.bootstrap?.Modal?.getInstance(modal)
      if (bsModal) {
        bsModal.hide()
      }
    },
    
    openModal() {
      // Open Bootstrap modal
      const modal = document.getElementById('jobModal')
      const bsModal = new window.bootstrap.Modal(modal)
      bsModal.show()
    },
    
    resetForm() {
      this.jobForm = {
        title: '',
        department: '',
        location: '',
        description: '',
        requirements: '',
        salary_min: null,
        salary_max: null
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  },
  
  watch: {
    showCreateModal(val) {
      if (val && !this.editingJob) {
        this.openModal()
      }
    }
  },
  
  async mounted() {
    await this.fetchJobs()
  }
}
</script> 