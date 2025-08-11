# pi3-histofy-backend

Este proyecto es un backend para la aplicación "Histofy". A continuación se describen los componentes principales del proyecto y cómo configurarlo.

## Estructura del Proyecto

```
pi3-histofy-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── auth.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   └── security.py
├── requirements.txt
└── README.md
```

## Descripción de Archivos

- **app/__init__.py**: Inicializa el paquete `app`. Puede contener configuraciones iniciales o importaciones de otros módulos.
  
- **app/main.py**: Punto de entrada de la aplicación. Configura y ejecuta la aplicación, incluyendo la inicialización de rutas y middleware.
  
- **app/auth.py**: Maneja la autenticación de usuarios, incluyendo funciones y clases para el inicio de sesión, registro y gestión de tokens.
  
- **app/models.py**: Define los modelos de datos utilizados en la aplicación, representando las entidades de la base de datos.
  
- **app/schemas.py**: Define los esquemas de validación de datos, utilizando bibliotecas como Pydantic para validar y serializar datos de entrada y salida.
  
- **app/database.py**: Configura la base de datos, incluyendo la conexión y la gestión de sesiones.
  
- **app/security.py**: Contiene funciones y utilidades relacionadas con la seguridad, como la encriptación de contraseñas y la gestión de permisos.
  
- **requirements.txt**: Lista las dependencias del proyecto, especificando las bibliotecas necesarias para que la aplicación funcione correctamente.

## Instalación

1. Clona el repositorio:
   ```
   git clone <URL_DEL_REPOSITORIO>
   cd pi3-histofy-backend
   ```

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Ejecución

Para ejecutar la aplicación, utiliza el siguiente comando:
```
python app/main.py
```

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT.