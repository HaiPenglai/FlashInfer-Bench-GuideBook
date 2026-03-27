# 实验报告模板 Makefile

MAIN = minimal-acm
export PATH := /root/texlive/bin/x86_64-linux:$(PATH)
LATEX = pdflatex

.PHONY: all clean cleanall force

# 默认目标
all: force
	@echo "Compiling $(MAIN).tex..."
	$(LATEX) $(MAIN)
	$(LATEX) $(MAIN)
	@echo "Done: $(MAIN).pdf"

# 强制目标（确保每次 make 都执行）
force:

# 清理临时文件
clean:
	@rm -f *.aux *.log *.out *.bbl *.blg *.fdb_latexmk *.fls *.synctex.gz
	@echo "Cleaned temporary files."

# 完全清理（包括 PDF）
cleanall: clean
	@rm -f $(MAIN).pdf
	@echo "Cleaned all including PDF."
