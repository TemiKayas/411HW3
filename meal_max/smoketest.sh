#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Meal Management
#
##########################################################

clear_all_meals() {
  echo "Wiping out the meal list..."
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"' && echo "Meals cleared."
}

add_new_meal() {
  meal_name=$1
  cuisine_type=$2
  cost=$3
  level=$4

  echo "Inserting new meal ($meal_name - $cuisine_type, $cost) into the database..."
  reply=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal_name\", \"cuisine\":\"$cuisine_type\", \"price\":$cost, \"difficulty\":\"$level\"}")
  if echo "$reply" | grep -q '"status": "combatant added"'; then
    echo "New meal successfully added."
  else
    echo "Error: Unable to add the meal."
    exit 1
  fi
}

remove_meal_by_id() {
  id=$1
  echo "Removing meal with ID ($id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$id")
  if echo "$response" | grep -q '"status": "meal deleted"'; then 
    echo "Meal with ID ($id) removed successfully."
  else
    echo "Error: Deletion of meal with ID ($id) failed."
    exit 1
  fi
}

fetch_meal_by_id() {
  id=$1

  echo "Fetching meal details by ID ($id)..."
  output=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$id")
  if echo "$output" | grep -q '"status": "success"'; then
    echo "Meal data retrieved successfully for ID ($id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal details in JSON format (ID $id):"
      echo "$output" | jq .
    fi
  else
    echo "Error: Could not retrieve meal for ID ($id)."
    exit 1
  fi
}

search_meal_by_name() {
  name=$1

  echo "Searching for meal by name ($name)..."
  data=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$name")
  if echo "$data" | grep -q '"status": "success"'; then
    echo "Successfully found meal by name ($name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON data (Name $name):"
      echo "$data" | jq .
    fi
  else
    echo "Error: Meal with name ($name) not found."
    exit 1
  fi
}


############################################################
#
# Combatant Setup & Battle Control
#
############################################################

wipe_combatants() {
  echo "Erasing all combatants..."
  outcome=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$outcome" | grep -q '"status": "combatants cleared"'; then
    echo "All combatants removed successfully."
  else
    echo "Error: Could not clear combatants."
    exit 1
  fi
}

list_combatants() {
  echo "Retrieving list of combatants..."
  result=$(curl -s -X GET "$BASE_URL/get-combatants")
  if echo "$result" | grep -q '"status": "success"'; then
    echo "Combatants list retrieved."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants in JSON:"
      echo "$result" | jq .
    fi
  else
    echo "Error: Unable to retrieve combatants."
    exit 1
  fi
}

register_combatant() {
  meal_title=$1 
  echo "Registering meal titled '$meal_title' as combatant"
  feedback=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
    -d "{\"meal\": \"$meal_title\"}")
  if echo "$feedback" | grep -q '"status": "combatant prepared"'; then
    echo "Meal titled '$meal_title' successfully registered as combatant."
  else
    echo "Error: Could not register meal titled '$meal_title' as combatant."
    exit 1
  fi
}

engage_battle() {
  echo "Starting a new battle between combatants..."
  battle_result=$(curl -s -X GET "$BASE_URL/battle")
  if echo "$battle_result" | grep -q '"status": "battle complete"'; then
    victor=$(echo "$battle_result" | jq -r '.winner')
    echo "Battle concluded. Victorious combatant: $victor"
  else
    echo "Battle initiation failed."
    exit 1
  fi
}


######################################################
#
# Ranking Table
#
######################################################

# Retrieve leaderboard sorted based on wins or winning rate
retrieve_leaderboard() {
  order=$1  # Choose either "wins" or "win_pct"
  echo "Retrieving leaderboard, ordered by $order..."
  leaderboard_data=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$order")
  if echo "$leaderboard_data" | grep -q '"status": "success"'; then
    echo "Leaderboard fetched successfully (ordered by $order)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON data (ordered by $order):"
      echo "$leaderboard_data" | jq .
    fi
  else
    echo "Error: Failed to fetch leaderboard."
    exit 1
  fi
}


#!/bin/bash

# Test Health Checks
echo "Running health checks..."
check_health
check_db

# Clear all meals and combatants for a clean test environment
echo "Resetting data..."
clear_all_meals
wipe_combatants

# Add meals with varied properties
echo "Adding test meals..."
add_new_meal "Sushi" "Japanese" 12.50 "MED"
add_new_meal "Burger" "American" 10.00 "LOW"
add_new_meal "Paella" "Spanish" 30.00 "HIGH"
add_new_meal "Lasagna" "Italian" 18.00 "MED"
add_new_meal "Croissant" "French" 5.00 "LOW"

# Remove a specific meal by ID (use a specific ID based on the sequence above if known, or adapt based on your DB setup)
echo "Testing deletion of meal by ID..."
remove_meal_by_id 3

# Retrieve a meal by ID and by name to confirm the meal data
echo "Fetching meals to validate additions..."
fetch_meal_by_id 2
search_meal_by_name "Sushi"

# Test combatant registration
echo "Registering meals as combatants..."
register_combatant "Sushi"
register_combatant "Burger"

# Confirm combatant list retrieval
echo "Listing all registered combatants..."
list_combatants

# Start a battle between combatants and check for a winner
echo "Initiating a battle and checking results..."
engage_battle

# Retrieve leaderboard to verify sorting by wins
echo "Fetching leaderboard sorted by wins..."
retrieve_leaderboard "wins"

# Retrieve leaderboard to verify sorting by win percentage
echo "Fetching leaderboard sorted by win percentage..."
retrieve_leaderboard "win_pct"

# Additional retrieval tests for validation
echo "Validating meal retrieval post-battle..."
fetch_meal_by_id 1
search_meal_by_name "Croissant"

# Final cleanup
echo "Clearing data at end of tests..."
clear_all_meals
wipe_combatants

# Confirm all data is cleared
echo "Validating that data has been cleared..."
list_combatants
fetch_meal_by_id 1

echo "All tests completed successfully!"