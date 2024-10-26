from account.entity.account import Account
from account.repository.account_repository_impl import AccountRepositoryImpl
from user_analysis.entity.user_analysis import UserAnalysis
from user_analysis.entity.user_analysis_fixed_boolean_selection import UserAnalysisFixedBooleanSelection
from user_analysis.entity.user_analysis_fixed_five_score_selection import UserAnalysisFixedFiveScoreSelection
from user_analysis.repository.user_analysis_answer_repository_impl import UserAnalysisAnswerRepositoryImpl
from user_analysis.repository.user_analysis_custom_selection_repository_impl import \
    UserAnalysisCustomSelectionRepositoryImpl
from user_analysis.repository.user_analysis_question_repository_impl import UserAnalysisQuestionRepositoryImpl
from user_analysis.repository.user_analysis_repository_impl import UserAnalysisRepositoryImpl
from user_analysis.repository.user_analysis_request_repository_impl import UserAnalysisRequestRepositoryImpl
from user_analysis.service.user_analysis_service import UserAnalysisService


class UserAnalysisServiceImpl(UserAnalysisService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__userAnalysisRepository = UserAnalysisRepositoryImpl.getInstance()
        cls.__instance.__userAnalysisQuestionRepository = UserAnalysisQuestionRepositoryImpl.getInstance()
        cls.__instance.__userAnalysisCustomSelectionRepository = UserAnalysisCustomSelectionRepositoryImpl.getInstance()
        cls.__instance.__userAnalysisAnswerRepository = UserAnalysisAnswerRepositoryImpl.getInstance()
        cls.__instance.__userAnalysisRequestRepository = UserAnalysisRequestRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def createUserAnalysis(self, title, description):
        try:
            return self.__userAnalysisRepository.create(title, description)

        except Exception as e:
            print('Error creating order:', e)
            raise e

    def createUserAnalysisQuestion(self, user_analysis_id, question_text, user_analysis_type):
        user_analysis = self.__userAnalysisRepository.findById(user_analysis_id)
        if user_analysis is None:
            raise ValueError("UserAnalysis not found")

        return self.__userAnalysisQuestionRepository.create(user_analysis, question_text, user_analysis_type)

    def createUserAnalysisCustomSelection(self, question_id, custom_text):
        try:
            question = self.__userAnalysisQuestionRepository.findById(question_id)
            if question is None:
                raise ValueError("Survey Question not found")

            return self.__userAnalysisCustomSelectionRepository.createUserAnalysisCustomSelection(question, custom_text)

        except ValueError as e:
            print(f"Error: {str(e)}")
            raise e

        except Exception as e:
            print(f"Unexpected error while creating selection: {str(e)}")
            raise e

    def saveAnswer(self, account_id, user_analysis_id, answers):
        try:
            user_analysis_request = self.__userAnalysisRequestRepository.create(account_id, user_analysis_id)
            questions = self.__userAnalysisQuestionRepository.findUserAnalysisQuestionListByUserAnalysisId(user_analysis_id)
            for question in questions:
                question_id = question.id
                answer_data = answers.get(str(question_id))

                if answer_data is not None:
                    self.__userAnalysisAnswerRepository.saveAnswer(user_analysis_request, question_id, answer_data)

        except Exception as e:
            print('답변 저장중 오류 발생: ', {e})

    def listAllRequest(self):
        return self.__userAnalysisRequestRepository.list()

    def listOwnRequest(self, account_id):
        account = Account.objects.get(id = account_id)
        return self.__userAnalysisRequestRepository.list(account)

    def listAnswer(self, filter, user_analysis_id=None, question_id=None, account_id=None):
        if filter == "user_analysis":
            listedAnswer = self.__userAnalysisAnswerRepository.summarizeAnswerByUserAnalysisId(user_analysis_id)
        elif filter == "account":
            listedAnswer = self.__userAnalysisAnswerRepository.summarizeAnswerByAccountId(account_id)
        elif filter == "question":
            listedAnswer = self.__userAnalysisAnswerRepository.summarizeAnswerByQuestionId(question_id)
        elif filter == "user_analysis and account":
            listedAnswer = self.__userAnalysisAnswerRepository.summarizeAnswerByUserAnalysisIdandAccountId(user_analysis_id, account_id)

        return listedAnswer

    def listQuestions(self, user_analysis_id):
        questions = self.__userAnalysisQuestionRepository.findUserAnalysisQuestionListByUserAnalysisId(user_analysis_id)
        return questions

    def listSelections(self, question_id):
        question = self.__userAnalysisQuestionRepository.findById(question_id)

        if question.user_analysis_type == 1:
            return None
        elif question.user_analysis_type == 2:
            selections = UserAnalysisFixedFiveScoreSelection.objects.all()
        elif question.user_analysis_type == 3:
            selections = UserAnalysisFixedBooleanSelection.objects.all()
        elif question.user_analysis_type == 4:
            selections = self.__userAnalysisCustomSelectionRepository.findUserAnalysisCustomSelectionListByQuestionId(question.id)

        return selections

    def listUserAnalysis(self):
        return self.__userAnalysisRepository.list()