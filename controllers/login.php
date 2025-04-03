<?php
// Procesar el formulario cuando se envía
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Configuración de la base de datos (cambia estos valores)
    $db_host = 'localhost';
    $db_user = 'root';
    $db_pass = '';
    $db_name = 'porta';
    
    // Conectar a MySQL
    $conn = new mysqli($db_host, $db_user, $db_pass, $db_name);
    
    // Verificar conexión
    if ($conn->connect_error) {
        die("Error de conexión: " . $conn->connect_error);
    }

    // Obtener y limpiar los datos del formulario
    $nombre = trim($_POST['nombre']);
    $email = trim($_POST['email']);
    $contrasena = trim($_POST['contrasena']);

    // Validar los datos
    if (empty($nombre) || empty($email) || empty($contrasena)) {
        $mensaje = "Por favor completa todos los campos.";
        $exito = false;
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $mensaje = "Por favor ingresa un correo electrónico válido.";
        $exito = false;
    } else {
        // Usar consultas preparadas para evitar inyección SQL
        $stmt = $conn->prepare("INSERT INTO usuarios (nombre, email, contrasena) VALUES (?, ?, ?)");
        
        // Hashear la contraseña antes de almacenarla
        $contrasena_hash = password_hash($contrasena, PASSWORD_BCRYPT);
        
        $stmt->bind_param("sss", $nombre, $email, $contrasena_hash);

        if ($stmt->execute()) {
            $mensaje = "¡Cuenta registrada exitosamente!";
            $exito = true;
            $_POST = array(); // Limpiar los campos del formulario
        } else {
            $mensaje = "Error al registrar el usuario: " . $stmt->error;
            $exito = false;
        }
        $stmt->close();
    }

    $conn->close();
}
?>

