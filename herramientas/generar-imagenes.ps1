# Genera las imagenes de un video a partir de un plan JSON.
#
#   .\generar-imagenes.ps1 -Plan "...\produccion\plan.json" -Destino "...\imagenes"
#
# Reanudable: salta las imagenes que ya existen en el destino, asi que si se
# corta a mitad basta con volver a lanzarlo. No repite ni cobra dos veces.
#
# Va en PowerShell y no en Python porque el proceso de Python no tiene acceso
# al directorio global de npm donde vive la CLI de Higgsfield.

param(
  [Parameter(Mandatory=$true)][string]$Plan,
  [Parameter(Mandatory=$true)][string]$Destino,
  [int]$Hilos = 4,
  [int]$MaxEsperas = 60   # tope por trabajo: ~5 min. Evita el bucle infinito.
)

$ErrorActionPreference = "Continue"
$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
New-Item -ItemType Directory -Force $Destino | Out-Null
$log = Join-Path (Split-Path $Plan) "progreso.txt"

function Registrar($txt) {
  $linea = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $txt
  Write-Output $linea
  Add-Content -Path $log -Value $linea -Encoding UTF8
}

$plan = Get-Content $Plan -Raw -Encoding UTF8 | ConvertFrom-Json
$pendientes = @($plan | Where-Object { -not (Test-Path (Join-Path $Destino ($_.id + ".png"))) })
Registrar "pendientes: $($pendientes.Count) de $($plan.Count)"
if ($pendientes.Count -eq 0) { Registrar "nada que hacer"; exit 0 }

$cola = New-Object System.Collections.Queue
foreach ($p in $pendientes) { $cola.Enqueue($p) | Out-Null }
$activos = @{}; $esperas = @{}; $hechas = 0; $fallos = @()

while ($cola.Count -gt 0 -or $activos.Count -gt 0) {
  while ($activos.Count -lt $Hilos -and $cola.Count -gt 0) {
    $item = $cola.Peek()
    $out = higgsfield generate create flux_2 --prompt $item.prompt --aspect-ratio 16:9 --resolution 1k --variant pro 2>&1 | Out-String
    $m = [regex]::Match($out, '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
    if ($m.Success) {
      $cola.Dequeue() | Out-Null
      $activos[$item.id] = $m.Value
      $esperas[$item.id] = 0
    } else { Start-Sleep -Seconds 5; break }
  }

  Start-Sleep -Seconds 5

  foreach ($id in @($activos.Keys)) {
    $esperas[$id]++
    if ($esperas[$id] -gt $MaxEsperas) {
      $fallos += $id; Registrar "sin resolver, se abandona: $id"; $activos.Remove($id); continue
    }
    $est = higgsfield generate get $activos[$id] 2>&1 | Out-String
    if ($est -match 'completed') {
      $url = ([regex]::Match($est, 'https://\S+')).Value
      if ($url) {
        try {
          Invoke-WebRequest -Uri $url -OutFile (Join-Path $Destino "$id.png") -UseBasicParsing -TimeoutSec 90
          $hechas++
          if ($hechas % 15 -eq 0 -or $hechas -eq 1) { Registrar "$hechas/$($pendientes.Count) (ultima: $id)" }
        } catch { $fallos += $id; Registrar "descarga fallo: $id" }
      }
      $activos.Remove($id)
    } elseif ($est -match 'failed') {
      $fallos += $id; Registrar "job fallo: $id"; $activos.Remove($id)
    }
  }
}

Registrar "TERMINADO  hechas: $hechas  fallos: $($fallos.Count)"
if ($fallos.Count) { Registrar ("fallaron: " + ($fallos -join ", ")) }
Registrar ("total png: " + (Get-ChildItem $Destino -Filter *.png).Count)
Registrar (higgsfield account status 2>&1 | Out-String).Trim()
