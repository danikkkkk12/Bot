import asyncio
import datetime
from random import uniform, randint

from aiogram import F, Router, types, Bot
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from config import VERIF_CHANNEL_ID
from database.db import DataBase
from keyboards.client import ClientKeyboard
from other.filters import ChatJoinFilter, RegisteredFilter
from other.languages import languages

router = Router()


class RegisterState(StatesGroup):
    input_id = State()


class GetSignalStates(StatesGroup):
    chosing_mines = State()


class ChangeReferral(StatesGroup):
    input_ref = State()


@router.message(CommandStart())
async def start_command(message: types.Message, user_id: int = 0):
    await message.delete()
    user = await DataBase.get_user_info(message.from_user.id if user_id == 0 else user_id)
    if user is None:
        await get_language(message, True)
        return

    await message.answer(languages[user[2]]["welcome"].format(first_name=message.from_user.first_name),
                         reply_markup=await ClientKeyboard.start_keyboard(user[2]), parse_mode="HTML")


@router.callback_query(F.data.startswith("sel_lang"))
async def select_language(callback: CallbackQuery):
    data = callback.data.split("|")
    await DataBase.register(callback.from_user.id, data[2])
    await start_command(message=callback.message, user_id=int(data[1]))


@router.callback_query(F.data.startswith("resel_lang"))
async def select_language(callback: CallbackQuery):
    data = callback.data.split("|")
    await DataBase.update_lang(int(data[1]), data[2])
    await start_command(message=callback.message, user_id=int(data[1]))


@router.callback_query(F.data == "get_lang")
async def get_language(query: Message | CallbackQuery, first: bool = False):
    q = query
    if isinstance(query, CallbackQuery):
        query = query.message
    try:
        await query.delete()
    except:
        pass

    if first:
        prefix = f"sel_lang|{query.from_user.id}"
    else:
        prefix = f"resel_lang|{q.from_user.id}"
    await query.answer("Select language",
                       reply_markup=await ClientKeyboard.languages_board(prefix))


@router.callback_query(F.data.in_(["back", "check"]), ChatJoinFilter())
async def menu_output(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass

    user_info = await DataBase.get_user_info(callback.from_user.id)
    lang = await DataBase.get_lang(callback.from_user.id)

    text = languages[lang]["register_info"]

    if lang == "ru":
        photo = types.FSInputFile("hello.jpg")
    else:
        photo = types.FSInputFile("hel.jpg")  


    await callback.message.answer_photo(photo, caption=languages[lang]["welcome_message"],
                                        parse_mode="HTML",
                                        reply_markup=await ClientKeyboard.menu_keyboard(user_info, lang))

    await callback.answer()





@router.callback_query(F.data == "register")
async def register_handler(callback: types.CallbackQuery, state: FSMContext):
    lang = await DataBase.get_lang(callback.from_user.id)
    text = languages[lang]["register_info"]


    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer(text, parse_mode="HTML",
                                  reply_markup=await ClientKeyboard.register_keyboard(callback, lang))
    await state.set_state(RegisterState.input_id)



@router.callback_query(F.data == "instruction")
async def instruction_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    new_ref_url = f"{(await DataBase.get_ref())}&sub1={user_id}"
    lang = await DataBase.get_lang(callback.from_user.id)
    text = languages[lang]["instruction_info"].format(ref_url=new_ref_url)

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(text, reply_markup=await ClientKeyboard.back_keyboard(lang),
                                  parse_mode="HTML")



@router.message(F.chat.func(lambda chat: chat.id == int(VERIF_CHANNEL_ID)))
async def channel_verification_handler(message: types.Message):
    if (await DataBase.get_user(message.text)) is None:
        lang = await DataBase.get_lang(int(message.text))
        await DataBase.update_verifed(message.text)
        await message.bot.send_message(chat_id=int(message.text),
                                       text=languages[lang]["success_registration"],
                                       reply_markup=await ClientKeyboard.get_signal_keyboard(lang), parse_mode="HTML")


@router.callback_query(F.data == "change_ref")
async def change_referral_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    lang = await DataBase.get_lang(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(languages[lang]["enter_new_ref"])
    await state.set_state(ChangeReferral.input_ref)


@router.message(ChangeReferral.input_ref)
async def change_referral_message_state(message: types.Message, state: FSMContext):
    lang = await DataBase.get_lang(message.from_user.id)
    await message.answer(languages[lang]["ref_changed"])
    await DataBase.edit_ref(message.text)
    await state.clear()
