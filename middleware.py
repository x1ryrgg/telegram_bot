import logging
from aiogram.exceptions import TelegramNetworkError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/info.log"),
    ]
)

logger = logging.getLogger(__name__)



async def log_middleware(handler, event, data):
    handler_name = getattr(handler, "__qualname__", handler.__name__)

    logger.info(f"Handler {handler_name} started for {type(event).__name__}")
    try:
        result = await handler(event, data)
        logger.info(f"Handler {handler_name} finished successfully")
        return result
    except TelegramNetworkError as e:
        raise
    except Exception as e:
        logger.error(
            f"Error in handler {handler_name}: {str(e)}",
            exc_info=True
        )
        raise