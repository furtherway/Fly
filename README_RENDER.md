# Despliegue en Render · TIM

Guía paso a paso para deployear **Trademark Insights México** en Render.com.

---

## Resumen rápido

| Archivo | Para qué sirve |
|---|---|
| `requirements.txt` | Dependencias Python (Flask, Playwright, pandas, xgboost, etc.) |
| `build.sh` | Instala Chromium + libs de sistema durante el build |
| `render.yaml` | Blueprint de IaC — define el servicio, env vars, disco |
| `Procfile` | Comando de arranque alternativo (si no usas blueprint) |
| `runtime.txt` | Pin de Python 3.11.9 |
| `.gitignore` | Excluye venv, .env, outputs, .playwright |
| `.env.example` | Plantilla de variables para correr local |

---

## Paso 1 · Preparar el repositorio

```bash
# Estructura final esperada
tim/
├── app.py              ← tu Flask server
├── ORCH_ONE.py         ← motor de scraping
├── requirements.txt
├── build.sh
├── render.yaml
├── Procfile
├── runtime.txt
├── .gitignore
└── README_RENDER.md
```

```bash
# Hacer build.sh ejecutable
chmod +x build.sh

# Subir a GitHub
git init
git add .
git commit -m "Setup deploy en Render"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/tim.git
git push -u origin main
```

---

## Paso 2 · Deploy en Render (opción A · con blueprint)

Es la opción **recomendada**. Render lee `render.yaml` y configura todo solo.

1. Entra a **https://dashboard.render.com**
2. Clic en **New +** → **Blueprint**
3. Conecta tu repo de GitHub
4. Render detecta `render.yaml` y muestra un preview del servicio
5. **Apply** → empieza el build
6. En el primer deploy, Render te pedirá las variables marcadas `sync: false`:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
7. Espera ~5-8 min al primer build (instala Chromium + apt deps)
8. Cuando veas **Live**, abre la URL `https://tim-trademark-insights.onrender.com`

---

## Paso 2 · Deploy en Render (opción B · manual)

Si prefieres no usar blueprint:

1. **New +** → **Web Service** → conecta tu repo
2. Configura:
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: copia el contenido de `Procfile` (la línea después de `web:`)
   - **Plan**: Starter ($7/mes) o superior
3. **Environment** → agrega las variables de `.env.example`
4. **Advanced** → habilita **Auto-Deploy**
5. **Create Web Service**

---

## Paso 3 · Verificar Playwright

Una vez **Live**, revisa los logs del primer arranque:

```
Dashboard → Service → Logs
```

Busca:

```
→ Instalando Chromium para Playwright…
→ Instalando librerías de sistema para Chromium…
✓ Build completo
```

Para probar OMPI desde la app: corre un análisis con **1 sola clase** primero para validar que Chromium arranca sin errores. Si ves `Browser closed unexpectedly` o `libnss3 not found`, falta alguna lib en `build.sh` — revisa los logs.

---

## Plan recomendado y por qué

| Plan | RAM | Sleep | ¿Sirve para TIM? |
|---|---|---|---|
| **Free** | 512 MB | sí (15 min idle) | ⚠ marginal — Chromium pide ~400MB |
| **Starter** | 512 MB | no | ✓ recomendado para uso ligero |
| **Standard** | 2 GB | no | ✓ ideal si scrapeas muchas clases |
| **Pro** | 4 GB | no | sólo si paralelas decenas de marcas |

El plan **Free** funciona pero al despertar tarda ~50 seg, y Chromium con 512MB es justo. Para un wizard interactivo como TIM, **Starter** es el mínimo cómodo.

---

## Variables de entorno (resumen)

Configura en **Dashboard → Service → Environment**:

| Variable | Valor | Notas |
|---|---|---|
| `SUPABASE_URL` | `https://xxx.supabase.co` | tu proyecto |
| `SUPABASE_ANON_KEY` | `eyJ...` | anon key, no service role |
| `PYTHON_VERSION` | `3.11.9` | ya lo fija render.yaml |
| `PLAYWRIGHT_BROWSERS_PATH` | `/opt/render/project/src/.playwright` | ya lo fija render.yaml |
| `PYTHONUNBUFFERED` | `1` | logs en tiempo real |
| `SECRET_KEY` | string aleatorio | si tu app usa sesiones Flask |

---

## Troubleshooting

### "playwright._impl._errors.Error: Browser closed unexpectedly"
Falta una lib de sistema. En los logs busca el `error while loading shared libraries: libXXX.so.N` y agrégala al `apt-get install` de `build.sh`.

### "Out of memory" durante un análisis
Chromium consume ~300-450MB por instancia. Soluciones:
- Sube de plan (Starter → Standard)
- En `ORCH_ONE.py`, agrega `--single-process` a los args de `chromium.launch()`
- Limita el análisis a clases por lotes pequeños

### El Excel no se descarga después del análisis
Si tu `app.py` guarda en `outputs/` y luego el filesystem se reinicia, el archivo se pierde. El `disk` que define `render.yaml` lo monta en `/opt/render/project/src/outputs` y persiste.

### El SSE (logs en vivo) se corta a los 30 seg
Revisa que el `startCommand` tenga `--timeout 0` (ya está en `render.yaml` y `Procfile`). Render no impone timeout adicional en streams.

### Build pasa de 20 min
Por defecto Render corta builds largos. Si pasa, considera pre-compilar wheels o subir a un plan que permita más build minutes.

### El módulo MUA no arranca
Render no tiene Microsoft Edge instalado y no es trivial. Dos opciones:
1. Modificar el módulo MUA para usar Chromium (ya disponible)
2. Hacer ese módulo opcional con un toggle, deshabilitado en producción

---

## Costo estimado

- **Starter**: $7 USD/mes (512MB, sin sleep, 0.5 CPU)
- **Disk de 1GB**: $0.25 USD/mes
- **Total**: ~$7.25 USD/mes

Si arrancas en **Free** para validar y luego escalas, los datos del disco no se transfieren — exporta antes.

---

## Workflow de actualización

Después del primer deploy, cualquier cambio se publica con:

```bash
git add .
git commit -m "fix: bug en wizard"
git push
```

Render detecta el push y hace auto-deploy en ~3-5 min (no reinstala Chromium si no cambió `requirements.txt`).
