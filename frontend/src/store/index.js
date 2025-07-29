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
    chatSessions: [],
    currentChatSession: null,
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
    SET_CHAT_SESSIONS(state, sessions) {
      state.chatSessions = sessions
    },
    SET_CURRENT_CHAT_SESSION(state, session) {
      state.currentChatSession = session
    },
    ADD_CHAT_SESSION(state, session) {
      // Add new session to the beginning of the list
      state.chatSessions.unshift(session)
    },
    UPDATE_CHAT_SESSION(state, updatedSession) {
      const index = state.chatSessions.findIndex(s => s.id === updatedSession.id)
      if (index !== -1) {
        state.chatSessions.splice(index, 1, updatedSession)
      }
      // Also update current session if it's the same
      if (state.currentChatSession && state.currentChatSession.id === updatedSession.id) {
        state.currentChatSession = updatedSession
      }
    },
    ADD_MESSAGE_TO_SESSION(state, { sessionId, userMessage, aiMessage }) {
      // Add messages to current session if loaded
      if (state.currentChatSession && state.currentChatSession.id === sessionId) {
        if (!state.currentChatSession.messages) {
          state.currentChatSession.messages = []
        }
        state.currentChatSession.messages.push(userMessage)
        state.currentChatSession.messages.push(aiMessage)
        state.currentChatSession.updated_at = aiMessage.created_at
      }
      
      // Update session in sessions list
      const sessionIndex = state.chatSessions.findIndex(s => s.id === sessionId)
      if (sessionIndex !== -1) {
        state.chatSessions[sessionIndex].updated_at = aiMessage.created_at
        // Move session to top of list
        const session = state.chatSessions.splice(sessionIndex, 1)[0]
        state.chatSessions.unshift(session)
      }
    },
    REMOVE_CHAT_SESSION(state, sessionId) {
      state.chatSessions = state.chatSessions.filter(s => s.id !== sessionId)
      if (state.currentChatSession && state.currentChatSession.id === sessionId) {
        state.currentChatSession = null
      }
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
      commit('SET_CHAT_SESSIONS', []) // Changed from SET_CHAT_HISTORY to SET_CHAT_SESSIONS
      commit('SET_CURRENT_CHAT_SESSION', null)
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
    
    async sendChatMessage({ commit }, { message, sessionId = null, jobId = null }) {
      try {
        const response = await axios.post('/chat/send', {
          message,
          session_id: sessionId,
          job_id: jobId
        })
        
        const { session, user_message, ai_message } = response.data
        
        // If this is a new session, add it to the list and set as current
        if (!sessionId) {
          commit('ADD_CHAT_SESSION', session)
          commit('SET_CURRENT_CHAT_SESSION', {
            ...session,
            messages: []
          })
        }
        
        // Add messages to the session
        commit('ADD_MESSAGE_TO_SESSION', { 
          sessionId: session.id, 
          userMessage: user_message, 
          aiMessage: ai_message 
        })
        
        return response.data
      } catch (error) {
        commit('SET_ERROR', 'Failed to send message')
        throw error
      }
    },
    
    async fetchChatSessions({ commit }) {
      try {
        const response = await axios.get('/chat/sessions')
        commit('SET_CHAT_SESSIONS', response.data)
      } catch (error) {
        commit('SET_ERROR', 'Failed to fetch chat sessions')
        throw error
      }
    },
    
    async fetchChatSession({ commit }, sessionId) {
      try {
        const response = await axios.get(`/chat/sessions/${sessionId}`)
        commit('SET_CURRENT_CHAT_SESSION', response.data)
        return response.data
      } catch (error) {
        commit('SET_ERROR', 'Failed to fetch chat session')
        throw error
      }
    },

    async deleteChatSession({ commit }, sessionId) {
      try {
        await axios.delete(`/chat/sessions/${sessionId}`)
        commit('REMOVE_CHAT_SESSION', sessionId)
        return { message: 'Chat session deleted' }
      } catch (error) {
        commit('SET_ERROR', 'Failed to delete chat session')
        throw error
      }
    },

    async clearAllChatSessions({ commit }) {
      try {
        const response = await axios.delete('/chat/sessions')
        commit('SET_CHAT_SESSIONS', [])
        commit('SET_CURRENT_CHAT_SESSION', null)
        return response.data
      } catch (error) {
        commit('SET_ERROR', 'Failed to clear chat sessions')
        throw error
      }
    },

    // Legacy action for backward compatibility - can be removed later
    async fetchChatHistory({ dispatch }) {
      return await dispatch('fetchChatSessions')
    },
    
    // Legacy action for backward compatibility - can be removed later  
    async clearAllChatHistory({ dispatch }) {
      return await dispatch('clearAllChatSessions')
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
    chatSessions: state => state.chatSessions, // Changed from chatHistory to chatSessions
    currentChatSession: state => state.currentChatSession,
    loading: state => state.loading,
    error: state => state.error
  }
}) 