# src/states/test_knowledge.py

from aiogram.fsm.state import State, StatesGroup

class TestKnowledge(StatesGroup):
    """États pour le Test Your Knowledge - Translation Assessment"""
    ready_to_start = State()          # Bouton "Ready to start?"
    language_selection = State()      # Sélection de la langue cible
    translation_task = State()        # Saisie de la traduction
    validation_pending = State()      # En attente de validation
    # ajotuer etat validee? simulee

    
    
    # Image Assessment states
    image_task = State()
    image_submission = State()
    image_feedback = State()
    
    
    # Video Assessment state
    video_task = State()
    video_submission = State()
    video_submission = State()
    


    # Audio assessment
    audio_instructions = State()
    audio_quiz = State()
    audio_quiz_submission = State()              
    
    
    
