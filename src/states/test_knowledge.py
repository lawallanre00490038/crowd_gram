# src/states/test_knowledge.py

from aiogram.fsm.state import State, StatesGroup

class TestKnowledge(StatesGroup):
    """États pour le Test Your Knowledge - Translation Assessment"""
    ready_to_start = State()          # Bouton "Ready to start?"
    language_selection = State()      # Sélection de la langue cible
    translation_task = State()        # Saisie de la traduction
    validation_pending = State()      # En attente de validation
    # ajotuer etat validee? simulee
    
    # Image assessment states
    image_instructions = State()
    image_quiz = State()
    image_quiz_submission = State()
    image_quiz_feedback = State()

    # Image request assessment state
    image_2_instructions = State()
    image_2_quiz = State()
    image_2_quiz_submission = State()
    image_2_quiz_feedback = State()
    image_annotation = State()
    image_annotation_submission = State()
    image_annotation_feedback = State()


    # Audio assessment
    audio_instructions = State()
    audio_quiz = State()
    audio_quiz_submission = State()              
    