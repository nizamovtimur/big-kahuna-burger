<template>
  <div id="app">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-danger">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <i class="fas fa-hamburger"></i> Big Kahuna Burger HR
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/jobs">Jobs</router-link>
            </li>
            <li class="nav-item" v-if="isAuthenticated">
              <router-link class="nav-link" to="/candidate-portal">Portal</router-link>
            </li>
            <li class="nav-item" v-if="isAuthenticated && isHR">
              <router-link class="nav-link" to="/hr/dashboard">HR Dashboard</router-link>
            </li>
          </ul>
          
          <ul class="navbar-nav">
            <li class="nav-item" v-if="!isAuthenticated">
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
            <li class="nav-item" v-if="isAuthenticated">
              <span class="navbar-text me-3">
                Welcome, {{ currentUser?.full_name || currentUser?.username }}!
              </span>
            </li>
            <li class="nav-item" v-if="isAuthenticated">
              <button class="btn btn-outline-light btn-sm" @click="logout">
                <i class="fas fa-sign-out-alt"></i> Logout
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>



    <!-- Main Content -->
    <main>
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-light py-4 mt-5">
      <div class="container">
        <div class="row">
          <div class="col-md-6">
            <h5><i class="fas fa-hamburger"></i> Big Kahuna Burger</h5>
            <p>The best burgers in town!</p>
          </div>
          <div class="col-md-6">
            <h6>Contact Us</h6>
            <p>Phone: (555) 123-KAHUNA<br>
               Email: careers@bigkahuna.com<br>
               Address: 123 Burger Lane, Food City, FC 12345</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'App',
  computed: {
    ...mapGetters(['isAuthenticated', 'currentUser', 'isHR'])
  },
  methods: {
    ...mapActions(['logout']),
    async logout() {
      await this.$store.dispatch('logout')
      this.$router.push('/login')
    }
  },
  async created() {
    // Check if user is already logged in
    const token = localStorage.getItem('token')
    if (token) {
      this.$store.commit('SET_TOKEN', token)
      await this.$store.dispatch('checkAuth')
    }
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}

.navbar-brand {
  font-weight: bold;
  font-size: 1.3rem;
}

.alert {
  border-radius: 0;
}

/* Vulnerable styling - allows potential CSS injection */
.user-content {
  /* WARNING: This allows arbitrary HTML/CSS - XSS vulnerability */
}

.chat-message {
  /* WARNING: Direct HTML rendering without sanitization */
}

.job-description {
  /* WARNING: Raw HTML content displayed */
}
</style> 