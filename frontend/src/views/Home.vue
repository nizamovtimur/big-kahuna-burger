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
            <h2 class="h3 mb-4">HR Платформа</h2>
            <p class="lead mb-4">
              Добро пожаловать на нашу комплексную HR платформу для управления заявками на работу, 
              взаимодействия с кандидатами и процессов найма.
            </p>
            <div class="d-grid gap-2 d-md-flex">
              <router-link to="/jobs" class="btn btn-warning btn-lg me-md-2">
                <i class="fas fa-search"></i> Просмотреть вакансии
              </router-link>
              <router-link to="/login" class="btn btn-outline-light btn-lg">
                <i class="fas fa-user"></i> Начать
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
            <h2 class="display-5 fw-bold mb-3">Возможности платформы</h2>
            <p class="lead">Всё необходимое для современного рекрутинга</p>
          </div>
        </div>

        <div class="row g-4">
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center">
                <div class="feature-icon mb-3">
                  <i class="fas fa-robot fa-3x text-primary"></i>
                </div>
                <h5 class="card-title">ИИ-помощник</h5>
                <p class="card-text">
                  Общайтесь с нашим интеллектуальным помощником, чтобы узнать о возможностях трудоустройства 
                  и корпоративной культуре. Получайте мгновенные ответы на ваши вопросы.
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
                <h5 class="card-title">Умный анализ резюме</h5>
                <p class="card-text">
                  Загрузите ваше резюме и получите анализ совместимости с требованиями вакансии на основе ИИ. 
                  Мгновенная обратная связь по вашей заявке.
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
                <h5 class="card-title">HR Панель</h5>
                <p class="card-text">
                  Комплексная панель для HR менеджеров для отслеживания заявок, 
                  управления вакансиями и принятия решений о найме на основе данных.
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
            <h2 class="display-6 mb-4">Готовы начать?</h2>
            <p class="lead mb-4">
              Присоединяйтесь к Big Kahuna Burger и изучите наши захватывающие карьерные возможности!
            </p>
            
            <div class="row g-3">
              <div class="col-md-6">
                <div class="card">
                  <div class="card-body">
                    <h5 class="card-title">
                      <i class="fas fa-user-tie"></i> Для кандидатов
                    </h5>
                    <p class="card-text">
                      Просматривайте вакансии, общайтесь с нашим ИИ-помощником и подавайте заявки.
                    </p>
                    <router-link to="/jobs" class="btn btn-primary">
                      Посмотреть вакансии
                    </router-link>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="card">
                  <div class="card-body">
                    <h5 class="card-title">
                      <i class="fas fa-users-cog"></i> Для HR менеджеров
                    </h5>
                    <p class="card-text">
                      Управляйте вакансиями, рассматривайте заявки и анализируйте данные кандидатов.
                    </p>
                    <router-link to="/login" class="btn btn-success">
                      HR Вход
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