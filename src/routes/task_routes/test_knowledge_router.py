from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.utils.markdown import hbold
from src.keyboards.inline import quiz_options_kb
from src.states.test_knowledge import TestKnowledge
from src.utils.test_knowledge import create_language_selection_keyboard, create_ready_button, create_task_ready_keyboard, load_json_file
from src.constant.test_knowledge_constant import AVAILABLE_LANGUAGES, SAMPLE_TEXTS
import random
import asyncio
from pathlib import Path

router = Router()
#to Get the video_id Values

# @router.message(F.text == "/preload_videos")
# async def preload_videos(message: Message):
#     for v in video_quiz_data:
#         sent = await message.answer_video(video=FSInputFile(v['video']))
#         v['video_id'] = sent.video.file_id
#         print(f"{v['video']} => {sent.video.file_id}")

#     for v in video_2_quiz_data:
#         sent = await message.answer_video(video=FSInputFile(v['video']))
#         v['video_id'] = sent.video.file_id
#         print(f"{v['video']} => {sent.video.file_id}")


# Load image quiz data
quiz_data = load_json_file(Path("src/data/image_quiz.json"))

# Image task
image_quiz_data = quiz_data['image_task']
image_openEnd = random.sample(image_quiz_data['image_openEnd'], 2)
image_closeEnd = random.sample(image_quiz_data['image_closeEnd'], 2)
image_request = random.sample(image_quiz_data['image_request'], 2)

# Video task

# Load video quiz data
video_quiz_data = load_json_file(Path("src/data/video_quiz.json"))
# Pick a video task @random
video_tasks = random.sample(video_quiz_data, 2)
video_2_quiz_data = load_json_file(Path("src/data/video_2_quiz.json"))
# Pick 2 task @random
video_2_tasks = random.sample(video_2_quiz_data, 2)


@router.message(F.text == "/start_test_knowledge")
async def start_knowledge_test(message: Message, state: FSMContext):
    """Point d'entrée pour Test Your Knowledge"""
    await handle_start_knowledge_assessment(message, state)

async def handle_start_knowledge_assessment(message: Message, state: FSMContext):
    """Fonction appelée depuis onboarding pour démarrer l'assessment"""
    
    welcome_text = (
        "🧠 Next Step: Knowledge Assessment\n\n"
        "Before you start earning, we'll test your knowledge with a few practical tasks:\n"
        "• 📝 Text Annotation\n"
        "• 🎵 Audio Recording\n" 
        "• 🖼️ Image Annotation\n"
        "• 🎥 Video Annotation\n\n"
        "This helps us assign you the right tasks for your skill level!\n\n"
    )
    await message.answer(welcome_text, reply_markup=create_ready_button())
    await state.set_state(TestKnowledge.ready_to_start)

@router.callback_query(TestKnowledge.ready_to_start, F.data == "ready_start")
async def handle_ready_start(callback: CallbackQuery, state: FSMContext):
    """Utilisateur a cliqué Ready to start"""
    await callback.answer()
    
    instructions_text = (
        "Awesome!\n"
        "Let's start with the text translation task!\n\n"  
        " 📋 Instructions:\n"
        "• You'll receive a short text\n"
        "• Translate it accurately to Yoruba\n"
        "• Write your translation as a text message\n"
        "• Focus on accuracy and natural flow\n\n"
    )
        
    await callback.message.answer(instructions_text)
    await asyncio.sleep(2)
    await handle_begin_translation(callback, state)



def select_sample_text(target_lang_code):
    sample_map = {
        "français": "english_to_french",
        "yoruba": "english_to_yoruba", 
        "hausa": "english_to_hausa",
        "swahili": "english_to_swahili",
        "igbo": "english_to_igbo",
        "pidgin": "english_to_pidgin",       
    }

    
    return sample_map.get(target_lang_code, "english_to_default")  # Par défaut si langue non trouvée

@router.callback_query(TestKnowledge.language_selection, F.data == "begin_translation")
async def handle_begin_translation(callback: CallbackQuery, state: FSMContext):
    #display text for task
    await callback.answer()
    

    sample_text = SAMPLE_TEXTS["english_to_yoruba"]["text"]
    
    translation_text = (
        f"Here is the text to translate from English to Yoruba:\n\n"
        f"---\n"
        f'"{sample_text}"\n'
        f"---\n\n"
        f" Make sure the translation is accurate and natural!\n"
        f"Type your translation below ⬇️"
        )
    
    await callback.message.answer(translation_text)
    await state.set_state(TestKnowledge.translation_task)

@router.message(TestKnowledge.translation_task)
async def handle_translation_submission(message: Message, state: FSMContext):
    """Gestion de la soumission de traduction"""
    
    if not message.text:
        await message.answer(" ❌ Please send your translation as text.")
        return
        
    user_translation = message.text.strip()
    await state.update_data(user_translation=user_translation)
    
    sample_text = SAMPLE_TEXTS["english_to_yoruba"]["text"]
    

    confirmation_text = (
        "✅ Translation Received!\n\n"  
        f"Original (English):\n"
        f'"{sample_text}"\n\n'
        f"Your Yoruba translation:\n"  
        f'"{user_translation}"\n\n'
        f"⏳ Status: Submitted for validation\n"
        f"🔔 Next: You'll be notified when reviewed\n\n"
    )
    
    await message.answer(confirmation_text)
    
    # Simulation of validation
    await simulate_validation(message, state)

async def simulate_validation(message: Message, state: FSMContext):
    """Simulation du processus de validation"""

    await asyncio.sleep(3)
    
    data = await state.get_data()
    user_data = await state.get_data()
    
    #to change later
    validation_result = True  
    
    if validation_result:


        await message.answer(
            "(simulation) Good job! You have successfully completed the task ✅ " \
            "Your task has been approved!\n" 
            "Now, let's continue with the next task... [audio, image, video...)]")
        
        
        # Start image assessment
        await asyncio.sleep(3)
        
        # Image assessment instructions
        image_instructions_text = (
            "Great!\n"
            "Let's move to Image Annotation task!\n\n"
            "📋 Instructions:\n"
            "• You'll receive an image.\n"
            "• You would be requested to give a well detail description of the image\n\n"
            "Ready to begin the image test?"
        )
        
        image_ready_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🖼️ Start Image Test", callback_data="start_image_test")]
            ]
        )
        
        await message.answer(image_instructions_text, reply_markup=image_ready_kb)
        await state.set_state(TestKnowledge.image_instructions)
        

        print(f"✅ TRANSLATION PASSED - User {message.from_user.id}")
        print(f"Translation: {data.get('user_translation')}")
        
        
    else:
        failure_text = (
            "Assessment needs improvement\n\n"
            "Feedback: Your translation needs some work\n"
            "Next step: Please try the assessment again\n"
            "Tip: Review translation guidelines and try again"
        )
        
        await message.answer(failure_text)
        await state.clear()

# Image Assessment Handlers
@router.callback_query(TestKnowledge.image_instructions, F.data == "start_image_test")
async def handle_start_image_test(callback: CallbackQuery, state: FSMContext):
    """Start the image assessment"""
    await callback.answer()
    
    # Initialize image quiz data
    await state.update_data(current_q=0, num_q=2, target_language='Yoruba')
    await state.set_state(TestKnowledge.image_quiz) 
    
    # Send first image question
    await send_image_question(callback.message, state)

async def send_image_question(message: Message, state: FSMContext):
    """Send an image quiz question"""
    data = await state.get_data()
    q_index = data["current_q"]
    target_lang = data['target_language']
    
    if not image_openEnd:
        await message.answer("❌ No quiz data available")
        return
    
    if q_index >= len(image_openEnd):
        await message.answer("❌ Question index out of range")
        return
    
    selected_question = image_openEnd[q_index]
    print(f"📝 Selected question: {selected_question}")
    
    try:
        # Use FSInputFile for local image files
        image_file = FSInputFile(selected_question['image'])
        await message.answer_photo(
            photo=image_file,
            caption=f"❓{hbold(selected_question['question'])}\n\n Make sure to describe in {target_lang}."
        )
        print("✅ Image sent successfully")
        await state.set_state(TestKnowledge.image_quiz_submission)
    except Exception as e:
        print(f"❌ Error sending image: {e}")
        await message.answer(f"❌ Error loading image: {e}")
        # Try without image for debugging
        await message.answer(
            f"❓{hbold(selected_question['question'])}\n\n Make sure to describe in {target_lang}.",
        )
        await state.set_state(TestKnowledge.image_quiz_submission)

@router.message(TestKnowledge.image_quiz_submission)
async def handle_image_submission(message: Message, state: FSMContext):
    """Handle image quiz submission"""

    if not message.text:
        message.answer("❌ Please send your descriptions as text.")
        return

    user_annotation = message.text.strip()

    data = await state.get_data()
    target_lang = data.get("target_language")

    await state.update_data(user_annotation=user_annotation)

    confirmation_message = (
        "✅ Description Received!\n\n"  
        f"Your {target_lang} Description:\n"  
        f'"{user_annotation}"\n\n'
        f"⏳ Status: Submitted for validation\n"
        f"🔔 Next: You'll be notified when reviewed\n\n"
    )

    await message.answer(confirmation_message)

    await simulate_image_validation(message, state)
    
@router.message(TestKnowledge.image_quiz_feedback)
async def simulate_image_validation(message: Message, state: FSMContext):
    
    await asyncio.sleep(3)

    data = await state.get_data()
    q_index = data['current_q']
    num_q = data.get('num_q', 0)
    target_lang = data.get('target_language')
    user_annotation = data.get('user_annotation')
    sent_image = image_openEnd[q_index]['image']

    
    validation_result = True  # TODO: QA validation
    
   
    if validation_result:


        await message.answer(
            "(simulation) Good job! You have successfully completed the task ✅ " \
            "Your task has been approved!\n" 
            "Now, let's continue with the next task...")
            
        num_q -= 1
            
        if num_q > 0:
            await state.update_data(num_q=num_q, current_q=1)
            await send_image_question(message, state)
        else:
            # Image assessment completed!
            await message.answer("🎉 Image annotation test completed!")
            
            # Start image request and annotation
            await asyncio.sleep(3)

            # test instructions
            image_request_instructions = (
                "Nice job so far!\n"
                "Let's move on to next task (image Annotation)!\n\n"
                "📋 Instructions:\n"
                "You'll receive a theme and need to send an image that matches it.\n"
                "You’ll also be asked to provide a short description of the image you send.\n\n"
                "Ready to begin the test?"
            )
                
            image_2_ready_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                        [InlineKeyboardButton(text="🖼️ Start Image Test", callback_data="start_image_2_test")]
                ]
            )

            await message.answer(image_request_instructions, reply_markup=image_2_ready_kb)
            await state.set_state(TestKnowledge.image_2_instructions)

    else:
        failure_text = (
            "Feedback: Your descriptions needs some work\n"
            "Next step: Please try the assessment again\n"
            "Assessment need improvement\n\n"
            "Tip: Review description guidelines and try again.\n\n"
        )
        await message.answer("❌ Incorrect.")
        await message.answer(failure_text)
        await message.answer("Let's try again one more time.")

        await send_image_question(message, state)



# Image 2 Assessment Handlers
@router.callback_query(TestKnowledge.image_2_instructions, F.data == 'start_image_2_test')
async def handle_start_image_2_test(callback: CallbackQuery, state: FSMContext):
    """Start the image request assessment"""
    await callback.answer()

    # Initialize image quiz data
    await state.update_data(
        current_req_q = 0,
        num_req_q = 2
    )
    await state.set_state(TestKnowledge.image_2_quiz)

    await send_image_2_question(callback.message, state)


@router.message(TestKnowledge.image_2_quiz)
async def send_image_2_question(message: Message, state: FSMContext):
    data = await state.get_data()
    q_index = data.get('current_req_q', 0)
    num_req_q = data.get('num_req_q')
    target_lang = data.get('target_language')

    if not image_request:
        await message.answer("❌ No quiz data available")
        return
    
    if q_index >= len(image_request):
        await message.answer("❌ Question index out of range")
        return
    
    selected_question = image_request[q_index]
    print(f"📝 Selected question: {selected_question}")

    await message.answer(
        f"Awesome! Here's your theme  — share an image and describe it in {target_lang}:\n\n"
        f"---\n"
        f"Theme: {selected_question['theme']}\n"
        f"--\n\n"
        f"Describe it using: {selected_question['annotation_type']}\n"
        f"Guide: {selected_question['instruction']}\n"
        f"Example: {selected_question['example_prompt']}\n\n"
        f"Your {target_lang} description:\n"
    )

    await state.set_state(TestKnowledge.image_2_quiz_submission)

@router.message((F.content_type == ContentType.PHOTO) | (F.content_type == ContentType.DOCUMENT), StateFilter(TestKnowledge.image_2_quiz_submission))
async def receive_image_submission(message: Message, state: FSMContext):
    """Handle Submission"""
    if not message.photo:
        await message.answer(" ❌ Please send an image.")
        return
    
    photo = message.photo[-1]
    file_id = photo.file_id

    await state.update_data(photo_id=file_id)
    await message.answer(
        f"✅ Image received!\n\n"
        f"⏳ Status: Submitted for validation\n"
        f"🔔 Next: You'll be notified when reviewed\n\n"
    )

    await simulate_request_image_validation(message, state)


async def simulate_request_image_validation(message: Message, state: FSMContext):
    """Simulation of the sent image validation"""
    await asyncio.sleep(3)

    data = await state.get_data()
    photo_id = data.get('photo_id')
    index_q = data.get('current_req_q')
    selected_question = image_request[index_q]

    # QA check and approval
    image_validation_check = True # TODO: QA Team

    if image_validation_check:
        await message.answer(
            f"(Simulation) Good job! Your uploaded image has been successfully received and approved ✅\n" \
            "Now, let's continue with describing the uploaded image..."
        )

        await state.set_state(TestKnowledge.image_annotation)
        await image_annotation(message, state)
    
    else:
        failure_text = (
            "Image Quality Check Failed\n\n"
            "Feedback: The uploaded image does not meet our quality standards\n"
            "Next step: Please upload a clearer, relevant image\n"
            "Tip: Ensure the image is well-lit, in focus, and matches the given theme"
            )
        await message.answer(failure_text)

@router.message(TestKnowledge.image_annotation)
async def image_annotation(message: Message, state: FSMContext):
    """start Image Annotation (Audio / Text)"""

    data = await state.get_data()
    photo_id = data.get('photo_id')
    index_q = data.get('current_req_q')
    selected_question = image_request[index_q]
    target_lang = data.get("target_language")

    await message.answer_photo(
        photo=photo_id,
        caption=(
            f"✅ Your image for **{selected_question['theme']}** has been received and approved!\n\n"
            f"Now, please describe this image in **{target_lang}** using {hbold(selected_question['annotation_type'])}.\n"
            "Focus on what is happening, the people, objects, and actions you see.\n"
            "✔ Be detailed and accurate.\n"
            "✔ Use complete sentences.\n"
            "❌ Avoid unrelated details."
        )
    )
    
    await state.set_state(TestKnowledge.image_annotation_submission)

@router.message(TestKnowledge.image_annotation_submission, F.text | F.voice | F.audio)
async def handle_annotation(message: Message, state: FSMContext):
    data = await state.get_data()
    index_q = data.get('current_req_q')
    selected_question = image_request[index_q]
    target_lang = data.get("target_language")
    annotation_type = selected_question['annotation_type']
    
    # Validate that user sent the right type
    if annotation_type == "text" and message.text:
        annotation_value = message.text
    elif annotation_type == "audio" and (message.audio or message.voice):
        annotation_value = message.audio.file_id if message.audio else message.voice.file_id
    else:
        await message.answer(f"❌ Please send a valid {annotation_type} description.")
        return
    
    
    # Save annotation to state
    await state.update_data(annotation_value=annotation_value)
    
    await message.answer(
        f"✅ {annotation_type.capitalize()} description received!\n\n"
        f"⏳ Status: Submitted for validation\n"
        f"🔔 Next: You'll be notified when reviewed\n\n"
    )
    
    await simulate_image_annotation_validation(message, state)


async def simulate_image_annotation_validation(message: Message, state: FSMContext):
    """Simulation of the sent annotation validation"""
    await asyncio.sleep(3)

    data = await state.get_data()
    annotation_value = data.get('annotation_value')
    index_q = data.get('current_req_q')
    selected_question = image_request[index_q]
    annotation_type = selected_question['annotation_type']

    # QA check and approval
    annotation_validation_check = True # TODO: QA Team

    if annotation_validation_check:
        await message.answer(
            f"(Simulation) Good job! Your uploaded {annotation_type} has been successfully received and approved ✅" \
            f"Now, let's continue with the next task..."
        )
         # Video image assessment
        await asyncio.sleep(3)
        
        # Video assessment instructions
        video_instructions_text = (
            "Great!\n"
            "Let's move to Video Annotation task!\n\n"
            "📋 Instructions:\n"
            "• You'll receive a video.\n"
            "• You will be asked to give a well detailed description of the image\n\n"
            "Ready to begin the video test?"
        )
        
        video_ready_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🖼️ Start Video Test", callback_data="start_video_test")]
            ]
        )
        
        await message.answer(video_instructions_text, reply_markup=video_ready_kb)
        await state.set_state(TestKnowledge.video_instructions)
        

        print(f"✅ TRANSLATION PASSED - User {message.from_user.id}")
        print(f"Translation: {data.get('user_translation')}")
        
        
    else:
        failure_text = (
            "Assessment needs improvement\n\n"
            "Feedback: Your translation needs some work\n"
            "Next step: Please try the assessment again\n"
            "Tip: Review translation guidelines and try again"
        )
        
        await message.answer(failure_text)
        await state.clear()

# Video Assessment Handlers
@router.callback_query(TestKnowledge.video_instructions, F.data == "start_video_test")
async def handle_start_video_test(callback: CallbackQuery, state: FSMContext):
    """Start the video assessment"""
    await callback.answer()
    
    # Initialize video quiz data
    await state.update_data(current_q=0, num_q=2, target_language='Yoruba')
    await state.set_state(TestKnowledge.video_quiz)
    
    # Send first video question
    await send_video_question(callback.message, state)

async def send_video_question(message: Message, state: FSMContext):
    """Send a video quiz question"""
    data = await state.get_data()
    q_index = data["current_q"]
    target_lang = data['target_language']
    
    if not video_quiz_data:
        await message.answer("❌ No quiz data available")
        return
    
    if q_index >= len(video_quiz_data):
        await message.answer("❌ Question index out of range")
        return
    
    selected_question = video_quiz_data[q_index]
    print(f"📝 Selected question: {selected_question}")
    
    try:
        # Use FSInputFile for local video files
       # video_file = FSInputFile(selected_question['video'])
        await message.answer_video(
            #video=video_file,
            video=selected_question['video_id'],
            caption=f"❓{hbold(selected_question['question'])}\n\n Make sure to describe in {target_lang}."
        )
        print("✅ Video sent successfully")
        await state.set_state(TestKnowledge.video_quiz_submission)
    except Exception as e:
        print(f"❌ Error sending video: {e}")
        await message.answer(f"❌ Error loading video: {e}")
        # Try without video for debugging
        await message.answer(
            f"❓{hbold(selected_question['question'])}\n\n Make sure to describe in {target_lang}.",
        )
        await state.set_state(TestKnowledge.video_quiz_submission)

@router.message(TestKnowledge.video_quiz_submission)
async def handle_video_submission(message: Message, state: FSMContext):
    """Handle video quiz submission with 10 word minimum check"""

    if not message.text:
        message.answer("❌ Please send your descriptions as text.")
        return

    user_annotation = message.text.strip()

    # Word count validation
    if len(user_annotation.split()) < 10:
        await message.answer(
            "❌ Your description is too short.\n"
            "Please provide at least 10 words for your annotation."
        )
        return

    data = await state.get_data()
    target_lang = data.get("target_language")

    await state.update_data(user_annotation=user_annotation)

    confirmation_message = (
        "✅ Description Received!\n\n"  
        f"Your {target_lang} Description:\n"  
        f'"{user_annotation}"\n\n'
        f"⏳ Status: Submitted for validation\n"
        f"🔔 Next: You'll be notified when reviewed\n\n"
    )

    await message.answer(confirmation_message)

    await simulate_video_validation(message, state)
    
@router.message(TestKnowledge.video_quiz_feedback)
async def simulate_video_validation(message: Message, state: FSMContext):
    
    await asyncio.sleep(3)

    data = await state.get_data()
    q_index = data['current_q']
    num_q = data.get('num_q', 0)
    target_lang = data.get('target_language')
    user_annotation = data.get('user_annotation')
    sent_video = video_tasks[q_index]['video_id']

    
    validation_result = True  # TODO: QA validation
    
   
    if validation_result:


        await message.answer(
            "(simulation) Good job! You have successfully completed the task ✅ " \
            "Your task has been approved!\n" 
            "Now, let's continue with the next task...")
            
        num_q -= 1
            
        if num_q > 0:
            await state.update_data(num_q=num_q, current_q=1)
            await send_video_question(message, state)
        else:
            # Video assessment completed!
            await message.answer("🎉 Video annotation test completed!")
            
            # Start Video request and annotation
            await asyncio.sleep(3)

            # test instructions
            video_request_instructions = (
                "Nice job so far!\n"
                "Let's move on to next task (video Annotation)!\n\n"
                "📋 Instructions:\n"
                "You'll receive a theme and need to send a video that matches it.\n"
                "You’ll also be asked to provide a short description of the video you send using a minimum of 10 words.\n\n"
                "Ready to begin the test?"
            )
                
            video_2_ready_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                        [InlineKeyboardButton(text="🖼️ Start Video Test", callback_data="start_video_2_test")]
                ]
            )

            await message.answer(video_request_instructions, reply_markup=video_2_ready_kb)
            await state.set_state(TestKnowledge.video_2_instructions)

    else:
        failure_text = (
            "Feedback: Your descriptions needs some work\n"
            "Next step: Please try the assessment again\n"
            "Assessment need improvement\n\n"
            "Tip: Review description guidelines and try again.\n\n"
        )
        await message.answer("❌ Incorrect.")
        await message.answer(failure_text)
        await message.answer("Let's try again one more time.")

        await send_video_question(message, state)



# Video 2 Assessment Handlers
@router.callback_query(TestKnowledge.video_2_instructions, F.data == 'start_video_2_test')
async def handle_start_video_2_test(callback: CallbackQuery, state: FSMContext):
    """Start the video request assessment"""
    await callback.answer()

    # Initialize video quiz data
    await state.update_data(
        current_req_q = 0,
        num_req_q = 2
    )
    await state.set_state(TestKnowledge.video_2_quiz)

    await send_video_2_question(callback.message, state)


@router.message(TestKnowledge.video_2_quiz)
async def send_video_2_question(message: Message, state: FSMContext):
    data = await state.get_data()
    q_index = data.get('current_req_q', 0)
    num_req_q = data.get('num_req_q')
    target_lang = data.get('target_language')

    if not video_2_quiz_data:
        await message.answer("❌ No quiz data available")
        return
    
    if q_index >= len(video_2_quiz_data):
        await message.answer("❌ Question index out of range")
        return
    
    selected_question = video_2_quiz_data[q_index]
    await state.update_data(selected_question=selected_question)
    print(f"📝 Selected question: {selected_question}")

    await message.answer(
        f"Awesome! Here's your theme  — share a video and describe it in {target_lang}:\n\n"
        f"---\n"
        f"Theme: {selected_question['theme']}\n"
        f"--\n\n"
        f"Describe it using: {selected_question['annotation_type']}\n"
        f"Guide: {selected_question['instruction']}\n"
        f"Example: {selected_question['example_prompt']}\n\n"
        f"Your {target_lang} description:\n"
    )

    # await receive_video_submission(message, state)
    await state.set_state(TestKnowledge.video_2_quiz_submission)

@router.message((F.content_type == ContentType.VIDEO) | (F.content_type == ContentType.DOCUMENT), StateFilter(TestKnowledge.video_2_quiz_submission))
async def receive_video_submission(message: Message, state: FSMContext):
    """Handle Submission"""
    if not message.video:
        await message.answer(" ❌ Please send a video.")
        return
    
    video = message.video
    file_id = video.file_id

    await state.update_data(video_id=file_id)
    await message.answer(
        f"✅ Video received!\n\n"
        f"⏳ Status: Submitted for validation\n"
        f"🔔 Next: You'll be notified when reviewed\n\n"
    )

    await simulate_request_video_validation(message, state)


async def simulate_request_video_validation(message: Message, state: FSMContext):
    """Simulation of the sent video validation"""
    await asyncio.sleep(3)

    data = await state.get_data()
    video_id = data.get('video_id')
    index_q = data.get('current_req_q')
    selected_question = video_2_tasks[index_q]

    # QA check and approval
    video_validation_check = True # TODO: QA Team

    if video_validation_check:
        await message.answer(
            f"(Simulation) Good job! Your uploaded video has been successfully received and approved ✅\n" \
            "Now, let's continue with describing the uploaded video..."
        )

        await state.set_state(TestKnowledge.video_annotation)
        await video_annotation(message, state)
    
    else:
        failure_text = (
            "Video Quality Check Failed\n\n"
            "Feedback: The uploaded video does not meet our quality standards\n"
            "Next step: Please upload a clearer, relevant video\n"
            "Tip: Ensure the video is filmed in a well-lit environment, in focus, and matches the given theme"
            )
        await message.answer(failure_text)

@router.message(TestKnowledge.video_annotation)
async def video_annotation(message: Message, state: FSMContext):
    """start Video Annotation (Audio / Text)"""

    data = await state.get_data()
    video_id = data.get('video_id')
    index_q = data.get('current_req_q')
   # selected_question = video_2_tasks[index_q]
    selected_question = data.get('selected_question')
    target_lang = data.get("target_language")

    await message.answer_video(
        video=video_id,
        caption=(
            f"✅ Your video for **{selected_question['theme']}** has been received and approved!\n\n"
            f"Now, please describe this video in **{target_lang}** using {hbold(selected_question['annotation_type'])}.\n"
            "Focus on what is happening, the people, objects, and actions you see.\n"
            "✔ Be detailed and accurate.\n"
            "✔ Use complete sentences.\n"
            "❌ Avoid unrelated details."
        )
    )
    
    await state.set_state(TestKnowledge.video_annotation_submission)

@router.message(TestKnowledge.video_annotation_submission, F.text | F.voice | F.audio)
async def handle_annotation(message: Message, state: FSMContext):
    data = await state.get_data()
    index_q = data.get('current_req_q')
    #selected_question = video_2_tasks[index_q]
    selected_question = data.get('selected_question')
    target_lang = data.get("target_language")
    annotation_type = selected_question['annotation_type']
    
    # Validate that user sent the right type
    if annotation_type == "text" and message.text:
        annotation_value = message.text.strip()
         # Word count validation
        if len(annotation_value.split()) < 10:
            await message.answer(
                "❌ Your description is too short.\n"
                "Please provide at least 10 words for your annotation."
            )
            return
    elif annotation_type == "audio" and (message.audio or message.voice):
        annotation_value = message.audio.file_id if message.audio else message.voice.file_id
    else:
        await message.answer(f"❌ Please send a valid {annotation_type} description.")
        return
    
    
    # Save annotation to state
    await state.update_data(annotation_value=annotation_value)
    
    await message.answer(
        f"✅ {annotation_type.capitalize()} description received!\n\n"
        f"⏳ Status: Submitted for validation\n"
        f"🔔 Next: You'll be notified when reviewed\n\n"
    )
    
    await simulate_video_annotation_validation(message, state)


async def simulate_video_annotation_validation(message: Message, state: FSMContext):
    """Simulation of the sent annotation validation"""
    await asyncio.sleep(3)

    data = await state.get_data()
    annotation_value = data.get('annotation_value')
    index_q = data.get('current_req_q')
    #selected_question = video_2_tasks[index_q]
    selected_question = data.get('selected_question')
    annotation_type = selected_question['annotation_type']

    # QA check and approval
    annotation_validation_check = True # TODO: QA Team

    if annotation_validation_check:
        await message.answer(
            f"(Simulation) Good job! Your uploaded {annotation_type} has been successfully received and approved ✅" \
            f"Now, let's continue with the next task..."
        )
        success_text = (
                    "🎉 (simulation) Congratulations! Test Passed!\n"  
                    "You're now eligible for real tasks!\n\n" \
                    "Ready to start earning?"
                )
        

            
        await message.answer(success_text)

        # Clear state
        await state.clear()
                
        # Show final completion buttons
        start_tasks_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Start Real Tasks", callback_data="start_real_tasks")],
                [InlineKeyboardButton(text="View Commands", callback_data="view_commands")]
            ]
        )
                
        await message.answer(
            "🎉 All assessments completed!\n\nClick below to access the task portal:",
            reply_markup=start_tasks_kb
        )
    
    else:
        failure_text = (
            f"{annotation_type} Quality Check Failed\n\n"
            f"Feedback: The uploaded {annotation_type}  does not meet our quality standards\n"
            f"Next step: Please send a clearer, relevant {annotation_type}\n"
            f"Tip: Ensure the {annotation_type} is well detailed, focuses, and matches the given theme"
            )
        await message.answer(failure_text)



@router.callback_query(F.data == "start_real_tasks")
async def handle_start_real_tasks(callback: CallbackQuery, state: FSMContext):
    """Redirection vers les tâches réelles"""
    await callback.answer()
    
    # Import local pour éviter circular imports
    from src.routes.task_routes.tasks import cmd_welcome
    
    redirect_text = (
        "🎉 Redirecting to Task Portal...\n\n"  
        "Time to start earning with real tasks!\n"
        "Use /welcome anytime to access the task portal."
    )
    
    await callback.message.answer(redirect_text)
    
    # Appeler directement la fonction welcome du module tasks
    await cmd_welcome(callback.message)  

@router.callback_query(F.data == "view_commands")
async def handle_view_commands(callback: CallbackQuery, state: FSMContext):
    """Afficher les commandes disponibles"""
    await callback.answer()
    
    commands_text = (
        "Menu :\n"
        "/welcome - Access task portal\n"
        "/status - Check your progress\n"
        "/leaderboard\n"
        "/payment\n"
        "/support\n" 
        "💡 Quick tip: Use /welcome to start your first real task!"
    )
    
    start_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Go to Tasks", callback_data="start_real_tasks")]
        ]
    )
    
    await callback.message.answer(commands_text, reply_markup=start_kb)

