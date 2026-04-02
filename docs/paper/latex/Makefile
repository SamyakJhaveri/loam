# Makefile — ParBench SC26 LaTeX build pipeline
# Usage: make        (builds paper.pdf)
#        make clean  (removes build artifacts)
#        make view   (opens PDF in default viewer)

MAIN = paper
TEX  = $(MAIN).tex
PDF  = $(MAIN).pdf
BIB  = references

.PHONY: all clean view

all: $(PDF)

$(PDF): $(TEX) $(BIB).bib
	pdflatex -interaction=nonstopmode $(MAIN)
	bibtex $(MAIN)
	pdflatex -interaction=nonstopmode $(MAIN)
	pdflatex -interaction=nonstopmode $(MAIN)

clean:
	rm -f $(MAIN).{aux,bbl,blg,log,out,pdf,toc,lof,lot,fls,fdb_latexmk,synctex.gz}
	rm -f appendices.{aux}

view: $(PDF)
	xdg-open $(PDF) 2>/dev/null || open $(PDF) 2>/dev/null
