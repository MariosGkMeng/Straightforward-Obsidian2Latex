# Set working directory to script location
Set-Location $PSScriptRoot

# Run pdflatex with shell-escape for minted package and nonstopmode to continue on errors
pdflatex -interaction=nonstopmode -shell-escape example_writing.tex
bibtex example_writing
pdflatex -interaction=nonstopmode -shell-escape example_writing.tex
pdflatex -interaction=nonstopmode -shell-escape example_writing.tex

# Check if PDF was created
if (Test-Path "example_writing.pdf") {
    Write-Host "PDF generated successfully!"
    Invoke-Item "example_writing.pdf"
} else {
    Write-Host "Error: PDF generation failed!"
    exit 1
}
