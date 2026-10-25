param([string]$Docx, [string]$Pdf)
# Converts a .docx to .pdf with Microsoft Word (fields such as page numbers are updated)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($Docx, $false, $true)
    $doc.Fields.Update() | Out-Null
    $doc.SaveAs([ref]$Pdf, [ref]17)
    $doc.Close([ref]0)
} finally {
    $word.Quit()
}
