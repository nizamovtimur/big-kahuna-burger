<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero-section bg-primary text-white py-5">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-lg-6">
            <h1 class="display-4 fw-bold">
              <i class="fas fa-hamburger"></i> Big Kahuna Burger
            </h1>
            <h2 class="h3 mb-4">HR Platform</h2>
            <p class="lead mb-4">
              Welcome to our comprehensive HR platform for managing job applications, 
              candidate interactions, and recruitment processes.
            </p>
            <div class="d-grid gap-2 d-md-flex">
              <router-link to="/jobs" class="btn btn-warning btn-lg me-md-2">
                <i class="fas fa-search"></i> Browse Jobs
              </router-link>
              <router-link to="/login" class="btn btn-outline-light btn-lg">
                <i class="fas fa-user"></i> Get Started
              </router-link>
            </div>
          </div>
          <div class="col-lg-6">
            <div class="text-center">
              <i class="fas fa-users display-1"></i>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section py-5">
      <div class="container">
        <div class="row text-center mb-5">
          <div class="col">
            <h2 class="display-5 fw-bold mb-3">Platform Features</h2>
            <p class="lead">Everything you need for modern recruitment</p>
          </div>
        </div>

        <div class="row g-4">
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center">
                <div class="feature-icon mb-3">
                  <i class="fas fa-robot fa-3x text-primary"></i>
                </div>
                <h5 class="card-title">AI-Powered Chat</h5>
                <p class="card-text">
                  Chat with our intelligent assistant to learn about job opportunities 
                  and company culture. Get instant answers to your questions.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center">
                <div class="feature-icon mb-3">
                  <i class="fas fa-file-pdf fa-3x text-success"></i>
                </div>
                <h5 class="card-title">Smart CV Analysis</h5>
                <p class="card-text">
                  Upload your CV and get AI-powered analysis of your compatibility 
                  with job requirements. Instant feedback on your application.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center">
                <div class="feature-icon mb-3">
                  <i class="fas fa-chart-line fa-3x text-info"></i>
                </div>
                <h5 class="card-title">HR Dashboard</h5>
                <p class="card-text">
                  Comprehensive dashboard for HR managers to track applications, 
                  manage job postings, and make data-driven hiring decisions.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>



    <!-- Get Started Section -->
    <section class="cta-section py-5">
      <div class="container">
        <div class="row">
          <div class="col-lg-8 mx-auto text-center">
            <h2 class="display-6 mb-4">Ready to Get Started?</h2>
            <p class="lead mb-4">
              Join Big Kahuna Burger and explore our exciting career opportunities!
            </p>
            
            <div class="row g-3">
              <div class="col-md-6">
                <div class="card">
                  <div class="card-body">
                    <h5 class="card-title">
                      <i class="fas fa-user-tie"></i> For Candidates
                    </h5>
                    <p class="card-text">
                      Browse job openings, chat with our AI assistant, and submit applications.
                    </p>
                    <router-link to="/jobs" class="btn btn-primary">
                      View Jobs
                    </router-link>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="card">
                  <div class="card-body">
                    <h5 class="card-title">
                      <i class="fas fa-users-cog"></i> For HR Managers
                    </h5>
                    <p class="card-text">
                      Manage job postings, review applications, and analyze candidate data.
                    </p>
                    <router-link to="/login" class="btn btn-success">
                      HR Login
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>


  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
}

.feature-icon {
  transition: transform 0.3s ease;
}

.card:hover .feature-icon {
  transform: scale(1.1);
}

.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.alert-danger {
  border-left: 5px solid #dc3545;
}
</style> 