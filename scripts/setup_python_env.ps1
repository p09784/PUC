# setup_python_env.ps1
# Tenta detectar/instalar Python (via winget quando possível) e instalar dependências

Write-Host "Verificando disponibilidade de 'py' e 'python'..."

$pyCmd = Get-Command py -ErrorAction SilentlyContinue
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

function Test-PythonLauncher {
    param($launcher)
    try {
        & $launcher --version > $null 2>&1
        return $true
    } catch {
        return $false
    }
}

if ($pyCmd -and (Test-PythonLauncher py)) {
    Write-Host "Launcher 'py' funcional." -ForegroundColor Green
} elseif ($pythonCmd -and (Test-PythonLauncher python)) {
    Write-Host "Comando 'python' funcional." -ForegroundColor Green
} else {
    Write-Host "Python não encontrado ou apontando para Microsoft Store stub." -ForegroundColor Yellow
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        Write-Host "Tentando instalar Python via winget..." -ForegroundColor Cyan
        winget install --id Python.Python.3 -e --source winget --accept-package-agreements --accept-source-agreements
        Write-Host "Instalação iniciada. Feche e reabra o PowerShell e execute o script novamente." -ForegroundColor Green
        exit 0
    } else {
        Write-Host "winget não disponível. Baixe e instale Python manualmente: https://www.python.org/downloads/windows/" -ForegroundColor Red
        Write-Host "Também verifique Settings -> Apps -> App execution aliases e desative/ative entradas de 'Python' conforme necessário." -ForegroundColor Yellow
        exit 1
    }
}

# Se chegou aqui, temos py ou python funcionais — instalar requirements
$repoRoot = Convert-Path "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\.."
$reqPath = Join-Path $repoRoot "SQA\requirements.txt"

if (-Not (Test-Path $reqPath)) {
    Write-Host "Arquivo requirements.txt não encontrado em: $reqPath" -ForegroundColor Red
    exit 1
}

Write-Host "Instalando dependências do $reqPath ..." -ForegroundColor Cyan
try {
    & py -3 -m pip install --user -r $reqPath
    Write-Host "Dependências instaladas com sucesso." -ForegroundColor Green
} catch {
    Write-Host "Falha ao instalar dependências com 'py'. Tente executar manualmente:" -ForegroundColor Red
    Write-Host "  py -3 -m pip install --user -r .\\SQA\\requirements.txt"
    exit 1
}

Write-Host "Pronto. Agora você pode executar: py -3 .\\SQA\\qualidade_ar.py" -ForegroundColor Green
