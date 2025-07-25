import { createStore } from 'vuex'
import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000'

// Configure axios defaults
axios.defaults.baseURL = API_BASE_URL

export default createStore({
  state: {
    // Authentication
    token: localStorage.getItem('token') || null,
    user: null,
    
    // Jobs
    jobs: [],
    currentJob: null,
    
    // Applications
    applications: [],
    
    // Chat
    chatMessages: [],
    chatSession: null,
    
    // UI State
    loading: false,
    error: null
  },
  
  getters: {
    isAuthenticated: state => !!state.token,
    currentUser: state => state.user,
    allJobs: state => state.jobs,
    filteredJobs: state => (filters) => {
      return state.jobs.filter(job => {
        if (filters.department && !job.department.toLowerCase().includes(filters.department.toLowerCase())) {
          return false
        }
        if (filters.location && !job.location.toLowerCase().includes(filters.location.toLowerCase())) {
          return false
        }
        return true
      })
    }
  },
  
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token
      if (token) {
        localStorage.setItem('token', token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      } else {
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
      }
    },
    
    SET_USER(state, user) {
      state.user = user
    },
    
    SET_JOBS(state, jobs) {
      state.jobs = jobs
    },
    
    SET_CURRENT_JOB(state, job) {
      state.currentJob = job
    },
    
    SET_APPLICATIONS(state, applications) {
      state.applications = applications
    },
    
    SET_CHAT_MESSAGES(state, messages) {
      state.chatMessages = messages
    },
    
    ADD_CHAT_MESSAGE(state, message) {
      state.chatMessages.push(message)
    },
    
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  
  actions: {
    async login({ commit }, credentials) {
      try {
        commit('SET_LOADING', true)
        const response = await axios.post('/auth/login', credentials)
        const { access_token } = response.data
        
        commit('SET_TOKEN', access_token)
        
        // Get user info
        const userResponse = await axios.get('/auth/me')
        commit('SET_USER', userResponse.data)
        
        return { success: true }
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || 'Login failed')
        return { success: false, error: error.response?.data?.detail }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async register({ commit }, userData) {
      try {
        commit('SET_LOADING', true)
        const response = await axios.post('/auth/register', userData)
        const { access_token } = response.data
        
        commit('SET_TOKEN', access_token)
        commit('SET_USER', response.data)
        
        return { success: true }
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || 'Registration failed')
        return { success: false, error: error.response?.data?.detail }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async logout({ commit }) {
      commit('SET_TOKEN', null)
      commit('SET_USER', null)
      commit('SET_APPLICATIONS', [])
    },
    
    async checkAuthStatus({ commit, state }) {
      if (state.token) {
        try {
          const response = await axios.get('/auth/me')
          commit('SET_USER', response.data)
        } catch (error) {
          commit('SET_TOKEN', null)
          commit('SET_USER', null)
        }
      }
    },
    
    async fetchJobs({ commit }, filters = {}) {
      try {
        commit('SET_LOADING', true)
        const params = new URLSearchParams()
        
        if (filters.department) params.append('department', filters.department)
        if (filters.location) params.append('location', filters.location)
        
        const response = await axios.get(`/jobs/?${params}`)
        commit('SET_JOBS', response.data)
      } catch (error) {
        commit('SET_ERROR', 'Failed to fetch jobs')
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async fetchJob({ commit }, jobId) {
      try {
        const response = await axios.get(`/jobs/${jobId}`)
        commit('SET_CURRENT_JOB', response.data)
        return response.data
      } catch (error) {
        commit('SET_ERROR', 'Failed to fetch job details')
        throw error
      }
    },
    
    async createJob({ commit }, jobData) {
      try {
        const response = await axios.post('/jobs/', jobData)
        return { success: true, job: response.data }
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || 'Failed to create job')
        return { success: false, error: error.response?.data?.detail }
      }
    },
    
    async createApplicant({ commit }, applicantData) {
      try {
        const response = await axios.post('/applicants/', applicantData)
        return { success: true, applicant: response.data }
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || 'Failed to create applicant profile')
        return { success: false, error: error.response?.data?.detail }
      }
    },
    
    async submitApplication({ commit }, { applicantId, applicationData }) {
      try {
        const response = await axios.post(`/applicants/${applicantId}/apply`, applicationData)
        return { success: true, application: response.data }
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || 'Failed to submit application')
        return { success: false, error: error.response?.data?.detail }
      }
    },
    
    async chatWithAI({ commit }, { message, jobId, applicantEmail }) {
      try {
        const params = applicantEmail ? { applicant_email: applicantEmail } : {}
        const response = await axios.post('/chat/', 
          { message, job_id: jobId },
          { params }
        )
        
        // Add user message
        commit('ADD_CHAT_MESSAGE', {
          role: 'user',
          content: message,
          timestamp: new Date()
        })
        
        // Add AI response
        commit('ADD_CHAT_MESSAGE', {
          role: 'assistant',
          content: response.data.message,
          timestamp: new Date()
        })
        
        return response.data
      } catch (error) {
        commit('SET_ERROR', 'Failed to send message')
        throw error
      }
    },
    
    async fetchApplications({ commit }) {
      try {
        const response = await axios.get('/applications/')
        commit('SET_APPLICATIONS', response.data)
      } catch (error) {
        commit('SET_ERROR', 'Failed to fetch applications')
      }
    }
  }
}) 