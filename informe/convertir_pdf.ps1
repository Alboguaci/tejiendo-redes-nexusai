# Convierte el informe .docx a PDF con Microsoft Word y actualiza el indice
# automatico (campo TOC) para que las paginas del PDF coincidan.
#
# El documento se abre en modo solo lectura: el .docx generado por
# build_reporte.py queda intacto y el PDF es el unico artefacto que cambia.
#
# Word responde de forma asincrona a la automatizacion COM. Se deja una espera
# breve despues de abrir y despues de actualizar el indice para no recibir
# RPC_E_CALL_REJECTED.

$ErrorActionPreference = "Stop"

$docx = Join-Path $PSScriptRoot "Informe_Actividad4_Tejiendo_Redes.docx"
$pdf  = Join-Path $PSScriptRoot "Informe_Actividad4_Tejiendo_Redes.pdf"

if (Test-Path $pdf) { Remove-Item $pdf -Force }

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

$doc = $word.Documents.Open($docx, $false, $true)
Start-Sleep -Seconds 1

foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
Start-Sleep -Seconds 2

$doc.Repaginate()
$pages = $doc.ComputeStatistics(2)
$words = $doc.ComputeStatistics(0)

$doc.ExportAsFixedFormat($pdf, 17, $false, 0, 0, 0, 0, 0, $true, $true, 0, $true, $true, $false)
$doc.Close($false)
$word.Quit()

Write-Output "PDF=$pdf"
Write-Output "PAGES=$pages WORDS=$words"
