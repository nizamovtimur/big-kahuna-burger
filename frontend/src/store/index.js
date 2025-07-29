import { createStore } from 'vuex'
import axios from 'axios'

// Configure axios base URL
const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8080/api'
axios.defaults.baseURL = API_BASE_URL

// Add token to requests
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default createStore({
  state: {
    user: null,
    token: localStorage.getItem('token'),
    jobs: [],
    applications: [],
    chatHistory: [],
    loading: false,
    error: null
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user
    },
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
    SET_JOBS(state, jobs) {
      state.jobs = jobs
    },
    SET_APPLICATIONS(state, applications) {
      state.applications = applications
    },
    SET_CHAT_HISTORY(state, history) {
      state.chatHistory = history
    },
    ADD_CHAT_MESSAGE(state, message) {
      state.chatHistory.push(message)
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    CLEAR_ERROR(state) {
      state.error = null
    }
  },
  
  actions: {
    async login({ commit }, credentials) {
      try {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        const formData = new FormData()
        formData.append('username', credentials.username)
        formData.append('password', credentials.password)
        
        const response = await axios.post('/auth/login', formData)
        const { access_token } = response.data
        
        commit('SET_TOKEN', access_token)
        
        // Get user info
        await this.dispatch('fetchCurrentUser')
        
        return true
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || 'Login failed')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async register({ commit }, userData) {
      try {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        await axios.post('/auth/register', userData)
        return true
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || 'Registration failed')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async fetchCurrentUser({ commit, state }) {
      if (!state.token) return
      
      try {
        const response = await axios.get('/auth/me')
        commit('SET_USER', response.data)
      } catch (error) {
        console.error('Failed to fetch user:', error)
        this.dispatch('logout')
      }
    },
    
    async checkAuth({ dispatch, state }) {
      if (state.token) {
        await dispatch('fetchCurrentUser')
      }
    },
    
    logout({ commit }) {
      commit('SET_TOKEN', null)
      commit('SET_USER', null)
      commit('SET_APPLICATIONS', [])
      commit('SET_CHAT_HISTORY', [])
    },
    
    async fetchJobs({ commit }) {
      try {
        commit('SET_LOADING', true)
        const response = await axios.get('/jobs/')
        // Backend returns {jobs: [...], query_executed: "..."}
        const jobs = response.data.jobs || response.data || []
        commit('SET_JOBS', jobs)
      } catch (error) {
        console.error('Failed to fetch jobs:', error)
        commit('SET_ERROR', 'Failed to fetch jobs')
        commit('SET_JOBS', []) // Set empty array on error
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async fetchJobById({ state }, jobId) {
      try {
        const response = await axios.get(`/jobs/${jobId}`)
        return response.data
      } catch (error) {
        throw error
      }
    },
    
    async submitApplication({ commit }, applicationData) {
      try {
        commit('SET_LOADING', true)
        const formData = new FormData()
        
        formData.append('job_id', applicationData.job_id)
        formData.append('cover_letter', applicationData.cover_letter)
        formData.append('additional_answers', JSON.stringify(applicationData.additional_answers || {}))
        formData.append('cv_file', applicationData.cv_file)
        
        const response = await axios.post('/applications/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || 'Application submission failed')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async fetchApplications({ commit }) {
      try {
        const response = await axios.get('/applications/')
        commit('SET_APPLICATIONS', response.data)
      } catch (error) {
        commit('SET_ERROR', 'Failed to fetch applications')
        throw error
      }
    },
    
    async fetchAllApplications({ commit }) {
      try {
        const response = await axios.get('/applications/hr')
        commit('SET_APPLICATIONS', response.data)
      } catch (error) {
        commit('SET_ERROR', 'Failed to fetch applications')
        throw error
      }
    },
    
    async sendChatMessage({ commit }, { message, job_id }) {
      try {
        const response = await axios.post('/chat/', {
          message,
          job_id
        })
        
        commit('ADD_CHAT_MESSAGE', response.data)
        return response.data
      } catch (error) {
        commit('SET_ERROR', 'Failed to send message')
        throw error
      }
    },
    
    async fetchChatHistory({ commit }) {
      try {
        const response = await axios.get('/chat/history')
        commit('SET_CHAT_HISTORY', response.data)
      } catch (error) {
        commit('SET_ERROR', 'Failed to fetch chat history')
        throw error
      }
    },

    async deleteChatSession({ commit, state }, sessionId) {
      try {
        // Call backend API to delete session
        await axios.delete(`/chat/${sessionId}`)
        
        // Update local state
        const updatedHistory = state.chatHistory.filter(session => 
          session.id !== sessionId && session.created_at !== sessionId
        )
        commit('SET_CHAT_HISTORY', updatedHistory)
        
        return { message: 'Chat session deleted' }
      } catch (error) {
        commit('SET_ERROR', 'Failed to delete chat session')
        throw error
      }
    },

    async clearAllChatHistory({ commit }) {
      try {
        const response = await axios.delete('/chat/')
        commit('SET_CHAT_HISTORY', [])
        return response.data
      } catch (error) {
        commit('SET_ERROR', 'Failed to clear chat history')
        throw error
      }
    },

    async exportChatHistory() {
      try {
        const response = await axios.get('/chat/export')
        return response.data
      } catch (error) {
        throw error
      }
    },
    
    // Vulnerable search function - exposes SQL injection endpoint
    async vulnerableJobSearch({ commit }, searchData) {
      try {
        const response = await axios.post('/jobs/search', searchData)
        return response.data
      } catch (error) {
        // Don't throw error to allow seeing injection results
        return error.response?.data || { error: 'Search failed' }
      }
    },

    async deleteApplication({ commit, state }, applicationId) {
      try {
        commit('SET_LOADING', true)
        const response = await axios.delete(`/applications/${applicationId}`)
        
        // Update local state by removing the deleted application
        const updatedApplications = state.applications.filter(app => app.id !== applicationId)
        commit('SET_APPLICATIONS', updatedApplications)
        
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || 'Failed to delete application')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async bulkDeleteApplications({ commit, state }, { applicationIds, confirmDeletion = false }) {
      try {
        commit('SET_LOADING', true)
        const response = await axios.post('/applications/bulk-delete', {
          application_ids: applicationIds,
          confirm_deletion: confirmDeletion
        })
        
        // Update local state by removing deleted applications
        const updatedApplications = state.applications.filter(app => !applicationIds.includes(app.id))
        commit('SET_APPLICATIONS', updatedApplications)
        
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || 'Failed to delete applications')
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    }
  },
  
  getters: {
    isAuthenticated: state => !!state.token,
    currentUser: state => state.user,
    isHR: state => state.user?.is_hr || false,
    jobs: state => state.jobs,
    applications: state => state.applications,
    chatHistory: state => state.chatHistory,
    loading: state => state.loading,
    error: state => state.error
  }
}) 