import logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

from resources.jobs import router as JobRouter
from resources.users import router as UserRouter
from resources.prompts import router as PromptRouter
from resources.assessment import router as AssessmentRouter