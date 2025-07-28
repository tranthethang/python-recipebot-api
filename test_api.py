#!/usr/bin/env python3
"""
Simple test script to verify the RecipeBot API functionality.
"""

import requests
import json
import time

def test_health_check():
    """Test the health check endpoint."""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_recipe_generation():
    """Test the recipe generation endpoint."""
    try:
        # Test with valid ingredients
        valid_request = {
            "ingredients": ["2kg pork", "1kg potatoes", "0.5kg onions"]
        }
        
        response = requests.post(
            "http://localhost:8000/api/recipe",
            json=valid_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Recipe Generation: {response.status_code}")
        if response.status_code == 200:
            recipe_data = response.json()
            print("Recipe generated successfully!")
            print(f"Title: {recipe_data['recipe']['title']}")
            print(f"Cooking Time: {recipe_data['recipe']['cooking_time']}")
            print(f"Ingredients: {len(recipe_data['recipe']['ingredients'])} items")
            print(f"Instructions: {len(recipe_data['recipe']['instructions'])} steps")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Recipe generation test failed: {e}")
        return False

def test_invalid_request():
    """Test with invalid request format."""
    try:
        invalid_request = {
            "ingredients": ["pork", "potatoes"]  # Missing quantities
        }
        
        response = requests.post(
            "http://localhost:8000/api/recipe",
            json=invalid_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Invalid Request Test: {response.status_code}")
        if response.status_code == 422:
            print("Validation error handled correctly")
            return True
        else:
            print(f"Unexpected response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Invalid request test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing RecipeBot API...")
    print("=" * 50)
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Run tests
    health_ok = test_health_check()
    print()
    
    recipe_ok = test_recipe_generation()
    print()
    
    validation_ok = test_invalid_request()
    print()
    
    # Summary
    print("=" * 50)
    print("Test Results:")
    print(f"Health Check: {'✓' if health_ok else '✗'}")
    print(f"Recipe Generation: {'✓' if recipe_ok else '✗'}")
    print(f"Validation: {'✓' if validation_ok else '✗'}")
    
    if all([health_ok, recipe_ok, validation_ok]):
        print("\n🎉 All tests passed! RecipeBot API is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the API implementation.")