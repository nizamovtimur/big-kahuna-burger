import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

// Import views
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Jobs from '../views/Jobs.vue'
import JobDetail from '../views/JobDetail.vue'
import CandidatePortal from '../views/CandidatePortal.vue'

// HR Views
import HRDashboard from '../views/hr/Dashboard.vue'
import HRJobs from '../views/hr/Jobs.vue'
import HRApplications from '../views/hr/Applications.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/jobs',
    name: 'Jobs',
    component: Jobs
  },
  {
    path: '/jobs/:id',
    name: 'JobDetail',
    component: JobDetail,
    props: true
  },
  {
    path: '/candidate-portal',
    name: 'CandidatePortal',
    component: CandidatePortal,
    meta: { requiresAuth: true }
  },
  {
    path: '/hr/dashboard',
    name: 'HRDashboard',
    component: HRDashboard,
    meta: { requiresAuth: true, requiresHR: true }
  },
  {
    path: '/hr/jobs',
    name: 'HRJobs',
    component: HRJobs,
    meta: { requiresAuth: true, requiresHR: true }
  },
  {
    path: '/hr/applications',
    name: 'HRApplications',
    component: HRApplications,
    meta: { requiresAuth: true, requiresHR: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated
  const isHR = store.getters.isHR
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next('/login')
      return
    }
  }
  
  if (to.matched.some(record => record.meta.requiresHR)) {
    if (!isHR) {
      next('/')
      return
    }
  }
  
  next()
})

export default router 