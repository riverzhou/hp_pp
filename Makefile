# make clean

exclude_dirs := .git 

dirs := $(shell find . -maxdepth 1 -type d)
dirs := $(basename $(patsubst ./%,%,$(dirs)))
dirs := $(filter-out $(exclude_dirs),$(dirs))

clean_dirs := $(addprefix _clean_,$(dirs))

.PHONY: $(clean_dirs) clean

clean:  $(clean_dirs)
	@echo 
	@echo '=========== All Project Cleaned ! ==========='
	@echo 

$(clean_dirs):
	@$(MAKE) clean -C $(patsubst _clean_%,%,$@)



