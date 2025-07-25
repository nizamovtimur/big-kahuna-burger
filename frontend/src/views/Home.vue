<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero bg-primary text-white py-5">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-lg-6">
            <h1 class="display-4 fw-bold mb-4">
              Welcome to Big Kahuna Burger HR Platform
            </h1>
            <p class="lead mb-4">
              Discover exciting career opportunities at Big Kahuna Burger, where we serve the most delicious burgers and build amazing careers!
            </p>
            <div class="d-flex gap-3">
              <router-link to="/jobs" class="btn btn-light btn-lg">
                <i class="fas fa-search me-2"></i>Browse Jobs
              </router-link>
              <router-link to="/candidate" class="btn btn-outline-light btn-lg">
                <i class="fas fa-comments me-2"></i>Chat with AI
              </router-link>
            </div>
          </div>
          <div class="col-lg-6 text-center">
            <i class="fas fa-hamburger text-kahuna" style="font-size: 10rem;"></i>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-5">
      <div class="container">
        <div class="text-center mb-5">
          <h2 class="fw-bold">Why Choose Big Kahuna Burger?</h2>
          <p class="text-muted">Join our team and be part of something special</p>
        </div>
        
        <div class="row g-4">
          <div class="col-md-4">
            <div class="card h-100 text-center">
              <div class="card-body">
                <i class="fas fa-users text-primary mb-3" style="font-size: 3rem;"></i>
                <h5 class="card-title">Great Team</h5>
                <p class="card-text">Work with passionate people who love what they do and support each other's growth.</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-4">
            <div class="card h-100 text-center">
              <div class="card-body">
                <i class="fas fa-chart-line text-success mb-3" style="font-size: 3rem;"></i>
                <h5 class="card-title">Career Growth</h5>
                <p class="card-text">Advance your career with comprehensive training programs and promotion opportunities.</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-4">
            <div class="card h-100 text-center">
              <div class="card-body">
                <i class="fas fa-heart text-danger mb-3" style="font-size: 3rem;"></i>
                <h5 class="card-title">Great Benefits</h5>
                <p class="card-text">Enjoy competitive salaries, health benefits, and free meals during your shifts.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Recent Jobs Section -->
    <section class="py-5 bg-light">
      <div class="container">
        <div class="text-center mb-5">
          <h2 class="fw-bold">Latest Job Openings</h2>
          <p class="text-muted">Check out our current opportunities</p>
        </div>
        
        <div class="row g-4" v-if="featuredJobs.length > 0">
          <div class="col-md-6 col-lg-4" v-for="job in featuredJobs" :key="job.id">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">{{ job.title }}</h5>
                <p class="text-muted mb-2">
                  <i class="fas fa-map-marker-alt me-1"></i>{{ job.location }}
                </p>
                <p class="text-muted mb-3">
                  <i class="fas fa-building me-1"></i>{{ job.department }}
                </p>
                <p class="card-text">{{ job.description.substring(0, 100) }}...</p>
                <router-link :to="`/jobs/${job.id}`" class="btn btn-primary">
                  View Details
                </router-link>
              </div>
            </div>
          </div>
        </div>
        
        <div class="text-center mt-4">
          <router-link to="/jobs" class="btn btn-outline-primary btn-lg">
            View All Jobs
          </router-link>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-5 bg-kahuna text-white">
      <div class="container text-center">
        <h2 class="fw-bold mb-4">Ready to Join Our Team?</h2>
        <p class="lead mb-4">Start your journey with Big Kahuna Burger today!</p>
        <router-link to="/candidate" class="btn btn-light btn-lg">
          <i class="fas fa-rocket me-2"></i>Get Started
        </router-link>
      </div>
    </section>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Home',
  data() {
    return {
      featuredJobs: []
    }
  },
  computed: {
    ...mapGetters(['allJobs'])
  },
  methods: {
    ...mapActions(['fetchJobs'])
  },
  async mounted() {
    await this.fetchJobs()
    // Get first 3 jobs for featured section
    this.featuredJobs = this.allJobs.slice(0, 3)
  }
}
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
}

.card {
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-5px);
}

.text-kahuna {
  color: #e67e22;
}

.bg-kahuna {
  background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);
}
</style> 