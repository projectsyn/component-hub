# ---------- STEP 1 ----------
# Build the documentation in web format
FROM vshn/antora:2.3.3 AS antora

WORKDIR /build
COPY . /build
RUN make html antora_cmd=antora antora_opts=--fetch

# ---------- STEP 2 ----------
# Docker image only containing nginx and the freshly built documentation
FROM vshn/nginx:1.18.0

# Finally, copy the contents of the documentation to be served
COPY --from=antora /build/_public /usr/share/nginx/html

