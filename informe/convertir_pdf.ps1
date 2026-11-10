# Convierte el informe .docx a PDF con Microsoft Word y actualiza el indice
# automatico (campo TOC) para que las paginas del PDF coincidan.
#
# El documento se abre en modo solo lectura: el .docx generado por
# build_reporte.py queda intacto y el PDF es el unico artefacto que cambia.
#
# Word responde de forma asincrona a la automatizacion COM. Se deja una espera
# breve despues de abrir y despues de actualizar el indice para no recibir
# RPC_E_CALL_REJECTED.
#
# El PDF se escribe con un nombre temporal y luego se renombra sobre el nombre
# final, para no dejar a Word esperando el bloqueo del PDF anterior.
#
# Cada etapa queda registrada en convertir_pdf.log: si Word se bloquea, el log
# indica en que llamada ocurrio. Antes de reintentar conviene cerrar cualquier
# instancia de Word que haya quedado abierta por una corrida anterior.

param(
    [string]$Docx  = (Join-Path $PSScriptRoot "Informe_Actividad4_Tejiendo_Redes.docx"),
    [string]$Tmp   = (Join-Path $PSScriptRoot "_export_tmp.pdf"),
    [string]$Final = (Join-Path $PSScriptRoot "Informe_Actividad4_Tejiendo_Redes.pdf")
)

$ErrorActionPreference = "Stop"
$log = Join-Path $PSScriptRoot "convertir_pdf.log"
function Log($m) { Add-Content -Path $log -Value ("{0:HH:mm:ss} {1}" -f (Get-Date), $m) -Encoding UTF8 }
Set-Content -Path $log -Value "" -Encoding UTF8

Log "inicio $Docx"
if (-not (Test-Path $Docx)) { throw "no existe el docx: $Docx" }
if (Test-Path $Tmp) { Remove-Item $Tmp -Force }

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$word.AutomationSecurity = 3
Log "word listo"

$doc = $word.Documents.Open($Docx, $false, $true, $false)
Log "abierto"
Start-Sleep -Seconds 2

foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
Log "indice"
Start-Sleep -Seconds 1

$doc.Repaginate()
Log "repaginado"

$doc.SaveAs2($Tmp, 17)
Log "guardado"

$pages = $doc.ComputeStatistics(2)
$doc.Close($false)
$word.Quit()
Log "fin paginas=$pages"

Move-Item $Tmp $Final -Force

Write-Output "PDF=$Final"
Write-Output "PAGES=$pages"
