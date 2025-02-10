# Check de jugadores suspendidos FCF

Este proyecto extrae información sobre jugadores sancionados y los compara con las alineaciones de las jornadas posteriores para verificar si han jugado cuando no debían.

## 📌 Funcionalidad

1. Obtiene todas las jornadas de la liga para determinar qué jugadores han jugado.
2. Extrae la lista de jugadores sancionados desde la web de la Federación Catalana de Fútbol.
3. Compara los jugadores sancionados con las alineaciones de las jornadas posteriores.
4. Genera alertas si un jugador sancionado aparece en una alineación cuando no debería.
5. Almacena la información en una base de datos SQLite con SQLAlchemy.

## 🛠️ Requisitos

- Python 3.8+
- Bibliotecas necesarias:
  - `requests`
  - `beautifulsoup4`
  - `sqlalchemy`

Puedes instalar las dependencias con:
```bash
pip install requests beautifulsoup4 sqlalchemy
```

## 🚀 Uso

### 1️⃣ Obtener y guardar jugadores sancionados en la base de datos
```python
from main import get_all_suspended_players, save_suspended_players_in_db

issues = get_all_suspended_players()
save_suspended_players_in_db(issues)
```

### 2️⃣ Verificar si algún jugador sancionado ha jugado en jornadas posteriores
```python
from main import check_suspended_players

check_suspended_players()
```

## 📂 Estructura del Proyecto
```
/
│── main.py                # Código principal del programa
│── save_in_database.py    # Configuración de la base de datos con SQLAlchemy
│── README.md              # Documento con instrucciones
```

## 🗄️ Base de Datos
Se usa **SQLite** para almacenar la información. Se definen dos tablas principales:

- **`suspended_players`**: Jugadores sancionados con detalles de la sanción.
- **`MatchdayPlayers`**: Registro de jugadores alineados en cada jornada.

## 🔧 Funciones principales

### 🔹 `get_suspended_players(matchday)`
Obtiene la lista de jugadores sancionados en una jornada específica desde la web de la FCF.

### 🔹 `get_hrefs_matchdays(matchday)`
Obtiene los enlaces de los partidos jugados en una jornada.

### 🔹 `get_match_lineups(hrefs, matchday)`
Extrae los jugadores que han jugado en una jornada específica.

### 🔹 `save_suspended_players_in_db(all_suspended_players)`
Guarda los jugadores sancionados en la base de datos SQLite.

### 🔹 `check_suspended_players()`
Compara los jugadores sancionados con las alineaciones de jornadas posteriores para verificar si han jugado cuando no debían.

## 📌 Notas
- Los datos se extraen de la web de la **Federación Catalana de Fútbol**.
- Asegúrate de que la estructura de la página no cambie, ya que el código depende de `BeautifulSoup` para extraer datos.
- Se usa `SQLAlchemy` para interactuar con la base de datos.

## 📝 Autor
**Pmarc21**

---
¡Cualquier mejora o sugerencia es bienvenida! 🚀
