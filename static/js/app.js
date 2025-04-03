const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

// Evento para abrir form de registro
signUpButton.addEventListener('click', () =>
  container.classList.add('right-panel-active')
);

// Evento para regresar al form de iniciar sesión
signInButton.addEventListener('click', () =>
  container.classList.remove('right-panel-active')
);

  // Cuenta regresiva
  const countdownElement = document.getElementById('countdown');
  if (countdownElement) {
      let tiempoRestante = parseInt(countdownElement.textContent);

      const interval = setInterval(() => {
          tiempoRestante--;
          countdownElement.textContent = tiempoRestante;

          if (tiempoRestante <= 0) {
              clearInterval(interval);
              location.reload(); // Recargar la página cuando termine la cuenta regresiva
          }
      }, 1000);
  }