@echo off
REM Build and run Factory Pulse as a single container (frontend + API) with podman.
REM Usage: deploy\deploy-local.cmd [up|down|logs]   (default: up)  ->  http://localhost:4000
REM Configuration comes from the repo-root .env (required for "up").
setlocal
cd /d "%~dp0.."
set "ROOT=%CD%"
set "ENV_FILE=%ROOT%\.env"
set "ACTION=%~1"
if "%ACTION%"=="" set "ACTION=up"
if not defined IMAGE set "IMAGE=factory-pulse"
if not defined NAME set "NAME=factory-pulse"
if not defined HOST_PORT set "HOST_PORT=4000"

where podman >nul 2>nul
if errorlevel 1 (
  echo [deploy-local] podman not found.
  exit /b 1
)

if /i "%ACTION%"=="down" ( podman rm -f %NAME% & exit /b 0 )
if /i "%ACTION%"=="logs" ( podman logs -f %NAME% & exit /b 0 )
if /i not "%ACTION%"=="up" (
  echo Usage: %~nx0 [up^|down^|logs]
  exit /b 1
)

if not exist "%ENV_FILE%" (
  echo [deploy-local] %ENV_FILE% not found. Create it ^(copy .env.example to .env^) and rerun.
  exit /b 1
)
echo [deploy-local] Using %ENV_FILE%

REM VITE_* values are public and baked into the frontend bundle at build time.
set "MAPS_KEY="
set "MAPS_ID="
for /f "usebackq tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
  if "%%A"=="VITE_GOOGLE_MAPS_API_KEY" set "MAPS_KEY=%%B"
  if "%%A"=="VITE_GOOGLE_MAPS_MAP_ID" set "MAPS_ID=%%B"
)

podman build -t %IMAGE% -f deploy/Dockerfile --build-arg "VITE_GOOGLE_MAPS_API_KEY=%MAPS_KEY%" --build-arg "VITE_GOOGLE_MAPS_MAP_ID=%MAPS_ID%" .
if errorlevel 1 exit /b 1
podman rm -f %NAME% >nul 2>nul
REM Everything in .env becomes the container environment; PORT is forced to the container port.
podman run -d --name %NAME% -p %HOST_PORT%:4000 --env-file "%ENV_FILE%" -e PORT=4000 %IMAGE%
if errorlevel 1 exit /b 1
echo [deploy-local] Running at http://localhost:%HOST_PORT%
