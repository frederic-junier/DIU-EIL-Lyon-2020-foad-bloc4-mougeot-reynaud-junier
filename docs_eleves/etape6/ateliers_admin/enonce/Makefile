FILE=$(wildcard *.md)
TARGET=$(FILE:.md=.pdf)  $(FILE:.md=.html)  $(FILE:.md=.docx)   

all: $(TARGET)

%.pdf: %.md
	pandoc -s $<    -o $@

	
%.html: %.md
	pandoc -s   -c  --mathjax --toc  -V toc-title:"Table des matières"  $< -o $@

	
%.docx: %.md
	pandoc   $< -o $@
