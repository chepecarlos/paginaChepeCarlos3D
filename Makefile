PY?=$(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
PELICAN?=$(if $(wildcard .venv/bin/pelican),.venv/bin/pelican,pelican)
PELICANOPTS=
UV?=uv

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py

GITHUB_PAGES_BRANCH=gh-pages
GITHUB_PAGES_COMMIT_MESSAGE=Generate Pelican site


DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

RELATIVE ?= 0
ifeq ($(RELATIVE), 1)
	PELICANOPTS += --relative-urls
endif

SERVER ?= "0.0.0.0"

PORT ?= 0
ifneq ($(PORT), 0)
	PELICANOPTS += -p $(PORT)
endif


help:
	@echo 'Makefile for a pelican Web site                                           '
	@echo '                                                                          '
	@echo 'Usage:                                                                    '
	@echo '   make install                        instala dependencias con uv        '
	@echo '   make install-frozen                 instala exacto desde uv.lock       '
	@echo '   make instagram-feed                sync del feed local al sitio        '
	@echo '   make instagram-feed-urls           descarga imagenes desde post_url    '
	@echo '   make instagram-feed-latest USERNAME=... trae ultimos posts del perfil  '
	@echo '   make instagram-feed-build          sync + build local completo         '
	@echo '   make optimize-images               optimiza imagenes de productos      '
	@echo '   make optimize-images-force         reprocesa todas las imagenes         '
	@echo '   make optimize-images-report        muestra ahorro total original vs webp'
	@echo '   make html                           (re)generate the web site          '
	@echo '   make clean                          remove the generated files         '
	@echo '   make regenerate                     regenerate files upon modification '
	@echo '   make publish                        generate using production settings '
	@echo '   make serve [PORT=8000]              serve site at http://localhost:8000'
	@echo '   make serve-global [SERVER=0.0.0.0]  serve (as root) to $(SERVER):80    '
	@echo '   make devserver [PORT=8000]          serve and regenerate together      '
	@echo '   make devserver-global               regenerate and serve on 0.0.0.0    '
	@echo '   make github                         upload the web site via gh-pages   '
	@echo '                                                                          '
	@echo 'Set the DEBUG variable to 1 to enable debugging, e.g. make DEBUG=1 html   '
	@echo 'Set the RELATIVE variable to 1 to enable relative urls                    '
	@echo '                                                                          '

install:
	"$(UV)" sync

install-frozen:
	"$(UV)" sync --frozen

instagram-feed:
	"$(PY)" scripts/sync_instagram_feed.py

instagram-feed-urls:
	"$(PY)" scripts/sync_instagram_feed.py --mode manual_urls

instagram-feed-latest:
	"$(PY)" scripts/sync_instagram_feed.py --mode profile_latest --username "$(USERNAME)"

prebuild: instagram-feed
	@$(MAKE) optimize-images

optimize-images:
	"$(PY)" scripts/optimize_images.py \
		--content-path "$(INPUTDIR)" \
		--source-dir images \
		--dest-dir images_opt \
		--products-subdir productos \
		--quality 72 \
		--formats ".jpg,.jpeg,.png"

optimize-images-force:
	"$(PY)" scripts/optimize_images.py \
		--content-path "$(INPUTDIR)" \
		--source-dir images \
		--dest-dir images_opt \
		--products-subdir productos \
		--quality 72 \
		--formats ".jpg,.jpeg,.png" \
		--force

optimize-images-report:
	"$(PY)" scripts/report_image_savings.py \
		--content-path "$(INPUTDIR)" \
		--source-dir images \
		--dest-dir images_opt \
		--products-subdir productos \
		--formats ".jpg,.jpeg,.png"

instagram-feed-build: clean instagram-feed html

html: prebuild
	"$(PELICAN)" "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

clean:
	[ ! -d "$(OUTPUTDIR)" ] || rm -rf "$(OUTPUTDIR)"

regenerate:
	"$(PELICAN)" -r "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

serve:
	"$(PELICAN)" -l "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

serve-global:
	"$(PELICAN)" -l "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS) -b $(SERVER)

devserver:
	"$(PELICAN)" -lr "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

devserver-global:
	"$(PELICAN)" -lr "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS) -b 0.0.0.0

publish: prebuild
	"$(PELICAN)" "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(PUBLISHCONF)" $(PELICANOPTS)

github: publish
	ghp-import -m "$(GITHUB_PAGES_COMMIT_MESSAGE)" -b $(GITHUB_PAGES_BRANCH) "$(OUTPUTDIR)" --no-jekyll
	git push origin $(GITHUB_PAGES_BRANCH)


.PHONY: install install-frozen instagram-feed instagram-feed-urls instagram-feed-latest prebuild optimize-images optimize-images-force optimize-images-report instagram-feed-build html help clean regenerate serve serve-global devserver devserver-global publish github
