#!/bin/sh

input="/config/frigate/config.yaml"
output="/config/frigate/config.template.yaml"

tmpfile="$output.tmp"

# Start from real config
cp "$input" "$tmpfile"

###############################################
# GENERIC PASSWORD / USER / TOKEN SANITIZATION
###############################################

# Replace common credential keys (password, user, token, etc.)
sed -i \
  -e 's/^\(\s*password:\s*\).*/\1YOUR_PASSWORD_HERE/' \
  -e 's/^\(\s*pass:\s*\).*/\1YOUR_PASSWORD_HERE/' \
  -e 's/^\(\s*user:\s*\).*/\1YOUR_USER_HERE/' \
  -e 's/^\(\s*username:\s*\).*/\1YOUR_USER_HERE/' \
  -e 's/^\(\s*mqtt_user:\s*\).*/\1YOUR_USER_HERE/' \
  -e 's/^\(\s*mqtt_password:\s*\).*/\1YOUR_PASSWORD_HERE/' \
  -e 's/^\(\s*api_key:\s*\).*/\1YOUR_API_KEY_HERE/' \
  -e 's/^\(\s*token:\s*\).*/\1YOUR_TOKEN_HERE/' \
  -e 's/^\(\s*secret:\s*\).*/\1YOUR_SECRET_HERE/' \
  "$tmpfile"

###############################################
# SANITIZE RTSP/HTTP URLs WITH EMBEDDED CREDS
###############################################

# Replace username:password@ inside URLs
sed -i \
  -e 's#rtsp://[^:@]*:[^@]*@#rtsp://USERNAME:PASSWORD@#g' \
  -e 's#http://[^:@]*:[^@]*@#http://USERNAME:PASSWORD@#g' \
  -e 's#https://[^:@]*:[^@]*@#https://USERNAME:PASSWORD@#g' \
  "$tmpfile"

###############################################
# SANITIZE LONG STRINGS THAT LOOK LIKE TOKENS
###############################################

# Base64-like strings >20 chars (common in NVR keys, deepstack, etc.)
sed -i \
  -E 's/([A-Za-z0-9+\/=]{20,})/REDACTED_TOKEN/g' \
  "$tmpfile"

###############################################
# IF CLEANED VERSION DIFFERS FROM EXISTING → REPLACE
###############################################

if ! cmp -s "$tmpfile" "$output"; then
    mv "$tmpfile" "$output"
    echo "UPDATED"
else
    rm "$tmpfile"
    echo "NOCHANGE"
fi
