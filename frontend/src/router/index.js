import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Jobs from '../views/Jobs.vue'
import JobDetail from '../views/JobDetail.vue'
import CandidatePortal from '../views/CandidatePortal.vue'
import Login from '../views/Login.vue'
import HRDashboard from '../views/hr/Dashboard.vue'
import HRJobs from '../views/hr/Jobs.vue'
import HRApplications from '../views/hr/Applications.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
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
    path: '/candidate',
    name: 'CandidatePortal',
    component: CandidatePortal
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/hr/dashboard',
    name: 'HRDashboard',
    component: HRDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/hr/jobs',
    name: 'HRJobs',
    component: HRJobs,
    meta: { requiresAuth: true }
  },
  {
    path: '/hr/applications',
    name: 'HRApplications',
    component: HRApplications,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.getters.isAuthenticated) {
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router 