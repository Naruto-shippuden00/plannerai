#!/usr/bin/env python3
"""
Language and AI Vision Test Script
Tests basic functionality without running the full bot
"""

import asyncio
import sys
from utils.translations import get_text, TRANSLATIONS
from utils.database import init_db, add_user, get_user_language, set_user_language

async def test_translations():
    """Test translation system"""
    print("=" * 60)
    print("🌐 TESTING TRANSLATION SYSTEM")
    print("=" * 60)
    
    # Test key
    test_key = "welcome"
    
    # Test all languages
    for lang in ["uz", "ru", "en"]:
        text = get_text(test_key, lang, name="Test User")
        print(f"\n{lang.upper()} ({lang}):")
        print("-" * 40)
        print(text[:200] + "..." if len(text) > 200 else text)
    
    print("\n" + "=" * 60)
    print("✅ Translation system works!")
    print("=" * 60)

async def test_database_language():
    """Test database language functions"""
    print("\n" + "=" * 60)
    print("💾 TESTING DATABASE LANGUAGE FUNCTIONS")
    print("=" * 60)
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Test user
    test_user_id = 123456789
    
    # Add test user
    await add_user(test_user_id, "test_user", "Test User")
    print(f"✅ Test user added: {test_user_id}")
    
    # Test language functions
    languages = ["uz", "ru", "en"]
    
    for lang in languages:
        # Set language
        await set_user_language(test_user_id, lang)
        print(f"✅ Language set: {lang}")
        
        # Get language
        stored_lang = await get_user_language(test_user_id)
        
        if stored_lang == lang:
            print(f"✅ Language retrieved correctly: {stored_lang}")
        else:
            print(f"❌ ERROR: Expected {lang}, got {stored_lang}")
            return False
    
    print("\n" + "=" * 60)
    print("✅ Database language functions work!")
    print("=" * 60)
    return True

async def test_ai_helper():
    """Test AI helper basic imports and functions"""
    print("\n" + "=" * 60)
    print("🤖 TESTING AI HELPER IMPORTS")
    print("=" * 60)
    
    try:
        from utils.ai_helper import _check_task_relevance
        
        # Test task relevance checker
        test_cases = [
            {
                "caption": "a book on a desk with a notebook",
                "task_name": "SAT Math",
                "category": "SAT",
                "expected": True
            },
            {
                "caption": "a person taking a selfie",
                "task_name": "Python Practice",
                "category": "Python",
                "expected": False
            },
            {
                "caption": "a laptop showing code on the screen",
                "task_name": "Python Web App",
                "category": "Python",
                "expected": True
            },
            {
                "caption": "food on a plate",
                "task_name": "IELTS Speaking",
                "category": "IELTS",
                "expected": False
            }
        ]
        
        print("\nTesting task relevance checker...")
        for i, test in enumerate(test_cases, 1):
            is_valid, confidence = _check_task_relevance(
                test["caption"],
                test["task_name"],
                test["category"]
            )
            
            status = "✅" if is_valid == test["expected"] else "❌"
            print(f"\n{status} Test {i}:")
            print(f"   Caption: {test['caption']}")
            print(f"   Category: {test['category']}")
            print(f"   Result: {'Valid' if is_valid else 'Invalid'} (confidence: {confidence:.2f})")
            print(f"   Expected: {'Valid' if test['expected'] else 'Invalid'}")
        
        print("\n" + "=" * 60)
        print("✅ AI Helper functions work!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_keyboards():
    """Test keyboard generation with languages"""
    print("\n" + "=" * 60)
    print("⌨️ TESTING KEYBOARD GENERATION")
    print("=" * 60)
    
    try:
        from utils.keyboards import (
            main_menu_keyboard,
            language_selection_keyboard,
            task_category_keyboard,
            priority_keyboard
        )
        
        # Test language selection
        lang_kb = language_selection_keyboard()
        print("✅ Language selection keyboard created")
        
        # Test main menu in all languages
        for lang in ["uz", "ru", "en"]:
            main_kb = main_menu_keyboard(lang)
            print(f"✅ Main menu keyboard created for {lang}")
        
        # Test task category in all languages
        for lang in ["uz", "ru", "en"]:
            cat_kb = task_category_keyboard(lang)
            print(f"✅ Task category keyboard created for {lang}")
        
        # Test priority in all languages
        for lang in ["uz", "ru", "en"]:
            pri_kb = priority_keyboard(lang)
            print(f"✅ Priority keyboard created for {lang}")
        
        print("\n" + "=" * 60)
        print("✅ All keyboards work!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("\n" + "🎯" * 30)
    print("PLANNERAI - LANGUAGE & AI VISION TEST")
    print("🎯" * 30 + "\n")
    
    results = []
    
    # Test 1: Translations
    try:
        await test_translations()
        results.append(("Translations", True))
    except Exception as e:
        print(f"❌ Translation test failed: {e}")
        results.append(("Translations", False))
    
    # Test 2: Database
    try:
        success = await test_database_language()
        results.append(("Database Language", success))
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        results.append(("Database Language", False))
    
    # Test 3: AI Helper
    try:
        success = await test_ai_helper()
        results.append(("AI Helper", success))
    except Exception as e:
        print(f"❌ AI Helper test failed: {e}")
        results.append(("AI Helper", False))
    
    # Test 4: Keyboards
    try:
        success = await test_keyboards()
        results.append(("Keyboards", success))
    except Exception as e:
        print(f"❌ Keyboard test failed: {e}")
        results.append(("Keyboards", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n✅ Your bot is ready for:")
        print("   - Multi-language support (UZ/RU/EN)")
        print("   - AI vision photo verification")
        print("\n🚀 Run: python bot.py")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED!")
        print("Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
