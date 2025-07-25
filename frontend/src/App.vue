<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
        <router-link to="/" class="navbar-brand">
          <i class="fas fa-hamburger me-2"></i>
          Big Kahuna Burger HR
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link to="/jobs" class="nav-link">
                <i class="fas fa-briefcase me-1"></i>Jobs
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/candidate" class="nav-link">
                <i class="fas fa-user me-1"></i>Candidate Portal
              </router-link>
            </li>
          </ul>
          
          <ul class="navbar-nav">
            <li class="nav-item" v-if="!isAuthenticated">
              <router-link to="/login" class="nav-link">
                <i class="fas fa-sign-in-alt me-1"></i>HR Login
              </router-link>
            </li>
            <li class="nav-item dropdown" v-if="isAuthenticated">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                <i class="fas fa-user-circle me-1"></i>{{ currentUser?.full_name }}
              </a>
              <ul class="dropdown-menu">
                <li><router-link to="/hr/dashboard" class="dropdown-item">Dashboard</router-link></li>
                <li><router-link to="/hr/jobs" class="dropdown-item">Manage Jobs</router-link></li>
                <li><router-link to="/hr/applications" class="dropdown-item">Applications</router-link></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click="logout">Logout</a></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <main class="flex-grow-1">
      <router-view />
    </main>

    <footer class="bg-dark text-white py-4 mt-5">
      <div class="container text-center">
        <p>&copy; 2024 Big Kahuna Burger. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'App',
  computed: {
    ...mapGetters(['isAuthenticated', 'currentUser'])
  },
  methods: {
    ...mapActions(['logout'])
  },
  mounted() {
    // Check if user is logged in on app start
    const token = localStorage.getItem('token')
    if (token) {
      this.$store.dispatch('checkAuthStatus')
    }
  }
}
</script>

<style>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar-brand {
  font-weight: bold;
  font-size: 1.5rem;
}

main {
  flex: 1;
}

.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  transition: box-shadow 0.15s ease-in-out;
}

.card:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

.text-kahuna {
  color: #e67e22 !important;
}

.bg-kahuna {
  background-color: #e67e22 !important;
}
</style> 