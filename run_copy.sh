#!/bin/bash
# Script to call the copy inspection data endpoint
# Make sure you're logged in to the system first

curl -X POST "https://carscraping-production.up.railway.app/api/copy-inspection-data" \
  -H "Content-Type: application/json" \
  --cookie-jar cookies.txt \
  --cookie cookies.txt

echo ""
echo "Done!"
