from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.keyboards.dynamic import create_data_type_keyboard_with_done
from src.keyboards.reply import  writing_ability_kb, phone_quality_kb, task_type_kb
from src.states.onboarding import Onboarding




class TaskTypeService():
    @staticmethod
    async def handle_data_type_selection_done(message: Message, state: FSMContext):
        
        user_data = await state.get_data()
        selected_data_types = user_data.get("selected_data_types", [])
        
        await state.update_data(task_type=", ".join(selected_data_types))
        await message.answer("✅ Data type selection confirmed!")
        
        if "📝Text" in selected_data_types:
            await message.answer("✍️ Can you write in your language?", reply_markup=writing_ability_kb)
            await state.set_state(Onboarding.text_writing_ability)
        elif "🎤Audio" in selected_data_types:
            await message.answer("📱 How good is your phone's mouthpiece and speaker?", reply_markup=phone_quality_kb)
            await state.set_state(Onboarding.phone_quality)

    
    @staticmethod

    async def handle_data_type_selection(message: Message, state: FSMContext):
        user_data = await state.get_data()
        selected_data_types = user_data.get("selected_data_types", [])

        if message.text in selected_data_types:
            selected_data_types.remove(message.text)
            await message.answer(f"❌ Removed: {message.text}")
        else:
            selected_data_types.append(message.text)
            await message.answer(f"✅ Added: {message.text}")
    
        await state.update_data(selected_data_types=selected_data_types)
    
        num_selected = len(selected_data_types)
        if num_selected == 0:
            await message.answer("📌 What kind of data do you want to give?\nSelect one or both.", reply_markup=task_type_kb)
        elif num_selected == 1:
            await message.answer("One data type selected.\nSelect another or press '✅ Done' to continue.", reply_markup=create_data_type_keyboard_with_done())
        elif num_selected == 2:
            await state.update_data(task_type=", ".join(selected_data_types))
            await message.answer(f"✅ Both selected: {', '.join(selected_data_types)}!")
            await message.answer("✍️ Can you write in your language?", reply_markup=writing_ability_kb)
            await state.set_state(Onboarding.text_writing_ability)

  