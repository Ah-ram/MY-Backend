from rest_framework import viewsets, status
from rest_framework.response import Response

from redis_token.service.redis_service_impl import RedisServiceImpl
from user_analysis.repository.user_analysis_question_repository_impl import UserAnalysisQuestionRepositoryImpl
from user_analysis.serializers import UserAnalysisAnswerSerializer, UserAnalysisQuestionSerializer, \
    UserAnalysisFixedFiveScoreSelectionSerializer, UserAnalysisFixedBooleanSelectionSerializer, \
    UserAnalysisCustomSelectionSerializer, UserAnalysisSerializer, UserAnalysisRequestSerializer
from user_analysis.service.user_analysis_service_impl import UserAnalysisServiceImpl


class UserAnalysisView(viewsets.ViewSet):
    userAnalysisService = UserAnalysisServiceImpl.getInstance()
    userAnalysisQuestionRepository = UserAnalysisQuestionRepositoryImpl.getInstance()
    redisService = RedisServiceImpl.getInstance()

    def createUserAnalysis(self, request):
        data = request.data
        title = data.get('title')
        description = data.get('description')

        if not title:

            return Response({"error": "제목이 필요합니다"}, status=status.HTTP_400_BAD_REQUEST)

        isCreated = {"title": f"{self.userAnalysisService.createUserAnalysis(title, description)}"}

        return Response(isCreated, status=status.HTTP_200_OK)

    def createUserAnalysisQuestion(self, request):
        data = request.data
        user_analysis_id = data.get('user_analysis')
        question_text = data.get('question')
        user_analysis_type = data.get('user_analysis_type')

        if not user_analysis_id or not question_text:
            return Response({"error": "유저조사 ID와 질문 내용이 필요합니다"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            question = self.userAnalysisService.createUserAnalysisQuestion(user_analysis_id, question_text, user_analysis_type)
            return Response({"success": "질문이 추가되었습니다", "questionId": f"{question.id}"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def createUserAnalysisCustomSelection(self, request):
        try:
            data = request.data
            question_id = data.get('question_id')
            custom_text = data.get('custom_text')
            print(f"question_id: {question_id}, custom_text: {custom_text}")

            if not question_id or not custom_text:
                return Response({"error": "Question ID and selection text are required."},
                                status=status.HTTP_400_BAD_REQUEST)

            selection = self.userAnalysisService.createUserAnalysisCustomSelection(question_id, custom_text)

            return Response({"message": "Selection created successfully", "selection_id": selection.id},
                            status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "Something went wrong while creating the selection."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def submitUserAnalysisAnswer(self, request):
        try:
            userToken = request.data.get('userToken')
            print(f"userToken: {userToken}")

            if userToken:
                user_identifier = self.redisService.getValueByKey(userToken)
                print("user_identifier: ", user_identifier)

                if isinstance(user_identifier, int):
                    account_id = user_identifier  # 회원의 경우 account_id
                    guest_identifier = None
                elif isinstance(user_identifier, str):
                    account_id = None
                    guest_identifier = user_identifier  # 비회원의 경우 IP 주소 (identifier)
                else:
                    account_id = None
                    guest_identifier = None
            else:
                account_id = None
                guest_identifier = None

            user_analysis_id = request.data.get('user_analysis')
            print(f"user_analysis_id: ", user_analysis_id)
            answers = request.data.get('user_analysis_answer')
            print(f"answers: {answers}")

            user_analysis_request = self.userAnalysisService.saveAnswer(
                account_id=account_id,
                user_analysis_id=user_analysis_id,
                answers=answers,
                guest_identifier=guest_identifier
            )

            # 중복 요청인 경우 (user_analysis_request가 None 반환)
            if user_analysis_request is None:
                return Response(
                    {"error": "비회원의 경우 최초 1회만 요청이 가능합니다."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 새로 생성된 요청이 있는 경우
            print("user_analysis_request: ", user_analysis_request.id)

            serializer = UserAnalysisRequestSerializer(user_analysis_request, many=False)
            print("serializer: ", serializer)

            return Response(serializer.data, status.HTTP_200_OK)

        except Exception as e:
            return Response(False, status.HTTP_400_BAD_REQUEST)

    def listAllUserAnalysisRequest(self, request):
        try:
            listedRequest = self.userAnalysisService.listAllRequest()
            serializer = UserAnalysisRequestSerializer(listedRequest, many=True)
            return Response(serializer.data, status.HTTP_200_OK)

        except Exception as e:
            return Response(False, status.HTTP_400_BAD_REQUEST)

    def listOwnUserAnalysisRequest(self, request):
        try:
            userToken = request.query_params.get('userToken')
            print(f"userToken: {userToken}")
            if userToken:
                account_id = self.redisService.getValueByKey(userToken)
            else:
                account_id = None

            listedRequest = self.userAnalysisService.listOwnRequest(account_id)
            serializer = UserAnalysisRequestSerializer(listedRequest, many=True)
            return Response(serializer.data, status.HTTP_200_OK)

        except Exception as e:
            return Response(False, status.HTTP_400_BAD_REQUEST)

    def readUserAnalysisRequest(self, request, pk=None):
        try:
            listedAnswer = self.userAnalysisService.readRequest(pk)
            print("listedAnswer: ", listedAnswer)
            serializer = UserAnalysisAnswerSerializer(listedAnswer, many=True)
            print("serializer: ", serializer)
            return Response(serializer.data, status.HTTP_200_OK)

        except Exception as e:
            return Response(False, status.HTTP_400_BAD_REQUEST)


    def listUserAnalysisAnswer(self, request):
        try:
            user_analysis_id = request.data.get('user_analysis_id')
            print("user_analysis_id: ", user_analysis_id)
            listedAnswer = self.userAnalysisService.listAnswer(user_analysis_id)
            print(listedAnswer)
            serializer = UserAnalysisAnswerSerializer(listedAnswer, many=True)

            return Response(serializer.data, status.HTTP_200_OK)

        except Exception as e:
            return Response(False, status.HTTP_400_BAD_REQUEST)

    def listUserAnalysisQuestion(self, request):
        try:
            userAnalysisId = request.data.get('user_analysis_Id')

            print(f"userAnalysisId: {userAnalysisId}")

            listedQuestions = self.userAnalysisService.listQuestions(userAnalysisId)

            serializer = UserAnalysisQuestionSerializer(listedQuestions, many=True)

            return Response(serializer.data, status.HTTP_200_OK)

        except Exception as e:
            return Response(False, status.HTTP_400_BAD_REQUEST)

    def listUserAnalysisSelection(self, request):
        try:
            questionId = request.data.get('question_Id')
            print(f"questionId: {questionId}")

            listedSelections = self.userAnalysisService.listSelections(questionId)
            print(f"listedSelections: {listedSelections}")

            question = self.userAnalysisQuestionRepository.findById(questionId)
            print(question.user_analysis_type)
            if question.user_analysis_type == 1:
                return Response({"message": "This is a descriptive question, no choices available."},
                                status=status.HTTP_200_OK)

            if question.user_analysis_type == 2:
                serializer = UserAnalysisFixedFiveScoreSelectionSerializer(listedSelections, many=True)
            elif question.user_analysis_type == 3:
                serializer = UserAnalysisFixedBooleanSelectionSerializer(listedSelections, many=True)
            elif question.user_analysis_type == 4:
                serializer = UserAnalysisCustomSelectionSerializer(listedSelections, many=True)
            else:
                return Response({"error": "Invalid survey type"}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status.HTTP_200_OK)

        except Exception as e:
            return Response(False, status.HTTP_400_BAD_REQUEST)

    def listUserAnalysis(self, request):
        userAnalysisList = self.userAnalysisService.listUserAnalysis()
        serializer = UserAnalysisSerializer(userAnalysisList, many=True)
        return Response(serializer.data)

    def getAnswerData(self, request):
        request_id = request.data.get('request_id')
        answerdata = self.userAnalysisService.getAnswer(request_id)
        print(answerdata)
        return Response(answerdata)