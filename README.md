# JIRA Metrics Dashboard

![JIRA Metrics Dashboard](https://img.shields.io/badge/JIRA-Metrics%20Dashboard-blue)

## Descripción

JIRA Metrics Dashboard es una aplicación web que permite visualizar métricas de JIRA, incluyendo el número de issues creadas, resueltas, y su distribución por organización y tipo de solicitud. La aplicación está construida con Flask y utiliza Chart.js para la visualización de datos.

## Características

- Visualización de issues creadas y resueltas en un gráfico de líneas.
- Tablas que muestran el número total de issues, issues abiertas y cerradas por organización.
- Tablas que muestran el número total de issues por tipo de solicitud y su distribución por organización.
- Selector de fechas para filtrar los datos mostrados.

## Instalación

### Prerrequisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. Clona el repositorio:

    ```bash
    git clone https://github.com/tu-usuario/JiraSoporte.git
    cd JiraSoporte
    ```

2. Crea un entorno virtual y actívalo:

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3. Instala las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

4. Configura las variables de entorno en el archivo `config.py`:

    ```python
    JIRA_URL = "https://tu-dominio.atlassian.net/"
    JIRA_USER = "tu-correo@dominio.com"
    JIRA_API_TOKEN = "tu-api-token"
    PROJECT_CODE = "CODIGO_DEL_PROYECTO"
    ```

## Uso

1. Inicia la aplicación Flask:

    ```bash
    python app.py
    ```

2. Abre tu navegador web y navega a `http://127.0.0.1:5000`.

3. Selecciona las fechas de inicio y fin, y haz clic en "Fetch Data" para visualizar las métricas.

## Estructura del Proyecto

```
JiraSoporte/
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── datepicker.js
│   │   ├── charts.js
│   │   ├── tables.js
│   │   └── scripts.js
├── templates/
│   └── index.html
├── .gitignore
├── app.py
├── config.py
├── jira_api.py
├── requirements.txt
└── README.md
```

## Contribución

¡Las contribuciones son bienvenidas! Si deseas contribuir a este proyecto, por favor sigue los siguientes pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -am 'Agrega nueva funcionalidad'`).
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Si tienes alguna pregunta o sugerencia, no dudes en contactarme a través de [tu-correo@dominio.com](norefice+jiraSoporte@gmail.com).
