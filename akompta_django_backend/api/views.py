from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, permissions
from .models import User, Product, Sale, Expense, Savings, StockMovement, Report
from .serializers import (
    UserSerializer,
    ProductSerializer,
    SaleSerializer,
    ExpenseSerializer,
    SavingsSerializer,
    StockMovementSerializer,
    ReportSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class SavingsViewSet(viewsets.ModelViewSet):
    queryset = Savings.objects.all()
    serializer_class = SavingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)




from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from openai import OpenAI
import base64
import json

@api_view(["POST"])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)})
    return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def verify_token(request):
    return Response({"message": "Token is valid"}, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def process_voice_command(request):
    audio_base64 = request.data.get("audio_base64")
    if not audio_base64:
        return Response({"error": "No audio provided"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        audio_data = base64.b64decode(audio_base64)
        # Save to a temporary file for OpenAI Whisper
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_data)

        client = OpenAI()
        with open("temp_audio.wav", "rb") as audio_file:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        
        text_command = transcript.text

        # Use OpenAI GPT for intent recognition and entity extraction
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts intent and entities from user commands related to business management (sales, expenses, stock, savings). Respond in JSON format."},
                {"role": "user", "content": f"Analyze the following command: \"{text_command}\". Extract intent (e.g., record_sale, record_expense, record_stock_movement, record_savings, get_report, get_dashboard_summary) and relevant entities (product_name, quantity, amount, category, type, period, etc.)."}
            ]
        )
        
        try:
            ai_response = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            ai_response = {"intent": "unknown", "raw_text": text_command, "ai_response": response.choices[0].message.content}

        return Response({"transcript": text_command, "ai_response": ai_response}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_dashboard_summary(request):
    user = request.user
    # Implement logic to fetch dashboard summary data
    # This is a placeholder, replace with actual data aggregation
    total_sales = Sale.objects.filter(user=user).aggregate(models.Sum("total_amount"))["total_amount__sum"] or 0
    total_expenses = Expense.objects.filter(user=user).aggregate(models.Sum("amount"))["amount__sum"] or 0
    net_profit = total_sales - total_expenses
    total_savings = Savings.objects.filter(user=user, transaction_type="deposit").aggregate(models.Sum("amount"))["amount__sum"] or 0
    total_savings -= Savings.objects.filter(user=user, transaction_type="withdrawal").aggregate(models.Sum("amount"))["amount__sum"] or 0

    return Response({
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "total_savings": total_savings,
        "message": "Dashboard summary data (placeholder)"
    }, status=status.HTTP_200_OK)


