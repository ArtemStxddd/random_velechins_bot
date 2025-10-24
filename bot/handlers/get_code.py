from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

router = Router()

@router.message(F.text.lower() == "/code")
async def cmd_start(message: Message, state: FSMContext):
    code_text = """
    def k_fold_sum_distribution(values, probs, k):
        values = np.asarray(values, dtype=float)
        probs = np.asarray(probs, dtype=float)

        pmf = {v: p for v, p in zip(values, probs)}
        for _ in range(k):
            new_pmf = defaultdict(float)
            for a, pa in pmf.items():
                for b, pb in zip(values, probs):
                    new_pmf[a + b] += pa * pb
            pmf = new_pmf

        sums = np.array(sorted(pmf.keys()))
        probabilities = np.array([pmf[s] for s in sums])
        return sums, probabilities
    """
    
    await message.answer(f"```python\n{code_text}\n```", parse_mode=ParseMode.MARKDOWN_V2)