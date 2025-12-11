#!/bin/sh

cd /config

# Check if config.template.yaml changed in git
if ! git diff --quiet frigate/config.template.yaml; then
    #git add frigate/config.template.yaml
    #git commit -m "Update Frigate config template: $(date)"
    # Optional: enable this ONLY if you want auto-push
    # git push
    echo "COMMITTED"    
else
    echo "NOCHANGE"
fi
